import requests
from django.core.cache import cache
from django.conf import settings

CURRENCY_TO_SYMBOL_MAPPING = {
    'NPR':'Rs',
    'USD':'$',
    'EUR':'€'
}

API_KEY = settings.EXCHANGE_RATE_API_KEY
BASE_CURRENCY = 'NPR'

def get_exchange_rate(target_currency):
    cache_key = f'exchange_rate_{BASE_CURRENCY}_{target_currency}'
    rate = cache.get(cache_key)

    if rate is not None:
        return rate

    url = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{BASE_CURRENCY}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # print(data,'data')
        rates = data.get('conversion_rates', {})
        rate = rates.get(target_currency)
        if rate:
            cache.set(cache_key, rate, timeout=60 * 60)  
            return rate
    return 1.0 
