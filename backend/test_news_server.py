#!/usr/bin/env python3
"""
Minimal test server for news endpoint
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.news.service import NewsAggregationService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="News Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize news service
perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
logger.info(f"Perplexity API key: {'Configured' if perplexity_api_key else 'Not configured'}")

news_service = NewsAggregationService(
    rotowire_api_key=None,
    perplexity_api_key=perplexity_api_key
)

@app.get("/")
def root():
    return {"message": "News Test Server Running"}

@app.get("/news/aggregated")
def get_aggregated_news():
    """Get aggregated news from all sources"""
    try:
        logger.info("Starting news aggregation...")
        news_items = news_service.aggregate_news()
        logger.info(f"Aggregation complete: {len(news_items)} items")
        
        return {
            "status": "success",
            "count": len(news_items),
            "data": news_items
        }
    except Exception as e:
        logger.error(f"Error in news aggregation: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)