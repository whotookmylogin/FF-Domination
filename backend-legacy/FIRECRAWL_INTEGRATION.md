# Firecrawl Integration for ESPN API Fallback

## Overview

This document explains how to set up and use the Firecrawl integration as a fallback mechanism for ESPN API data extraction when the official ESPN API is unavailable.

As of 2025, ESPN has implemented new access restrictions that prevent API access even with valid cookies. This affects many users of the ESPN fantasy API. The Firecrawl integration provides a backup solution using web scraping to extract data from ESPN's public pages.

## Prerequisites

1. A Firecrawl API key (available from [firecrawl.dev](https://firecrawl.dev))
2. The Firecrawl Python SDK installed (`pip install firecrawl-py`)
3. Valid ESPN credentials (espn_s2 cookie and SWID)

## Setup Instructions

### 1. Get a Firecrawl API Key

1. Visit [firecrawl.dev](https://firecrawl.dev)
2. Sign up for an account
3. Get your API key from the dashboard

### 2. Configure Environment Variables

Update your `.env` file in the `backend/` directory:

```env
# ESPN credentials
ESPN_COOKIE=your_espn_s2_cookie_here

# Firecrawl API key
FIRECRAWL_API_KEY=your_actual_firecrawl_api_key_here
```

Replace `your_actual_firecrawl_api_key_here` with your actual Firecrawl API key.

### 3. Install Dependencies

Make sure the Firecrawl Python SDK is installed:

```bash
pip install firecrawl-py
```

## How It Works

The fallback mechanism is implemented in the `PlatformIntegrationService` class:

1. When an ESPN API request is made, the service first attempts to use the official ESPN API
2. If the ESPN API returns an error or non-JSON response, the service logs a warning
3. The service then automatically attempts to use Firecrawl as a fallback
4. If Firecrawl is enabled and successfully extracts data, that data is returned
5. If both ESPN API and Firecrawl fail, the service returns None

## Testing the Integration

Run the test script to verify the Firecrawl integration:

```bash
python test_firecrawl_fallback.py
```

The script will show whether Firecrawl is enabled and whether it can successfully extract data as a fallback.

## Data Extraction Logic

The `ESPNFirecrawlIntegration` class includes placeholder methods for extracting structured data from scraped ESPN pages:

- `get_roster_data()`: Extracts team and player roster information
- `get_transactions_data()`: Extracts league transaction data
- `get_user_data()`: Extracts user profile information

The current implementation includes placeholder data structures. To make the integration fully functional, you would need to implement actual data extraction logic in the `_extract_data_from_markdown()` method using regex or NLP techniques to parse the scraped content.

## Limitations

1. **Rate Limits**: Firecrawl has rate limits that may affect data extraction speed
2. **Data Structure**: Scraped data may not have the same structure as the ESPN API
3. **Reliability**: Web scraping is less reliable than API access and may break if ESPN changes their page structure
4. **Cost**: Firecrawl may have usage-based pricing that could add costs

## Monitoring and Maintenance

1. Monitor the ESPN API community for updates or fixes
2. Check if ESPN releases official API documentation
3. Update the data extraction logic if ESPN changes their page structure
4. Monitor Firecrawl usage and costs

## Troubleshooting

### Firecrawl Integration Disabled

If the Firecrawl integration shows as disabled:

1. Verify that `FIRECRAWL_API_KEY` is set in your `.env` file
2. Ensure the API key is valid and not the placeholder value
3. Check that `firecrawl-py` is installed: `pip install firecrawl-py`

### Data Extraction Fails

If Firecrawl is enabled but data extraction fails:

1. Check the Firecrawl dashboard for error logs
2. Verify that the ESPN URLs being scraped are correct
3. Update the data extraction logic in `_extract_data_from_markdown()`

## Future Improvements

1. Implement more sophisticated data extraction logic using NLP
2. Add caching to reduce Firecrawl API usage
3. Implement retry logic for transient scraping failures
4. Add support for more ESPN data types
5. Implement better error handling and logging
