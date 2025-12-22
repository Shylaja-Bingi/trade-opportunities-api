import httpx
from duckduckgo_search import DDGS
from typing import List
import asyncio
from app.models import MarketData
from app.config import settings

async def search_market_data(sector: str, max_results: int = 10) -> List[MarketData]:
    """
    Search for current market data and news about the sector
    """
    market_data = []
    
    try:
        # Use DuckDuckGo search for market news
        with DDGS() as ddgs:
            query = f"{sector} sector India market news trends 2024 latest updates"
            results = list(ddgs.text(query, max_results=max_results))
            
            for result in results:
                market_data.append(MarketData(
                    title=result.get('title', ''),
                    source=result.get('source', 'Unknown'),
                    snippet=result.get('body', ''),
                    date=result.get('date', 'Recent'),
                    url=result.get('href', '')
                ))
        
        # Additional API calls can be added here for more data sources
        # Example: Financial news APIs, stock market APIs, etc.
        
    except Exception as e:
        # Fallback to static data if search fails
        print(f"Search failed: {e}")
        market_data = get_fallback_data(sector)
    
    return market_data

def get_fallback_data(sector: str) -> List[MarketData]:
    """Provide fallback data if web search fails"""
    fallback_data = {
        "pharmaceuticals": [
            MarketData(
                title="Indian Pharma Sector Growth Outlook 2024",
                source="Industry Report",
                snippet="Indian pharmaceutical sector expected to grow at 8-10% CAGR driven by exports and domestic demand.",
                date="2024",
                url=""
            )
        ],
        "technology": [
            MarketData(
                title="India Tech Sector: AI and Digital Transformation",
                source="Tech Analysis",
                snippet="Technology sector in India seeing increased investment in AI, cloud computing, and digital services.",
                date="2024",
                url=""
            )
        ],
        "agriculture": [
            MarketData(
                title="Agricultural Sector Modernization Trends",
                source="Agri Report",
                snippet="Precision farming and organic exports driving growth in Indian agriculture sector.",
                date="2024",
                url=""
            )
        ]
    }
    
    return fallback_data.get(sector, [
        MarketData(
            title=f"{sector.title()} Sector Analysis",
            source="Market Intelligence",
            snippet=f"Current trends and opportunities in the {sector} sector.",
            date="2024",
            url=""
        )
    ])