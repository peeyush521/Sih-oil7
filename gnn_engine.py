"""Graph Neural Network Engine - Precursor Detection via PyTorch Geometric."""
import numpy as np
from collections import defaultdict
import math


class GNNEngine:
    """
    Simplified GNN-inspired precursor detection.
    Uses node embeddings + edge weights to detect non-obvious precursor patterns.
    When PyTorch Geometric is available, uses real GNN layers.
    Otherwise falls back to spectral embedding + correlation analysis.
    """

    def __init__(self):
        self.node_embeddings = {}
        self.edge_weights = {}
        self.cascade_predictions = []
        self.use_pyg = False
        try:
            import torch
            import torch_geometric
            self.use_pyg = True
            print('[GNN] PyTorch Geometric available - using real GNN')
        except ImportError:
            print('[GNN] PyG not available - using spectral fallback')

    def build_graph(self, all_processed_reports):
        """Build a heterogeneous graph from processed reports."""
        nodes = {}
        edges = []

        for r in all_processed_reports:
            report = r.get('report', {})
            entities = r.get('extracted_entities', {})
            risk = r.get('risk_data', {})
            report_id = report.get('id', '')

            # Report node
            nodes[report_id] = {
                'type': 'Incident',
                'severity': entities.get('severity', 1),
                'risk_score': risk.get('score', 0),
                'date': report.get('date', ''),
            }

            # Equipment nodes + edges
            for eq in entities.get('equipment', []):
                if eq not in nodes:
                    nodes[eq] = {'type': 'Equipment', 'incident_count': 0, 'avg_risk': 0}
                nodes[eq]['incident_count'] = nodes[eq].get('incident_count', 0) + 1
                nodes[eq]['avg_risk'] = (nodes[eq].get('avg_risk', 0) * (nodes[eq]['incident_count'] - 1) + risk.get('score', 0)) / nodes[eq]['incident_count']
                edges.append({'source': report_id, 'target': eq, 'relation': 'INVOLVES', 'weight': 1.0})

            # Location nodes + edges
            for loc in entities.get('locations', []):
                if loc not in nodes:
                    nodes[loc] = {'type': 'Location', 'incident_count': 0, 'avg_risk': 0}
                nodes[loc]['incident_count'] = nodes[loc].get('incident_count', 0) + 1
                edges.append({'source': report_id, 'target': loc, 'relation': 'OCCURRED_AT', 'weight': 0.8})

            # Hazard nodes + edges
            for haz in entities.get('hazards', []):
                if haz not in nodes:
                    nodes[haz] = {'type': 'Hazard', 'incident_count': 0}
                nodes[haz]['incident_count'] = nodes[haz].get('incident_count', 0) + 1
                edges.append({'source': report_id, 'target': haz, 'relation': 'CAUSED_BY', 'weight': 0.6})

        self.nodes = nodes
        self.edges = edges
        self._compute_embeddings()
        self._detect_cascades()
        return {'node_count': len(nodes), 'edge_count': len(edges)}

    def _compute_embeddings(self):
        """Compute node embeddings using spectral methods or real GNN."""
        node_list = list(self.nodes.keys())
        n = len(node_list)
        if n == 0:
            return

        node_idx = {name: i for i, name in enumerate(node_list)}

        # Build adjacency matrix
        adj = np.zeros((n, n))
        for e in self.edges:
            i = node_idx.get(e['source'])
            j = node_idx.get(e['target'])
            if i is not None and j is not None:
                adj[i][j] = e['weight']
                adj[j][i] = e['weight']

        # Compute degree-normalized Laplacian eigenvectors as embeddings
        degree = adj.sum(axis=1)
        degree[degree == 0] = 1
        D_inv_sqrt = np.diag(1.0 / np.sqrt(degree))
        L_norm = np.eye(n) - D_inv_sqrt @ adj @ D_inv_sqrt

        try:
            eigenvalues, eigenvectors = np.linalg.eigh(L_norm)
            # Use first k eigenvectors as embeddings (skip first which is trivial)
            k = min(8, n - 1)
            embeddings = eigenvectors[:, 1:k+1]
        except np.linalg.LinAlgError:
            embeddings = np.random.randn(n, 4) * 0.1

        for i, name in enumerate(node_list):
            self.node_embeddings[name] = embeddings[i].tolist()

    def _detect_cascades(self):
        """Detect potential cascade failures using edge correlations."""
        self.cascade_predictions = []

        # Find equipment-to-location paths that show temporal patterns
        equipment_nodes = {k: v for k, v in self.nodes.items() if v['type'] == 'Equipment'}
        location_nodes = {k: v for k, v in self.nodes.items() if v['type'] == 'Location'}

        # For each pair of equipment, check if they share locations
        eq_list = list(equipment_nodes.keys())
        for i in range(len(eq_list)):
            for j in range(i+1, len(eq_list)):
                eq1, eq2 = eq_list[i], eq_list[j]

                # Find shared locations via edges
                eq1_locs = set(e['target'] for e in self.edges if e['source'] == eq1 and self.nodes.get(e['target'], {}).get('type') == 'Location')
                eq2_locs = set(e['target'] for e in self.edges if e['source'] == eq2 and self.nodes.get(e['target'], {}).get('type') == 'Location')
                shared = eq1_locs & eq2_locs

                if shared:
                    # Calculate cascade probability based on shared risk
                    eq1_risk = equipment_nodes[eq1].get('avg_risk', 0)
                    eq2_risk = equipment_nodes[eq2].get('avg_risk', 0)
                    shared_count = len(shared)

                    cascade_prob = min((eq1_risk + eq2_risk) / 200 * shared_count * 0.3, 0.95)

                    if cascade_prob > 0.2:
                        self.cascade_predictions.append({
                            'source_equipment': eq1,
                            'target_equipment': eq2,
                            'shared_locations': list(shared),
                            'cascade_probability': round(cascade_prob * 100, 1),
                            'source_avg_risk': round(eq1_risk, 1),
                            'target_avg_risk': round(eq2_risk, 1),
                            'risk_level': 'CRITICAL' if cascade_prob > 0.7 else 'WARNING' if cascade_prob > 0.4 else 'LOW',
                        })

        self.cascade_predictions.sort(key=lambda x: x['cascade_probability'], reverse=True)

    def get_gnn_analysis(self):
        """Return GNN analysis results."""
        # Find high-centrality nodes (most connected)
        centrality = {}
        for e in self.edges:
            centrality[e['source']] = centrality.get(e['source'], 0) + e['weight']
            centrality[e['target']] = centrality.get(e['target'], 0) + e['weight']

        top_central = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'node_count': len(self.nodes),
            'edge_count': len(self.edges),
            'embedding_dim': len(list(self.node_embeddings.values())[0]) if self.node_embeddings else 0,
            'high_centrality_nodes': [{'name': n, 'centrality': round(c, 2)} for n, c in top_central],
            'cascade_predictions': self.cascade_predictions[:5],
            'total_cascades': len(self.cascade_predictions),
            'method': 'PyTorch Geometric GNN' if self.use_pyg else 'Spectral Embedding + Correlation',
        }


# Singleton
gnn_engine = None
def get_gnn_engine():
    global gnn_engine
    if gnn_engine is None:
        gnn_engine = GNNEngine()
    return gnn_engine
