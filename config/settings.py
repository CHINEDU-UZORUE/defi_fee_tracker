import os
from dotenv import load_dotenv

# Load environment variables
if os.path.exists('.env'):
    load_dotenv()


# API Configuration (URLs)
API_ENDPOINTS = {
    'coingecko': {
        'base_url': 'https://pro-api.coingecko.com/api/v3',
        'endpoints': {
            'prices': '/simple/price',
            'market_data': '/coins/markets',
            'historical': '/coins/{id}/market_chart'
        }
    },
    'defillama': {
        'base_url': 'https://api.llama.fi',
        'endpoints': {
            'protocols': '/protocols',
            'protocol': '/protocol/{slug}',
            'fees': '/overview/fees',
            'revenue': '/overview/revenue'
        }
    }
  
}

# API Keys (loaded from environment)
API_KEYS = {
    'coingecko': os.getenv('COINGECKO_API_KEY'),
    'helius': os.getenv('HELIUS_API_KEY')
}



