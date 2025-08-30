"""
LinkedIn Scraper Configuration File

This file contains configurable parameters for the LinkedIn Post Scraper.
Modify these settings as needed for different scraping requirements.
"""

# Login Credentials
LINKEDIN_CREDENTIALS = {
    'email': 'mathsfodnahai@gmail.com',
    'password': 'Anjaliandanuj19'
}

# Hashtags to search for (can be easily modified)
HASHTAG_SETS = {
    'ai_ml_jobs': ['AIMLhiring']
}

# Scraping Parameters
SCRAPING_CONFIG = {
    'target_post_count': 50,
    'max_scroll_attempts': 100,
    'scroll_delay': 5,  # seconds
    'headless_mode': False,  # Set to True for headless browsing
    'timeout_seconds': 15
}

# File Output Settings
OUTPUT_CONFIG = {
    'csv_filename': 'linkedin_posts.csv',
    'json_filename': 'linkedin_posts.json',
    'include_timestamp': True
}

# Date Filter Options
DATE_FILTERS = {
    'past_24h': 'Past 24 hours',
    'past_week': 'Past week',
    'past_month': 'Past month',
    'any_time': 'Any time'
}

# Currently selected configuration
CURRENT_HASHTAGS = HASHTAG_SETS['ai_ml_jobs']  # Change this to use different hashtag sets
CURRENT_DATE_FILTER = 'past_week'  # Change this to use different date filters
