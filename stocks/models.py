from django.db import models
from django.db.models import Avg, F, Window
from django.db.models.functions import RowNumber

class StockData(models.Model):
    # Fields to store the stock symbol and various prices for each trading day.
    symbol = models.CharField(max_length=10)  # The ticker symbol for the stock.
    date = models.DateField()  # The trading day.
    open_price = models.FloatField()  # The price of the stock at the opening of the trading day.
    high_price = models.FloatField()  # The highest price of the stock during the trading day.
    low_price = models.FloatField()  # The lowest price of the stock during the trading day.
    close_price = models.FloatField()  # The price of the stock at the closing of the trading day.
    volume = models.BigIntegerField()  # The volume of stock traded during the day.

    class Meta:
        # Creating an index on 'date' and 'symbol' to improve query performance.
        indexes = [
            models.Index(fields=['date', 'symbol']),
        ]

    def calculate_moving_average(self, window_size=50):
        """
        Calculates the moving average of the closing price over a specified window size.
        This method filters the stock data by symbol and date, annotates each entry with
        a row number ordered by date, and computes the average closing price for the top 
        entries defined by the window size.
        
        Args:
        window_size (int): The number of days to include in the moving average calculation.

        Returns:
        float: The average closing price over the window size.
        """
        return (StockData.objects
                .filter(symbol=self.symbol, date__lte=self.date)
                .order_by('-date')
                .annotate(row_number=Window(
                    expression=RowNumber(),
                    order_by=F('date').desc()))
                .filter(row_number__lte=window_size)
                .aggregate(Avg('close_price'))['close_price__avg'])

    def __str__(self):
        # String representation to identify this stock data easily in admin or debug.
        return f"{self.symbol} data on {self.date}"

class StockPrediction(models.Model):
    # ForeignKey relationship to associate each prediction with corresponding stock data.
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name='predictions')
    prediction_date = models.DateField()  # The date for which the prediction is made.
    predicted_close_price = models.FloatField()  # The predicted closing price of the stock.

    def __str__(self):
        # String representation to easily identify this prediction.
        return f"Prediction for {self.stock.symbol} on {self.prediction_date}"
