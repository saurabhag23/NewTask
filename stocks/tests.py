from django.test import TestCase
from stocks.models import StockData
from stocks.api import fetch_stock_data
from unittest.mock import patch
from datetime import date
from .views import BacktestView

class FetchStockDataTest(TestCase):
    @patch('stocks.api.requests.get')
    def test_fetch_stock_data_success(self, mock_get):
        # Mocking the requests.get to return a predefined response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "Time Series (Daily)": {
                "2020-01-01": {
                    "1. open": "300",
                    "2. high": "305",
                    "3. low": "295",
                    "4. close": "300",
                    "5. volume": "1000000"
                }
            }
        }

        fetch_stock_data('AAPL')
        self.assertEqual(StockData.objects.count(), 1)
        stock = StockData.objects.first()
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertEqual(stock.close_price, 300.0)

    @patch('stocks.api.requests.get')
    def test_api_failure(self, mock_get):
        # Simulating an API failure
        mock_get.return_value.raise_for_status.side_effect = Exception('API failure')
        
        with self.assertRaises(Exception):
            fetch_stock_data('AAPL')
class FetchAndStoreIntegrationTest(TestCase):
    def test_complete_flow(self):
        

        # Trigger data fetch
        fetch_stock_data('AAPL')  # Ensure this is the actual call you would use in production

        # Check data is stored
        self.assertTrue(StockData.objects.exists())
        self.assertEqual(StockData.objects.filter(symbol='AAPL').count(), 1)

class BacktestLogicTests(TestCase):

    def setUp(self):
        # Set up test data
        StockData.objects.create(symbol="AAPL", date=date(2020, 1, 1), close_price=150.0, open_price=145.0, high_price=155.0, low_price=140.0, volume=1000)
        StockData.objects.create(symbol="AAPL", date=date(2020, 1, 2), close_price=155.0, open_price=150.0, high_price=160.0, low_price=149.0, volume=1000)
        StockData.objects.create(symbol="AAPL", date=date(2020, 1, 3), close_price=158.0, open_price=154.0, high_price=159.0, low_price=151.0, volume=1000)
        # More data points as needed for comprehensive testing

    def test_moving_average_calculation(self):
        """
        Test that moving averages are calculated correctly.
        """
        response = self.client.post('/stocks/backtest/', {'symbol': 'AAPL', 'initial_investment': 10000, 'short_window': 1, 'long_window': 2})
        self.assertIn('short_ma', response.context)
        self.assertAlmostEqual(response.context['short_ma'], 155.0)  # Check if the short moving average is calculated correctly

    def test_buy_sell_logic(self):
        """
        Test the buy and sell logic based on moving averages.
        """
        response = self.client.post('/stocks/backtest/', {'symbol': 'AAPL', 'initial_investment': 10000, 'short_window': 1, 'long_window': 2})
        trades = response.context['trades']
        self.assertEqual(len(trades), 2)  # Assuming at least one buy and one sell
        self.assertEqual(trades[0]['action'], 'buy')
        self.assertEqual(trades[1]['action'], 'sell')

    def test_output_summary(self):
        """
        Test the final output summary, including total return and max drawdown.
        """
        response = self.client.post('/stocks/backtest/', {'symbol': 'AAPL', 'initial_investment': 10000, 'short_window': 1, 'long_window': 2})
        self.assertIn('total_return', response.context)
        self.assertIn('max_drawdown', response.context)
        self.assertGreater(response.context['total_return'], 0)  # Check if there is a positive return
        self.assertLessEqual(response.context['max_drawdown'], 0)  # Check if drawdown is calculated and non-positive

    def test_edge_cases(self):
        """
        Test edge cases such as no data or invalid input.
        """
        response = self.client.post('/stocks/backtest/', {'symbol': 'XYZ', 'initial_investment': 10000, 'short_window': 1, 'long_window': 2})
        self.assertIn('error', response.context)  # Expect an error due to no data