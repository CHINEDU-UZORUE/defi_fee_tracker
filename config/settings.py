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
    }
  
}

# API Keys (loaded from environment)
API_KEYS = {
    'coingecko': os.getenv('COINGECKO_API_KEY'),
    'helius': os.getenv('HELIUS_API_KEY')
}

# App Settings
APP_CONFIG = {
    'cache_ttl_hours': int(os.getenv('CACHE_TTL_HOURS', 24)),
    'debug': os.getenv('DEBUG', 'False').lower() == 'true',
    'max_api_retries': 3,
    'request_timeout': 30
}


# # Solana protocol tokens
# SOLANA_PROTOCOL_TOKENS = {
#     # DeFi Protocols
#     "Jupiter (JUP)": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
#     "Marinade (MNDE)": "MNDEFzGvMt87ueuHvVU9VcTqsAP5b3fTGPsHuuPA5ey",
#     "Raydium (RAY)": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
#     "Orca (ORCA)": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
#     "Serum (SRM)": "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt",
#     "Saber (SBR)": "Saber2gLauYim4Mvftnrasomsv6NvAuncvMEZwcLpD1",
#     "Drift (DRIFT)": "DriFtupJYLTosbwoN8koMbEYSx54aFAVLddWsbksjwg7",
#     "Mango (MNGO)": "MangoCzJ36AjZyKwVj3VnYU4GTonjfVEnJmvvWaxLac",
#     # Infrastructure & Tools
#     "Pyth (PYTH)": "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",
#     "Helium (HNT)": "hntyVP6YFm1Hg25TN9WGLqM12b8TQmcknKrdu1oxWux",
#     "Jito (JTO)": "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",
#     "Bonk (BONK)": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
#     # Gaming & NFTs
#     "Star Atlas (ATLAS)": "ATLASXmbPQxBUYbxPsV97usA3fPQYEqzQBUHgiFCUsXx",
#     "Star Atlas DAO (POLIS)": "poLisWXnNRwC6oBu1vHiuKQzFjGL4XDSu4g9qjz9qVk",
#     "Step Finance (STEP)": "StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT",
#     # Staking & Liquid Staking
#     "Lido (stSOL)": "7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj",
#     "Marinade Staked SOL (mSOL)": "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
# }



