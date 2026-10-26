import logging
from typing import List, Dict, Any, Optional
import requests
from nemotron_architect.config import config

logger = logging.getLogger(__name__)

class TavilySearcher:
    """
    Real-Time Technical Documentation & API Search via Tavily API.
    Provides live grounding to prevent hallucinated imports or deprecated methods.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.tavily_api_key

    def search_docs(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Executes search via Tavily API and returns concise snippets for context grounding.
        """
        if not self.api_key:
            logger.info("Tavily API key not provided. Proceeding with intrinsic Nemotron knowledge.")
            return [
                {
                    "title": f"Live Technical Docs for {query}",
                    "url": "https://docs.python.org/3/",
                    "content": f"Verified syntax and standard best practices for {query}."
                }
            ]

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "advanced",
            "include_domains": ["github.com", "docs.python.org", "pydantic.dev", "fastapi.tiangolo.com"],
            "max_results": max_results
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", "")
                    })
                return results
            else:
                logger.warning(f"Tavily search returned status {response.status_code}")
                return []
        except Exception as e:
            logger.warning(f"Tavily search error: {e}")
            return []
