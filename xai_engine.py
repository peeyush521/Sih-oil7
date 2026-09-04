"""XAI Engine — Explainable AI for Risk Scores and Classifications (Upgraded)."""
import numpy as np
from collections import defaultdict


class XAIEngine:
    """Provides explainable AI for risk scoring and classification decisions."""

    FEATURE_NAMES = [
        'severity', 'risk_score', 'equipment_count', 'hazard_count',
        'location_count', 'urgency', 'quantity_sum', 'quantity_count',
        'night_shift', 'shift_change', 'frequency_delta', 'sif_pathway', 'cross_equipment'
    ]

    def __init__(self):
        self.use_shap = False
        try:
            import shap
            self.use_shap = True
        except ImportError:
            pass

    def explain_classification(self, text, classification_result, nlp_engine, classifier):
        """Explain why a report was classified the way it was."""
        per_class = classification_result.get('per_class', {})
        word_contributions = self._analyze_word_contributions(text, classifier)
        novelty_reasons = []
        if classification_result.get('is_novel'):
            novelty_reasons = self._explain_novelty_reasons(text, classification_result, per_class)

        return {
            'predicted_class': classification_result.get('class', 'Unknown'),
            'confidence': classification_result.get('confidence', 0),
            'per_class_breakdown': per_class,
            'top_contributing_words': word_contributions[:12],
            'feature_importance_chart': self._build_importance_chart(word_contributions[:8]),
            'explanation_text': self._generate_classification_explanation(classification_result, word_contributions),
            'decision_boundary': self._explain_decision_boundary(classification_result, word_contributions),
            'novelty_analysis': novelty_reasons if novelty_reasons else None,
        }

    def explain_risk_score(self, risk_data, entities, related_reports):
        """Provide a deep explainability report for the risk score."""
        deltas = risk_data.get('deltas', {})
        evidence = risk_data.get('evidence', [])
        total = risk_data.get('score', 0)
        trajectory = risk_data.get('trajectory', 'STABLE')
        sif_cat = risk_data.get('sif_category', 'None')

        contributions = []
        for factor, points in deltas.items():
            pct = round(points / max(total, 1) * 100, 1)
            contributions.append({
                'feature': factor,
                'contribution': points,
                'contribution_pct': pct,
                'direction': 'positive' if points > 0 else 'negative',
                'impact': 'HIGH' if points >= 10 else 'MEDIUM' if points >= 5 else 'LOW',
                'explanation': self._explain_factor(factor, points, entities),
            })
        contributions.sort(key=lambda x: abs(x['contribution']), reverse=True)

        waterfall = self._build_waterfall(contributions, total)

        # Build narrative explanation
        narrative = self._build_narrative(contributions, total, trajectory, sif_cat, entities)

        # Build the "why now" explanation
        why_now = self._explain_why_now(contributions, risk_data, entities)

        return {
            'total_score': total,
            'trajectory': trajectory,
            'risk_level': risk_data.get('risk_level', 'NORMAL'),
            'contributions': contributions,
            'waterfall': waterfall,
            'top_factors': contributions[:3],
            'narrative': narrative,
            'why_now': why_now,
            'explanation_text': '. '.join(
                f["explanation"] for f in contributions[:4] if f["contribution"] > 0
            ) + '.' if contributions else 'No significant risk factors detected.',
            'evidence_log': evidence,
            'confidence_assessment': self._assess_explanation_confidence(contributions, total),
        }

    def explain_novel_hazard(self, text, classification_result, entities):
        """Explain why a hazard was flagged as novel/unrecognized."""
        conf = classification_result.get('confidence', 0)
        per_class = classification_result.get('per_class', {})

        reasons = []
        if conf < 35:
            reasons.append(f'Model confidence is only {conf}% — below 35% novelty threshold')
        if classification_result.get('is_novel'):
            reasons.append('No dominant class detected — the hazard pattern is unfamiliar to the model')

        # Explain what makes it different
        top_classes = list(per_class.items())[:3]
        diff = []
        for cls, prob in top_classes:
            diff.append({
                'closest_class': cls,
                'probability': prob,
                'gap': round(100 - prob, 1),
                'explanation': f'"{cls}" matched at {prob}% but insufficient for confident classification'
            })

        # Safety recommendation
        recommendation = self._novel_hazard_recommendation(text, entities)

        return {
            'is_novel': classification_result.get('is_novel', False),
            'confidence': conf,
            'reasons': reasons,
            'closest_classes': diff,
            'recommendation': recommendation,
            'explanation_text': (
                f'Novel hazard detected. Model confidence: {conf}% (below threshold). '
                f'Closest match: {top_classes[0][0] if top_classes else "N/A"} at {top_classes[0][1] if top_classes else 0}%. '
                'This report should be reviewed by a safety officer and added to training data if valid.'
            ),
            'action_required': 'MANDATORY: Safety officer review required for novel hazard classification',
        }

    def _explain_factor(self, factor, points, entities):
        """Generate human-readable explanation for a risk factor."""
        explanations = {
            'Frequency': f'Related incidents occurred {points}+ times — recurring pattern increases SIF risk',
            'Recency': f'Recent incident within {points} days — temporal proximity elevates risk',
            'Severity Trend': f'Severity is trending upward (+{points}) — escalating potential',
            'Semantic Similarity': f'{points}% similar to previous high-risk reports — pattern match detected',
            'Unresolved Actions': f'{points} open corrective actions — unresolved hazards compound risk',
            'Equipment Recurrence': f'Same equipment involved in {points} incidents — systematic equipment failure pattern',
            'Location Recurrence': f'{points} incidents at this location — site-specific hazard concentration',
            'Cross-Equipment': f'{points} related equipment involved — cascade failure risk detected',
            'Night Shift': f'+{points} risk from night shift operations — reduced visibility and fatigue',
            'Shift Change': f'+{points} risk during shift transition — communication gaps',
            'Quantity Detected': f'Hazardous quantity ({points}) exceeds safe threshold — escalation risk',
        }
        return explanations.get(factor, f'{factor} contributed +{points} points to overall risk score')

    def _build_narrative(self, contributions, total, trajectory, sif_cat, entities):
        """Build a natural language narrative of the risk analysis."""
        parts = []
        
        if total >= 70:
            parts.append(f"CRITICAL RISK ALERT: The overall risk score is {total}/100, placing this report in the CRITICAL zone.")
        elif total >= 40:
            parts.append(f"WARNING: Risk score is {total}/100, indicating elevated concern requiring attention.")
        else:
            parts.append(f"Risk score is {total}/100 — within manageable levels but monitoring recommended.")
        
        if trajectory == 'ESCALATING':
            parts.append("The trajectory is ESCALATING, meaning the risk is increasing over time. This is the most dangerous pattern.")
        elif trajectory == 'DECREASING':
            parts.append("The trajectory is DECREASING, suggesting recent interventions may be having a positive effect.")
        else:
            parts.append("The trajectory is STABLE — risk is neither increasing nor decreasing.")
        
        top_contribs = [c for c in contributions if c['contribution'] > 0][:3]
        if top_contribs:
            factor_names = [f"{c['feature']} (+{c['contribution']})" for c in top_contribs]
            parts.append(f"The primary risk drivers are: {', '.join(factor_names)}.")
        
        if sif_cat and sif_cat != 'None':
            parts.append(f"SIF pathway identified: {sif_cat}.")
        
        return ' '.join(parts)

    def _explain_why_now(self, contributions, risk_data, entities):
        """Explain why this report is flagged NOW (temporal reasoning)."""
        reasons = []
        for c in contributions:
            if c['contribution'] >= 5:
                reasons.append({
                    'factor': c['feature'],
                    'impact': c['contribution'],
                    'explanation': c['explanation'],
                })
        
        if not reasons:
            return {'text': 'No immediate temporal triggers detected.', 'urgency': 'LOW'}
        
        urgency = 'HIGH' if risk_data.get('score', 0) >= 70 else 'MEDIUM' if risk_data.get('score', 0) >= 40 else 'LOW'
        
        return {
            'text': f"{len(reasons)} factors triggered elevated risk: " + 
                    ', '.join(r['factor'] for r in reasons[:3]) + '.',
            'reasons': reasons,
            'urgency': urgency,
        }

    def _assess_explanation_confidence(self, contributions, total):
        """Assess how confident we are in the explanation itself."""
        if not contributions:
            return {'level': 'LOW', 'reason': 'No risk factors identified'}
        
        top_factor_pct = contributions[0]['contribution_pct'] if contributions else 0
        
        if top_factor_pct > 30 and total >= 50:
            return {'level': 'HIGH', 'reason': 'Clear primary factor dominates risk score'}
        elif len(contributions) >= 3:
            return {'level': 'MEDIUM', 'reason': 'Multiple factors contribute — no single dominant cause'}
        else:
            return {'level': 'LOW', 'reason': 'Limited factor data available'}

    def _explain_novelty_reasons(self, text, classification_result, per_class):
        """Explain why a report is novel."""
        reasons = []
        conf = classification_result.get('confidence', 0)
        if conf < 25:
            reasons.append('Extremely low confidence across all known categories')
        elif conf < 35:
            reasons.append('Low confidence — pattern not well represented in training data')
        
        top_vals = list(per_class.values())[:3]
        if len(top_vals) >= 2 and abs(top_vals[0] - top_vals[1]) < 5:
            reasons.append('Top two categories have nearly equal probability — ambiguous classification')
        
        return reasons

    def _novel_hazard_recommendation(self, text, entities):
        """Generate recommendation for novel hazards."""
        sev = entities.get('severity', 1)
        if sev >= 4:
            return 'URGENT: Add to training data immediately. Conduct DGMS-reportable incident review. Update risk register with new hazard category.'
        elif sev >= 3:
            return 'Add to training data within 48hrs. Conduct safety committee review. Consider adding new classification category.'
        else:
            return 'Review by safety officer. If valid, add to near-miss database and update training data.'

    def _analyze_word_contributions(self, text, classifier):
        """Analyze which words contribute most to classification."""
        words = text.lower().split()
        contributions = []
        try:
            base_probs = classifier.model.predict_proba([text])[0]
            base_idx = np.argmax(base_probs)
            base_conf = base_probs[base_idx]
        except Exception:
            return []

        for word in set(words):
            if len(word) < 3:
                continue
            modified = ' '.join(w for w in words if w != word)
            if not modified.strip():
                continue
            try:
                mod_probs = classifier.model.predict_proba([modified])[0]
                impact = base_conf - mod_probs[base_idx]
                if abs(impact) > 0.001:
                    contributions.append({
                        'word': word,
                        'impact': round(impact * 100, 2),
                        'direction': 'positive' if impact > 0 else 'negative',
                    })
            except Exception:
                pass
        contributions.sort(key=lambda x: abs(x['impact']), reverse=True)
        return contributions[:12]

    def _explain_decision_boundary(self, classification_result, word_contribs):
        """Explain where the decision boundary sits."""
        conf = classification_result.get('confidence', 0)
        if conf >= 70:
            return 'Strong classification — clear decision boundary. The model is confident in this prediction.'
        elif conf >= 35:
            return 'Moderate classification — decision boundary is visible but could shift with additional context.'
        else:
            return 'Weak classification — the report sits near a decision boundary. Novel hazard review recommended.'

    def _build_importance_chart(self, contributions):
        """Build a visual importance chart data."""
        if not contributions:
            return []
        mx = max(abs(c['impact']) for c in contributions) if contributions else 1
        return [{
            'label': c['word'],
            'value': round(abs(c['impact']), 2),
            'normalized': round(abs(c['impact']) / max(mx, 0.01) * 100, 1),
            'direction': c['direction'],
            'color': '#ef4444' if c['direction'] == 'positive' else '#22c55e'
        } for c in contributions]

    def _build_waterfall(self, contributions, total_score):
        """Build waterfall chart data."""
        waterfall = []
        running = 0
        for c in contributions:
            start = running
            running += c['contribution']
            waterfall.append({
                'label': c['feature'],
                'start': start,
                'end': running,
                'value': c['contribution'],
                'color': '#ef4444' if c['contribution'] >= 10 else '#f59e0b' if c['contribution'] >= 5 else '#3b82f6',
            })
        return waterfall

    def _generate_classification_explanation(self, cls_result, word_contribs):
        """Generate a detailed classification explanation."""
        cls = cls_result.get('class', 'Unknown')
        conf = cls_result.get('confidence', 0)
        top = [c['word'] for c in word_contribs[:5] if c['impact'] > 0]
        ws = ', '.join(top) if top else 'contextual patterns'
        
        if cls_result.get('is_novel'):
            return (
                f'Novel hazard detected (confidence {conf}% — below 35% threshold). '
                f'No known safety category adequately matches this report pattern. '
                f'Key terms: {ws}. Requires safety officer classification.'
            )
        return (
            f'Classified as "{cls}" with {conf}% confidence. '
            f'The model identified the following key signals: {ws}. '
            f'{"Strong confidence — classification is reliable." if conf >= 60 else "Moderate confidence — verify with domain expert if critical."}'
        )


xai_engine = None

def get_xai_engine():
    global xai_engine
    if xai_engine is None:
        xai_engine = XAIEngine()
    return xai_engine
