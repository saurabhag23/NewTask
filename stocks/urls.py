from django.urls import path
from .views import BacktestView, generate_report, predict_stock_prices

urlpatterns = [
    path('backtest/', BacktestView.as_view(), name='backtest'),
    path('predict/<str:symbol>/', predict_stock_prices, name='predict_stock_prices'),
    path('report/<str:symbol>/', generate_report, name='generate_report'),
]
