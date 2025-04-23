from django.core.management.base import BaseCommand
import pandas as pd
import xgboost as xgb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MODEL_PATH = r"match_model.xgb"
IMPORTANCE_TYPE = "weight"

class Command(BaseCommand):
    help = "Generate a feature importance plot for the XGBoost model."

    def handle(self, *args, **options):
        model = xgb.Booster()
        try:
            model.load_model(MODEL_PATH)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading model: {e}"))
            return

        df = self._get_feature_importance(model, IMPORTANCE_TYPE)
        
        plt.figure(figsize=(10, 6))
        plt.barh(df['feature'][::-1], df['importance'][::-1])
        plt.xlabel('Importance Score')
        plt.title('Feature Importance')
        
        plt.savefig('feature_importance.png')
        self.stdout.write(self.style.SUCCESS('Feature importance plot saved to feature_importance.png'))

    def _get_feature_importance(self, model, importance_type: str = 'weight') -> pd.DataFrame:
        importance = model.get_score(importance_type=importance_type)
        df = pd.DataFrame({
            'feature': list(importance.keys()),
            'importance': list(importance.values())
        }).sort_values('importance', ascending=False)
        return df
