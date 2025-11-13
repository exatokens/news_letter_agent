from langchain_core.tools import tool
from newsdataapi import NewsDataApiClient
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)


class NewsTools:
    """Collection of news-related tools"""

    @staticmethod
    @tool
    def fetch_news(
            query: str,
            country: Optional[str] = None,
            category: Optional[str] = None,
            language: str = "en"
    ) -> str:
        """
        Fetch news articles from NewsDataAPI based on search criteria.

        Args:
            query: Search query for news (e.g., "artificial intelligence", "climate change")
            country: ISO country code (e.g., "us", "gb", "in"). Optional.
            category: News category (e.g., "business", "technology", "science", "sports"). Optional.
            language: Language code (default: "en")

        Returns:
            JSON string containing news articles with title, description, content, link, source, etc.
        """
        from config.settings import settings

        try:
            logger.info(f"Fetching news: query='{query}', country={country}, category={category}")
            
            # import pdb;pdb.set_trace()
            # Initialize API client
            api = NewsDataApiClient(apikey=settings.NEWSDATA_API_KEY)

            # Build request parameters
            params = {
                "q": query,
                "language": language
            }

            if country:
                params["country"] = country
            if category:
                params["category"] = category

            # Fetch news
            response = api.news_api(**params)

            # Extract and structure articles
            articles = []
            for article in response.get("results", [])[:settings.MAX_ARTICLES_PER_FETCH]:
                structured_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "link": article.get("link", ""),
                    "source_id": article.get("source_id", ""),
                    "source_name": article.get("source_name", ""),
                    "pub_date": article.get("pubDate", ""),
                    "image_url": article.get("image_url", ""),
                    "keywords": article.get("keywords", []),
                    "category": article.get("category", []),
                }
                articles.append(structured_article)

            logger.info(f"Successfully fetched {len(articles)} articles")

            return json.dumps({
                "status": "success",
                "count": len(articles),
                "articles": articles,
                "query_params": params
            }, indent=2)

        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return json.dumps({
                "status": "error",
                "error": str(e),
                "error_type": type(e).__name__
            })


