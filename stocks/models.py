from django.db import models
from django.db.models import Avg, F, Window
from django.db.models.functions import RowNumber

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['date', 'symbol']),
        ]
    def calculate_moving_average(self, window_size=50):
        """
        Calculate the moving average over a specified window size.
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
        return f"{self.symbol} data on {self.date}"

class StockPrediction(models.Model):
    stock = models.ForeignKey(StockData, on_delete=models.CASCADE, related_name='predictions')
    prediction_date = models.DateField()
    predicted_close_price = models.FloatField()

    def __str__(self):
        return f"Prediction for {self.stock.symbol} on {self.prediction_date}"