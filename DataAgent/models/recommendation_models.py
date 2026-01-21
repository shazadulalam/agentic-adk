"""
Recommendation Model Registry - Multiple recommendation models
"""
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class CollaborativeFiltering:
    """Simple collaborative filtering recommendation model"""
    
    def __init__(self, similarity_metric='cosine'):
        self.similarity_metric = similarity_metric
        self.user_item_matrix = None
        self.user_similarity = None
        self.item_similarity = None
    
    def fit(self, interactions: pd.DataFrame, user_col: str = 'user_id', 
            item_col: str = 'item_id', rating_col: str = 'rating'):
        """Fit the model on user-item interactions"""
        # Create user-item matrix
        self.user_item_matrix = interactions.pivot_table(
            index=user_col, columns=item_col, values=rating_col, fill_value=0
        )
        
        # Calculate similarities
        if self.similarity_metric == 'cosine':
            self.user_similarity = cosine_similarity(self.user_item_matrix)
            self.item_similarity = cosine_similarity(self.user_item_matrix.T)
        
        return self
    
    def recommend_items(self, user_id: int, n_recommendations: int = 10) -> list:
        """Recommend items for a user"""
        if user_id not in self.user_item_matrix.index:
            return []
        
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        user_sim = self.user_similarity[user_idx]
        
        # Get items not yet rated by user
        user_ratings = self.user_item_matrix.loc[user_id]
        unrated_items = user_ratings[user_ratings == 0].index
        
        # Calculate predicted ratings
        scores = {}
        for item in unrated_items:
            item_idx = self.user_item_matrix.columns.get_loc(item)
            similar_users = np.argsort(user_sim)[::-1][1:11]  # Top 10 similar users
            
            numerator = sum(
                self.user_similarity[user_idx, sim_user] * 
                self.user_item_matrix.iloc[sim_user, item_idx]
                for sim_user in similar_users
            )
            denominator = sum(abs(self.user_similarity[user_idx, sim_user]) for sim_user in similar_users)
            
            if denominator > 0:
                scores[item] = numerator / denominator
        
        # Return top N recommendations
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]


class MatrixFactorization:
    """Matrix factorization recommendation model"""
    
    def __init__(self, n_components: int = 50, method: str = 'nmf'):
        self.n_components = n_components
        self.method = method
        self.model = None
        self.user_item_matrix = None
    
    def fit(self, interactions: pd.DataFrame, user_col: str = 'user_id',
            item_col: str = 'item_id', rating_col: str = 'rating'):
        """Fit the model"""
        self.user_item_matrix = interactions.pivot_table(
            index=user_col, columns=item_col, values=rating_col, fill_value=0
        )
        
        if self.method == 'nmf':
            self.model = NMF(n_components=self.n_components, random_state=42, max_iter=1000)
        else:  # svd
            self.model = TruncatedSVD(n_components=self.n_components, random_state=42)
        
        self.model.fit(self.user_item_matrix)
        return self
    
    def recommend_items(self, user_id: int, n_recommendations: int = 10) -> list:
        """Recommend items for a user"""
        if user_id not in self.user_item_matrix.index:
            return []
        
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        user_vector = self.user_item_matrix.iloc[user_idx:user_idx+1]
        
        # Transform and reconstruct
        if self.method == 'nmf':
            user_factors = self.model.transform(user_vector)
            predicted_ratings = self.model.inverse_transform(user_factors)
        else:  # svd
            user_factors = self.model.transform(user_vector)
            predicted_ratings = self.model.inverse_transform(user_factors)
        
        # Get top recommendations
        predicted_series = pd.Series(predicted_ratings[0], index=self.user_item_matrix.columns)
        user_rated = self.user_item_matrix.iloc[user_idx]
        unrated = predicted_series[user_rated == 0]
        
        return unrated.nlargest(n_recommendations).to_dict()


class ContentBasedFiltering:
    """Content-based recommendation model"""
    
    def __init__(self):
        self.item_features = None
        self.similarity_matrix = None
        self.scaler = StandardScaler()
    
    def fit(self, item_features: pd.DataFrame):
        """Fit on item features"""
        self.item_features = item_features
        features_scaled = self.scaler.fit_transform(item_features.select_dtypes(include=[np.number]))
        self.similarity_matrix = cosine_similarity(features_scaled)
        return self
    
    def recommend_items(self, item_id: int, n_recommendations: int = 10) -> list:
        """Recommend similar items"""
        if item_id not in self.item_features.index:
            return []
        
        item_idx = self.item_features.index.get_loc(item_id)
        similarities = self.similarity_matrix[item_idx]
        
        # Get top similar items (excluding itself)
        top_indices = np.argsort(similarities)[::-1][1:n_recommendations+1]
        recommendations = [
            (self.item_features.index[idx], similarities[idx])
            for idx in top_indices
        ]
        
        return recommendations


class RecommendationModelRegistry:
    """
    Registry for recommendation models following MCP pattern
    """
    
    def __init__(self):
        self.models = {
            'collaborative_filtering': self._create_collaborative_filtering,
            'matrix_factorization': self._create_matrix_factorization,
            'content_based': self._create_content_based,
            'hybrid': self._create_hybrid
        }
    
    def get_model(self, model_name: str, config: Dict[str, Any] = None) -> Any:
        """Get a model instance by name"""
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}. Available: {self.list_models()}")
        
        config = config or {}
        return self.models[model_name](config)
    
    def list_models(self) -> list:
        """List all available models"""
        return list(self.models.keys())
    
    def _create_collaborative_filtering(self, config: Dict[str, Any]) -> CollaborativeFiltering:
        return CollaborativeFiltering(
            similarity_metric=config.get('similarity_metric', 'cosine')
        )
    
    def _create_matrix_factorization(self, config: Dict[str, Any]) -> MatrixFactorization:
        return MatrixFactorization(
            n_components=config.get('n_components', 50),
            method=config.get('method', 'nmf')
        )
    
    def _create_content_based(self, config: Dict[str, Any]) -> ContentBasedFiltering:
        return ContentBasedFiltering()
    
    def _create_hybrid(self, config: Dict[str, Any]):
        """Hybrid recommendation model combining multiple approaches"""
        # Simple hybrid: average predictions from multiple models
        class HybridModel:
            def __init__(self):
                self.cf = CollaborativeFiltering()
                self.mf = MatrixFactorization()
            
            def fit(self, interactions, item_features=None):
                self.cf.fit(interactions)
                self.mf.fit(interactions)
                if item_features is not None:
                    self.cb = ContentBasedFiltering()
                    self.cb.fit(item_features)
                return self
            
            def recommend_items(self, user_id, n_recommendations=10):
                cf_recs = dict(self.cf.recommend_items(user_id, n_recommendations))
                mf_recs = self.mf.recommend_items(user_id, n_recommendations)
                
                # Combine scores
                combined = {}
                for item, score in cf_recs.items():
                    combined[item] = combined.get(item, 0) + score * 0.5
                for item, score in mf_recs.items():
                    combined[item] = combined.get(item, 0) + score * 0.5
                
                return sorted(combined.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        
        return HybridModel()
