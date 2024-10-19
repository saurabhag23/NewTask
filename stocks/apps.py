import os
from django.apps import AppConfig
import joblib


class StocksConfig(AppConfig):
    name = 'stocks'
    model = None

    def ready(self):
        print("Loading the model...")
        model_path = os.path.join(os.path.dirname(__file__), 'linear_regression_model.pkl')
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print("Model loaded successfully:", self.model)
        else:
            print("Model file not found at:", model_path)