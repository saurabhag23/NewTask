from django.core.management.base import BaseCommand
from datetime import timedelta, date
import numpy as np
import joblib
from stocks.models import StockPrediction, StockData

class Command(BaseCommand):
    help = 'Generate and store stock predictions for the given symbol around a specified date.'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Stock symbol to generate predictions for')
        parser.add_argument('base_date', type=str, help='Date from which to start predictions (YYYY-MM-DD)')
        parser.add_argument('days', type=int, help='Number of days to predict before and after the base date')

    def handle(self, *args, **options):
        symbol = options['symbol']
        base_date = date.fromisoformat(options['base_date'])
        days = options['days']
        
        # Load your model directly here instead of using settings
        model_path = './stocks/linear_regression_model.pkl'  # Adjusted relative path
        model = joblib.load(model_path)  # Load the model

        # Fetch the most recent stock data entry for the symbol
        stock = StockData.objects.filter(symbol=symbol).order_by('date').first()
        if not stock:
            self.stdout.write(self.style.ERROR(f'No StockData found for symbol {symbol}'))
            return

        # Generate dates for the predictions
        dates = [base_date + timedelta(days=i) for i in range(-days, days + 1)]
        date_ordinals = np.array([d.toordinal() for d in dates]).reshape(-1, 1)

        # Use your model to generate predictions
        predictions = model.predict(date_ordinals).flatten()

        # Store predictions in the database
        for pred_date, pred_price in zip(dates, predictions):
            StockPrediction.objects.update_or_create(
                stock=stock,
                prediction_date=pred_date,
                defaults={'predicted_close_price': pred_price}
            )
        self.stdout.write(self.style.SUCCESS(f'Successfully saved predictions for {symbol} around {base_date}.'))
