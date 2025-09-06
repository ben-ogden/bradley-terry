"""
Configuration settings for the Bradley-Terry model hockey statistics system.
"""

# Web scraping configuration
DIVISION_ID = 3659
TEAM_ID = 140689
BASE_URL = 'https://gamesheetstats.com/seasons/{}/teams/{}/standings'

# Chrome driver options
CHROME_OPTIONS = {
    'headless': True,
    'disable_gpu': True,
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
    'disable_extensions': True,
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
}

# KRACH algorithm parameters
KRACH_ALPHA = 0.85
KRACH_SCALING_FACTOR = 10000 * 10000
KRACH_MAX_ITERATIONS = 200
KRACH_CONVERGENCE_THRESHOLD = 0.00001

# Web scraping delays (seconds)
REQUEST_DELAY = 2
PAGE_LOAD_TIMEOUT = 30

# File paths
TEAM_RESULTS_FILE = 'team_results.pkl'
