import requests
import json
import time
import os
import logging


class CurrencyConverter:
    def __init__(self, api_url="https://api.exchangerate-api.com/v4/latest/USD",
                 cache_file="exchange_rates.json", cache_expiry=3600,
                 max_retries=3, retry_delay=2):
        self.api_url = api_url
        self.cache_file = cache_file
        self.cache_expiry = cache_expiry
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = self._setup_logger()
        self.rates = self._get_rates()

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _load_from_cache(self):
        if not os.path.exists(self.cache_file):
            return None
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                if time.time() - data['timestamp'] < self.cache_expiry:
                    return data['rates']
        except (json.JSONDecodeError, KeyError, IOError) as e:
            self.logger.warning(f"Cache load failed: {e}")
            return None

    def _save_to_cache(self, rates):
        try:
            data = {'timestamp': time.time(), 'rates': rates}
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
        except IOError as e:
            self.logger.error(f"Cache save failed: {e}")

    def _fetch_rates(self):
        for attempt in range(self.max_retries):
            try:
                response = requests.get(self.api_url, timeout=10)
                response.raise_for_status()
                return response.json().get('rates')
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decode error: {e}")
        return None

    def _get_rates(self):
        rates = self._load_from_cache()
        if rates:
            self.logger.info("Rates loaded from cache")
            return rates

        self.logger.info("Fetching rates from API")
        rates = self._fetch_rates()
        if rates:
            self._save_to_cache(rates)
            return rates

        self.logger.error("Failed to fetch rates")
        return {}

    def convert(self, target_currency, amount):
        if not self.rates:
            raise ValueError("Exchange rates not available")

        rate = self.rates.get(target_currency)
        if rate is None:
            raise ValueError(f"Currency {target_currency} not supported")

        return round(amount * rate, 2)