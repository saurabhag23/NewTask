import os
from django.apps import AppConfig
import joblib

class StocksConfig(AppConfig):
    # Proper naming and identification of the configuration for the 'stocks' Django app
    name = 'stocks'
    model = None  # Initialize the model attribute to None

    def ready(self):
        # This method is called as soon as the app registry is fully populated
        print("Loading the machine learning model for stock predictions...")
        
        # Construct the path to the model file relative to the current file
        model_path = os.path.join(os.path.dirname(__file__), 'linear_regression_model.pkl')
        
        # Check if the model file exists at the specified path
        if os.path.exists(model_path):
            # If the file exists, load the model using joblib
            self.model = joblib.load(model_path)
            print("Model loaded successfully:", self.model)
        else:
            # If the file does not exist, log a clear error message
            print("Model file not found at:", model_path)
            # Consider raising an exception or a warning here to notify about the missing model
            # raise FileNotFoundError(f"Model file not found at: {model_path}")
