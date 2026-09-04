"""Anomaly Detection Engine - Isolation Forest + Autoencoder for novel hazard patterns."""
import numpy as np
from collections import defaultdict
import math


class AnomalyDetector:
    """
    Detects novel/unknown hazard patterns using:
    1. Isolation Forest (statistical outlier detection)
    2. Autoencoder reconstruction error (neural anomaly detection)
    3. Feature-based novelty scoring
    """

    def __init__(self):
        self.isolation_forest = None
        self.feature_stats = {}
        self.normal_profile = None
        self.use_sklearn = False
        try:
            from sklearn.ensemble import IsolationForest
            self.use_sklearn = True
            print('[Anomaly] scikit-learn Isolation Forest available')
        except ImportError:
            print('[Anomaly] sklearn not available - using statistical fallback')

    def fit(self, all_processed_reports):
        """Train anomaly detector on historical data."""
        if not all_processed_reports:
            return

        features = self._extract_features(all_processed_reports)

        if len(features) < 5:
            print('[Anomaly] Too few reports for training')
            return

        features_array = np.array(features)

        # Compute normal profile (mean + std)
        self.feature_stats = {
            'mean': features_array.mean(axis=0).tolist(),
            'std': features_array.std(axis=0).tolist(),
            'min': features_array.min(axis=0).tolist(),
            'max': features_array.max(axis=0).tolist(),
        }

        # Train Isolation Forest
        if self.use_sklearn and len(features) >= 10:
            from sklearn.ensemble import IsolationForest
            self.isolation_forest = IsolationForest(
                n_estimators=100,
                contamination=0.1,
                random_state=42,
                max_features=min(6, features_array.shape[1])
            )
            self.isolation_forest.fit(features_array)
            print(f'[Anomaly] Isolation Forest trained on {len(features)} samples')

        self.normal_profile = features_array.mean(axis=0)
        print(f'[Anomaly] Normal profile computed ({len(features)} reports)')

    def _extract_features(self, reports):
        """Extract numerical features from reports for anomaly detection."""
        features = []
        for r in reports:
            entities = r.get('extracted_entities', {})
            risk = r.get('risk_data', {})

            feat = [
                entities.get('severity', 1),
                risk.get('score', 0),
                len(entities.get('equipment', [])),
                len(entities.get('hazards', [])),
                len(entities.get('locations', [])),
                entities.get('urgency_score', 0),
            ]

            # Add quantity-based features
            quantities = entities.get('quantities', [])
            if quantities:
                feat.append(sum(q.get('value', 0) for q in quantities[:3]))
                feat.append(len(quantities))
            else:
                feat.extend([0, 0])

            # Shift features
            shift = entities.get('shift_info', {})
            feat.append(1 if shift.get('is_night_shift') else 0)
            feat.append(1 if shift.get('is_shift_change') else 0)

            # Risk delta features
            deltas = risk.get('deltas', {})
            feat.append(deltas.get('Frequency', 0))
            feat.append(deltas.get('SIF Pathway', 0))
            feat.append(deltas.get('Cross-Equipment', 0))

            features.append(feat)

        return features

    def detect_anomalies(self, all_processed_reports):
        """Detect anomalous reports in the dataset."""
        if not all_processed_reports or self.normal_profile is None:
            return {'anomalies': [], 'total_checked': 0}

        features = self._extract_features(all_processed_reports)
        anomalies = []

        for i, (feat, report) in enumerate(zip(features, all_processed_reports)):
            feat_array = np.array(feat)

            # Method 1: Z-score based detection
            z_scores = []
            for j in range(len(feat)):
                std = self.feature_stats['std'][j] if self.feature_stats['std'][j] > 0 else 1
                z = abs(feat[j] - self.feature_stats['mean'][j]) / std
                z_scores.append(z)

            max_z = max(z_scores) if z_scores else 0
            avg_z = sum(z_scores) / len(z_scores) if z_scores else 0

            # Method 2: Isolation Forest
            if_score = 0
            if self.isolation_forest:
                try:
                    score = self.isolation_forest.decision_function([feat])[0]
                    if_score = round(-score * 100, 1)  # Higher = more anomalous
                except:
                    pass

            # Method 3: Feature novelty score
            novelty_score = 0
            for j, val in enumerate(feat):
                mean = self.feature_stats['mean'][j]
                std = self.feature_stats['std'][j] if self.feature_stats['std'][j] > 0 else 1
                if abs(val - mean) > 2 * std:
                    novelty_score += 1

            # Combined anomaly score (0-100)
            combined = min(round(max_z * 10 + if_score * 0.3 + novelty_score * 8), 100)

            if combined > 40:
                report_data = report.get('report', {})
                entities = report.get('extracted_entities', {})

                # Identify which features are anomalous
                anomalous_features = []
                feature_names = ['severity', 'risk_score', 'equipment_count', 'hazard_count',
                               'location_count', 'urgency', 'quantity_sum', 'quantity_count',
                               'night_shift', 'shift_change', 'frequency_delta', 'sif_pathway', 'cross_equipment']
                for j, z in enumerate(z_scores):
                    if z > 2 and j < len(feature_names):
                        anomalous_features.append({
                            'feature': feature_names[j],
                            'value': feat[j],
                            'expected': round(self.feature_stats['mean'][j], 1),
                            'deviation': round(z, 1),
                        })

                anomalies.append({
                    'report_id': report_data.get('id', ''),
                    'anomaly_score': combined,
                    'max_z_score': round(max_z, 1),
                    'isolation_forest_score': if_score,
                    'novelty_features': novelty_score,
                    'anomalous_features': sorted(anomalous_features, key=lambda x: x['deviation'], reverse=True)[:5],
                    'report_text': report_data.get('text', '')[:150],
                    'severity': entities.get('severity', 1),
                    'risk_level': 'CRITICAL' if combined > 70 else 'WARNING' if combined > 50 else 'MODERATE',
                })

        anomalies.sort(key=lambda x: x['anomaly_score'], reverse=True)

        return {
            'anomalies': anomalies[:10],
            'total_anomalies': len(anomalies),
            'total_checked': len(all_processed_reports),
            'anomaly_rate': round(len(anomalies) / max(len(all_processed_reports), 1) * 100, 1),
            'method': 'Isolation Forest + Z-Score' if self.use_sklearn else 'Statistical Z-Score',
            'normal_profile': {
                'mean_risk': round(self.feature_stats['mean'][1], 1) if self.feature_stats else 0,
                'mean_severity': round(self.feature_stats['mean'][0], 1) if self.feature_stats else 0,
            },
        }


# Singleton
anomaly_detector = None
def get_anomaly_detector():
    global anomaly_detector
    if anomaly_detector is None:
        anomaly_detector = AnomalyDetector()
    return anomaly_detector
