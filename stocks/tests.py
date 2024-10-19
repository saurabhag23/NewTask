from django.test import TestCase
from stocks.models import StockData
from stocks.api import fetch_stock_data
from unittest.mock import patch
from datetime import date

class FetchStockDataTest(TestCase):
    @patch('stocks.api.requests.get')
    def test_fetch_stock_data_success(self, mock_get):
        # This test verifies that stock data fetching and storage work as expected.
        # It mocks the external API call to return a predefined response successfully.
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

        # Call the function under test
        fetch_stock_data('AAPL')

        # Validate that the stock data is correctly stored in the database
        self.assertEqual(StockData.objects.count(), 1)
        stock = StockData.objects.first()
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertEqual(stock.close_price, 300.0)

    @patch('stocks.api.requests.get')
    def test_api_failure(self, mock_get):
        # This test ensures that the system appropriately handles and reports API failures.
        # It simulates an API failure by raising an exception when the API is called.
        mock_get.return_value.raise_for_status.side_effect = Exception('API failure')
        
        # Validate that an exception is raised during API failure
        with self.assertRaises(Exception):
            fetch_stock_data('AAPL')

class FetchAndStoreIntegrationTest(TestCase):
    def test_complete_flow(self):
        # This integration test checks the complete flow from fetching data to storing it in the database.
        # It assumes that the fetch_stock_data function is integrated and functional without mocking.
        fetch_stock_data('AAPL')  # Trigger data fetch

        # Check that the data has been stored correctly
        self.assertTrue(StockData.objects.exists())
        self.assertEqual(StockData.objects.filter(symbol='AAPL').count(), 1)

class BacktestLogicTests(TestCase):
    def setUp(self):
        # Setup sample stock data to be used in various backtest logic tests.
        StockData.objects.create(symbol="AAPL", date=date(2020, 1, 1), close_price=150.0, 
                                 open_price=145.0, high_price=155.0, low_price=140.0, volume=1000)
        StockData.objects.create(symbol="AAPL", date=date(2020, 1, 2), close_price=155.0, 
                                 open_price=150.0, high_price=160.0, low_price=149.0, volume=1000)
        StockData.objects.create(symbol="AAPL", date=date(2020, 1, 3), close_price=158.0, 
                                 open_price=154.0, high_price=159.0, low_price=151.0, volume=1000)

    def test_moving_average_calculation(self):
        # Test to verify that the moving average calculation is accurate.
        response = self.client.post('/stocks/backtest/', {'symbol': 'AAPL', 'initial_investment': 10000, 
                                                          'short_window': 1, 'long_window': 2})
        self.assertIn('short_ma', response.context)
        self.assertAlmostEqual(response.context['short_ma'], 155.0)  # Verify correct moving average

    def test_buy_sell_logic(self):
        # Test to verify the buy and sell logic based on moving averages.
        response = self.client.post('/stocks/backtest/', {'symbol': 'AAPL', 'initial_investment': 10000, 
                                                          'short_window': 1, 'long_window': 2})
        trades = response.context['trades']
        self.assertEqual(len(trades), 2)  # Expect buy and sell actions
        self.assertEqual(trades[0]['action'], 'buy')
        self.assertEqual(trades[1]['action'], 'sell')

    def test_output_summary(self):
        # Test to validate the summary output of backtesting, including total return and max drawdown.
        response = self.client.post('/stocks/backtest/', {'symbol': 'AAPL', 'initial_investment': 10000, 
                                                          'short_window': 1, 'long_window': 2})
        self.assertIn('total_return', response.context)
        self.assertIn('max_drawdown', response.context)
        self.assertGreater(response.context['total_return'], 0)  # Verify positive return
        self.assertLessEqual(response.context['max_drawdown'], 0)  # Ensure drawdown is non-positive

    def test_edge_cases(self):
        # Test handling of edge cases like missing data or invalid inputs.
        response = self.client.post('/stocks/backtest/', {'symbol': 'XYZ', 'initial_investment': 10000, 
                                                          'short_window': 1, 'long_window': 2})
        self.assertIn('error', response.context)  # Verify error handling for non-existent stock data
