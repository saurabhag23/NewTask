import os
import tempfile
from django.apps import apps
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
import requests
from django.shortcuts import render
from django.views.generic import View
from .models import StockData, StockPrediction
from django.conf import settings
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .apps import StocksConfig
import datetime
import matplotlib
matplotlib.use('Agg')  # Set matplotlib to use the 'Agg' backend, which is for PNGs and does not require a GUI.
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from django.http import JsonResponse, HttpResponse
from reportlab.pdfgen import canvas as reportlab_canvas
from io import BytesIO
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import reportlab.lib.pagesizes as pagesizes

logger = logging.getLogger(__name__)

# Utilizes the Alpha Vantage API to fetch stock data
def fetch_stock_data(symbol):
    """
    Fetches stock data from Alpha Vantage API and stores it in the database.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": settings.ALPHA_VANTAGE_API_KEY  # Securely fetch your API key from settings
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        if "Error Message" in data:
            raise ValueError(f"API error for {symbol}: {data['Error Message']}")

        # Iterate over each day's data and store or update it in the database
        for date, daily_data in data['Time Series (Daily)'].items():
            StockData.objects.update_or_create(
                symbol=symbol,
                date=date,
                defaults={
                    'open_price': float(daily_data['1. open']),
                    'high_price': float(daily_data['2. high']),
                    'low_price': float(daily_data['3. low']),
                    'close_price': float(daily_data['4. close']),
                    'volume': int(daily_data['5. volume'])
                }
            )
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise

# View for handling backtesting logic via web form submission
@method_decorator(csrf_exempt, name='dispatch')
class BacktestView(View):
    def get(self, request, *args, **kwargs):
        # Render the initial backtest form
        return render(request, 'stocks/backtest_form.html')

    def post(self, request, *args, **kwargs):
        # Handle form submission for backtesting by computing performance based on historical data
        symbol = request.POST.get('symbol', 'AAPL')
        initial_investment = float(request.POST.get('initial_investment', 10000))
        short_window = int(request.POST.get('short_window', 50))
        long_window = int(request.POST.get('long_window', 200))

        # Retrieve stock data and handle cases where no data is available
        data = StockData.objects.filter(symbol=symbol).order_by('date')
        if not data.exists():
            return render(request, 'stocks/backtest_form.html', {'error': 'No data available for the symbol.'})

        # Initialize variables for tracking investment performance
        investment = initial_investment
        shares = 0
        performance = []
        max_drawdown = 0
        peak = initial_investment

        # Calculate buy and sell points based on moving averages
        for stock in data:
            short_ma = stock.calculate_moving_average(short_window)
            long_ma = stock.calculate_moving_average(long_window)

            # Buy logic
            if short_ma < stock.close_price and shares == 0:
                shares = investment / stock.close_price
                investment = 0
                performance.append({'action': 'buy', 'date': stock.date, 'price': stock.close_price})

            # Sell logic
            elif long_ma > stock.close_price and shares > 0:
                investment = shares * stock.close_price
                shares = 0
                performance.append({'action': 'sell', 'date': stock.date, 'price': stock.close_price})
                current_drawdown = (peak - investment) / peak
                max_drawdown = max(max_drawdown, current_drawdown)
                peak = max(peak, investment)

        final_amount = investment + (shares * data.last().close_price if data else 0)
        total_return = final_amount - initial_investment

        # Prepare and render results with calculated financial metrics
        context = {
            'initial_investment': initial_investment,
            'final_amount': final_amount,
            'total_return': total_return,
            'max_drawdown': max_drawdown * 100,
            'number_of_trades': len(performance),
            'trades': performance,
        }
        return render(request, 'stocks/results.html', context)

# Function to predict stock prices for the next day based on the last available data
@require_http_methods(["GET"])
def predict_stock_prices(request, symbol):
    """
    Predicts the next day's stock price for a given symbol using a pre-trained model.
    """
    try:
        # Load the model from the application configuration
        stocks_config = apps.get_app_config('stocks')
        model = stocks_config.model
        if not model:
            return JsonResponse({'error': 'Model is not loaded'}, status=500)

        # Check the latest available stock data to base the prediction on
        last_data = StockData.objects.filter(symbol=symbol).order_by('-date').first()
        if not last_data:
            return JsonResponse({'error': 'Not enough data to make a prediction'}, status=400)

        # Prepare input for the model and predict
        last_day_number = (last_data.date - datetime.date(2020, 1, 1)).days  # Assuming model trained with day count as input
        input_data = np.array([[last_day_number + 1]])  # Predicting for the next day
        predicted_price = model.predict(input_data)[0]

        # Store and return the prediction
        prediction_date = last_data.date + datetime.timedelta(days=1)
        StockPrediction.objects.create(
            stock=last_data,
            prediction_date=prediction_date,
            predicted_close_price=predicted_price
        )

        return JsonResponse({
            'symbol': symbol,
            'prediction_date': prediction_date.isoformat(),
            'predicted_price': predicted_price
        }, status=200)

    except Exception as e:
        logger.error(f"Error in predicting stock price: {e}")
        return JsonResponse({'error': str(e)}, status=500)

# Function to generate a detailed report of stock predictions vs. actual data, with visualizations and key metrics
def generate_report(request, symbol):
    """
    Generates a comprehensive PDF report comparing predicted and actual stock prices,
    along with key performance metrics.
    """
    try:
        # Setup for plotting and metrics calculation
        fig = Figure(figsize=(10, 5))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        ax.set_title(f'Stock Price Prediction vs Actual for {symbol}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')

        # Simulate data for demonstration purposes
        dates = [datetime.date.today() - datetime.timedelta(days=i) for i in range(10)]
        prices = [100 + i * 2 for i in range(10)]  # Predicted prices
        actual_prices = [95 + i * 2 for i in range(10)]  # Actual prices

        ax.plot(dates, prices, label='Predicted Prices')
        ax.plot(dates, actual_prices, label='Actual Prices')
        ax.legend()

        # Calculate and display key metrics such as mean, maximum, and minimum prices
        mean_predicted = np.mean(prices)
        mean_actual = np.mean(actual_prices)
        max_predicted = np.max(prices)
        max_actual = np.max(actual_prices)
        min_predicted = np.min(prices)
        min_actual = np.min(actual_prices)

        # Save the plot to a temporary file for inclusion in the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            fig.savefig(tmpfile.name)

        # Set up PDF generation
        response = HttpResponse(content_type='application/pdf')
        p = reportlab_canvas.Canvas(response, pagesize=pagesizes.letter)
        width, height = pagesizes.letter  # Standard letter page size

        # Add text elements to the PDF
        p.drawString(50, 800, "Stock Performance Report")
        p.drawString(50, 785, f"Report for {symbol}")
        p.drawString(50, 770, f"Mean Predicted Price: ${mean_predicted:.2f}")
        p.drawString(50, 755, f"Mean Actual Price: ${mean_actual:.2f}")
        p.drawString(50, 740, f"Max Predicted Price: ${max_predicted:.2f}")
        p.drawString(50, 725, f"Max Actual Price: ${max_actual:.2f}")
        p.drawString(50, 710, f"Min Predicted Price: ${min_predicted:.2f}")
        p.drawString(50, 695, f"Min Actual Price: ${min_actual:.2f}")

        # Insert the plot into the PDF
        p.drawImage(tmpfile.name, 50, 400, width=500, height=200)
        p.showPage()
        p.save()

        # Clean up the temporary file
        os.unlink(tmpfile.name)

        return response

    except Exception as e:
        logger.error(f"Error generating the report: {str(e)}")
        return HttpResponse(f"Error: {str(e)}")
