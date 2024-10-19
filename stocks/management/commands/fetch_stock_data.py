from django.core.management.base import BaseCommand
from requests.exceptions import RequestException
from stocks.views import fetch_stock_data as api_fetch_stock_data 

class Command(BaseCommand):
    help = 'Fetches stock data and stores it in the database'

    def handle(self, *args, **options):
        symbols = ['AAPL']  # Extend this list with more symbols if needed
        for symbol in symbols:
            try:
                api_fetch_stock_data(symbol)
                self.stdout.write(self.style.SUCCESS(f'Successfully updated data for {symbol}'))
            except RequestException as e:
                self.stdout.write(self.style.ERROR(f'Network error occurred: {str(e)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
