"""
Classification Model Registry - Multiple classification models
"""
from typing import Dict, Any
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier, 
    AdaBoostClassifier, ExtraTreesClassifier, VotingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from config import RANDOM_STATE


class ClassificationModelRegistry:
    """
    Registry for classification models following MCP pattern
    """
    
    def __init__(self):
        self.models = {
            'logistic_regression': self._create_logistic_regression,
            'random_forest': self._create_random_forest,
            'gradient_boosting': self._create_gradient_boosting,
            'svm': self._create_svm,
            'neural_network': self._create_neural_network,
            'naive_bayes': self._create_naive_bayes,
            'knn': self._create_knn,
            'decision_tree': self._create_decision_tree,
            'adaboost': self._create_adaboost,
            'extra_trees': self._create_extra_trees,
            'voting_classifier': self._create_voting_classifier
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
    
    def _create_logistic_regression(self, config: Dict[str, Any]) -> LogisticRegression:
        return LogisticRegression(
            max_iter=config.get('max_iter', 1000),
            random_state=RANDOM_STATE,
            **{k: v for k, v in config.items() if k != 'max_iter'}
        )
    
    def _create_random_forest(self, config: Dict[str, Any]) -> RandomForestClassifier:
        return RandomForestClassifier(
            n_estimators=config.get('n_estimators', 100),
            random_state=RANDOM_STATE,
            **{k: v for k, v in config.items() if k != 'n_estimators'}
        )
    
    def _create_gradient_boosting(self, config: Dict[str, Any]) -> GradientBoostingClassifier:
        return GradientBoostingClassifier(
            n_estimators=config.get('n_estimators', 100),
            random_state=RANDOM_STATE,
            **{k: v for k, v in config.items() if k != 'n_estimators'}
        )
    
    def _create_svm(self, config: Dict[str, Any]) -> SVC:
        return SVC(
            random_state=RANDOM_STATE,
            probability=True,
            **config
        )
    
    def _create_neural_network(self, config: Dict[str, Any]) -> MLPClassifier:
        return MLPClassifier(
            hidden_layer_sizes=config.get('hidden_layer_sizes', (100, 50)),
            max_iter=config.get('max_iter', 500),
            random_state=RANDOM_STATE,
            **{k: v for k, v in config.items() if k not in ['hidden_layer_sizes', 'max_iter']}
        )
    
    def _create_naive_bayes(self, config: Dict[str, Any]) -> GaussianNB:
        return GaussianNB(**config)
    
    def _create_knn(self, config: Dict[str, Any]) -> KNeighborsClassifier:
        return KNeighborsClassifier(
            n_neighbors=config.get('n_neighbors', 5),
            **{k: v for k, v in config.items() if k != 'n_neighbors'}
        )
    
    def _create_decision_tree(self, config: Dict[str, Any]) -> DecisionTreeClassifier:
        return DecisionTreeClassifier(
            random_state=RANDOM_STATE,
            **config
        )
    
    def _create_adaboost(self, config: Dict[str, Any]) -> AdaBoostClassifier:
        return AdaBoostClassifier(
            n_estimators=config.get('n_estimators', 50),
            random_state=RANDOM_STATE,
            **{k: v for k, v in config.items() if k != 'n_estimators'}
        )
    
    def _create_extra_trees(self, config: Dict[str, Any]) -> ExtraTreesClassifier:
        return ExtraTreesClassifier(
            n_estimators=config.get('n_estimators', 100),
            random_state=RANDOM_STATE,
            **{k: v for k, v in config.items() if k != 'n_estimators'}
        )
    
    def _create_voting_classifier(self, config: Dict[str, Any]) -> VotingClassifier:
        estimators = config.get('estimators', [
            ('rf', RandomForestClassifier(n_estimators=50, random_state=RANDOM_STATE)),
            ('gb', GradientBoostingClassifier(n_estimators=50, random_state=RANDOM_STATE)),
            ('lr', LogisticRegression(max_iter=500, random_state=RANDOM_STATE))
        ])
        return VotingClassifier(estimators=estimators, voting=config.get('voting', 'soft'))
