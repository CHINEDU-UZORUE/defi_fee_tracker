import os
from dotenv import load_dotenv

# Load environment variables
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
    },
    'dune': {
        'base_url': 'https://api.dune.com/api/v1',
        'endpoints': {
            'query': '/query/{query_id}/execute',
            'results': '/execution/{execution_id}/results'
        }
    }
}

# API Keys (loaded from environment)
API_KEYS = {
    'coingecko': os.getenv('COINGECKO_API_KEY'),
    'dune': os.getenv('DUNE_API_KEY'),
    'helius': os.getenv('HELIUS_API_KEY')
}

# App Settings
APP_CONFIG = {
    'cache_ttl_hours': int(os.getenv('CACHE_TTL_HOURS', 24)),
    'debug': os.getenv('DEBUG', 'False').lower() == 'true',
    'max_api_retries': 3,
    'request_timeout': 30
}


# Solana Protocol Configuration
SOLANA_PROTOCOLS = {
    'jupiter': {
        'name': 'Jupiter',
        'token_symbol': 'JUP',
        'coingecko_id': 'jupiter-exchange-solana',
        'defillama_slug': 'jupiter',
        'category': 'DEX Aggregator',
        'description': 'Leading DEX aggregator on Solana',
        'has_native_api': True,
        'launch_date': '2024-01-31',
        'mint_address': 'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN'
    },
    'jito': {
        'name': 'Jito',
        'token_symbol': 'JTO',
        'coingecko_id': 'jito-governance-token',
        'defillama_slug': 'jito',
        'category': 'Liquid Staking',
        'description': 'MEV-focused liquid staking protocol',
        'has_native_api': True,
        'launch_date': '2023-12-07',
        'mint_address': 'jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL'
    },
    'meteora': {
        'name': 'Meteora',
        'token_symbol': 'MET',
        'coingecko_id': 'meteora',
        'defillama_slug': 'meteora',
        'category': 'DEX/AMM',
        'description': 'Dynamic liquidity protocol',
        'has_native_api': False,
        'launch_date': '2024-01-20',
        'mint_address': 'METADDFL6wWMqokotz2N6yAYW1e9zSVMQ1p4Q1X2N'
    },
    'raydium': {
        'name': 'Raydium',
        'token_symbol': 'RAY',
        'coingecko_id': 'raydium',
        'defillama_slug': 'raydium',
        'category': 'DEX/AMM',
        'description': 'Leading AMM on Solana integrated with Serum',
        'has_native_api': False,
        'launch_date': '2021-02-21',
        'mint_address': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R'
    },
    'marinade': {
        'name': 'Marinade Finance',
        'token_symbol': 'MNDE',
        'coingecko_id': 'marinade',
        'defillama_slug': 'marinade-finance',
        'category': 'Liquid Staking',
        'description': 'Non-custodial liquid staking protocol',
        'has_native_api': False,
        'launch_date': '2021-08-06',
        'mint_address': 'MNDEFzGvMt87ueuHvVU9VcTqsAP5b3fTGPsHuuPA5ey'
    },
    'kamino': {
        'name': 'Kamino Finance',
        'token_symbol': 'KMNO',
        'coingecko_id': 'kamino',
        'defillama_slug': 'kamino',
        'category': 'Lending',
        'description': 'Automated liquidity and lending protocol',
        'has_native_api': False,
        'launch_date': '2023-11-15',
        'mint_address': 'KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS'
    },
    'orca': {
        'name': 'Orca',
        'token_symbol': 'ORCA',
        'coingecko_id': 'orca',
        'defillama_slug': 'orca',
        'category': 'DEX/AMM',
        'description': 'User-friendly DEX with concentrated liquidity',
        'has_native_api': False,
        'launch_date': '2021-02-20',
        'mint_address': 'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE'
    }
}

# Protocol Categories for Filtering
PROTOCOL_CATEGORIES = {
    'DEX/AMM': ['jupiter', 'meteora', 'raydium', 'orca'],
    'Liquid Staking': ['jito', 'marinade'],
    'Lending': ['kamino']
}

# Cache settings for joblib
CACHE_CONFIG = {
    'cache_dir': 'data/cache',
    'compression': 3,  # 0-9, higher = more compression
    'api_cache_hours': 1,  # Short cache for API responses
    'processed_cache_hours': 24,  # Longer cache for processed data
    'calc_cache_hours': 168  # Weekly cache for calculations
}