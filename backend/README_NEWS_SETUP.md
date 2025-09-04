# News Feed Configuration

The Fantasy Football app aggregates real-time news from multiple sources to provide comprehensive coverage.

## Current News Sources

### Active Sources (No API Key Required)
- **ESPN**: Uses public API and RSS feeds
- **CBS Sports**: RSS feed integration  
- **Yahoo Sports**: RSS feed integration
- **NFL.com**: RSS feed integration

### Optional Enhanced Sources

#### Perplexity API (Real-time AI Research)
For enhanced, real-time news research and analysis:

1. Get API key from https://www.perplexity.ai/settings/api
2. Add to `.env` file:
```
PERPLEXITY_API_KEY=your_api_key_here
```

Benefits:
- Real-time web search for latest news
- AI-powered relevance filtering
- Player-specific news tracking
- Breaking news detection

#### Firecrawl (Web Scraping)
For direct website scraping when RSS feeds are limited:

1. Get API key from https://www.firecrawl.dev/
2. Add to `.env` file:
```
FIRECRAWL_API_KEY=your_api_key_here
```

## News Endpoints

- `/news/aggregated` - All news from all sources
- `/news/breaking` - High-urgency news only
- `/news/source/{source_name}` - News from specific source
- `/news/personalized/{user_id}` - News relevant to user's team

## Data Quality

The system prioritizes real data sources and only returns empty lists if no data is available. Mock data has been completely removed from production use.

## Monitoring

Check news feed status:
```bash
curl http://localhost:8000/news/stats
```

This shows:
- Active sources
- Items fetched per source
- Last update time
- Any API errors