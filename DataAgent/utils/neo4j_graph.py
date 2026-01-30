import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class Neo4jGraphBuilder:
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        if NEO4J_AVAILABLE:
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
            except Exception:
                pass
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def build_correlation_graph(self, df: pd.DataFrame, threshold: float = 0.5) -> Dict:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return {'nodes': [], 'edges': []}
        
        corr_matrix = df[numeric_cols].corr().abs()
        nodes = [{'id': col, 'label': col[:20], 'type': 'feature'} for col in numeric_cols[:15]]
        edges = []
        
        for i, col1 in enumerate(numeric_cols[:15]):
            for j, col2 in enumerate(numeric_cols[:15]):
                if i < j:
                    corr_val = corr_matrix.loc[col1, col2]
                    if not pd.isna(corr_val) and corr_val >= threshold:
                        edges.append({
                            'source': col1,
                            'target': col2,
                            'weight': float(corr_val),
                            'type': 'correlation'
                        })
        
        if not edges and len(nodes) >= 2:
            threshold = 0.3
            for i, col1 in enumerate(numeric_cols[:15]):
                for j, col2 in enumerate(numeric_cols[:15]):
                    if i < j:
                        corr_val = corr_matrix.loc[col1, col2]
                        if not pd.isna(corr_val) and corr_val >= threshold:
                            edges.append({
                                'source': col1,
                                'target': col2,
                                'weight': float(corr_val),
                                'type': 'correlation'
                            })
        
        return {'nodes': nodes, 'edges': edges}
    
    def build_segmentation_graph(self, df: pd.DataFrame, segment_col: str, value_col: str) -> Dict:
        if segment_col not in df.columns or value_col not in df.columns:
            return {'nodes': [], 'edges': []}
        
        segments = df[segment_col].unique()[:15]
        nodes = [{'id': str(seg), 'label': str(seg), 'type': 'segment'} for seg in segments]
        
        if value_col in df.select_dtypes(include=[np.number]).columns:
            segment_stats = df.groupby(segment_col)[value_col].agg(['mean', 'count']).reset_index()
            edges = []
            for _, row in segment_stats.iterrows():
                nodes.append({
                    'id': f"stat_{row[segment_col]}",
                    'label': f"Avg: {row['mean']:.2f}",
                    'type': 'statistic'
                })
                edges.append({
                    'source': str(row[segment_col]),
                    'target': f"stat_{row[segment_col]}",
                    'weight': float(row['count']),
                    'type': 'has_statistic'
                })
        
        return {'nodes': nodes, 'edges': edges}
    
    def build_feature_relationship_graph(self, df: pd.DataFrame, top_n: int = 10) -> Dict:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:top_n]
        if len(numeric_cols) < 2:
            return {'nodes': [], 'edges': []}
        
        nodes = [{'id': col, 'label': col[:20], 'type': 'feature'} for col in numeric_cols]
        edges = []
        
        for i, col1 in enumerate(numeric_cols):
            for j, col2 in enumerate(numeric_cols):
                if i < j:
                    corr = df[[col1, col2]].corr().iloc[0, 1]
                    if abs(corr) > 0.5:
                        edges.append({
                            'source': col1,
                            'target': col2,
                            'weight': abs(corr),
                            'type': 'related' if corr > 0 else 'inverse'
                        })
        
        return {'nodes': nodes, 'edges': edges}
