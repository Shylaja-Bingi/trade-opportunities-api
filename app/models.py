from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AnalysisRequest(BaseModel):
    sector: str = Field(..., min_length=2, max_length=50)

class MarketData(BaseModel):
    title: str
    source: str
    snippet: str
    date: str
    url: Optional[str] = None

class TradeOpportunity(BaseModel):
    opportunity: str
    reasoning: str
    risk_level: str  # low, medium, high
    time_horizon: str  # short-term, medium-term, long-term

class AnalysisResponse(BaseModel):
    sector: str
    timestamp: str
    summary: str
    market_trends: List[str]
    key_news: List[MarketData]
    trade_opportunities: List[TradeOpportunity]
    risks: List[str]
    markdown_report: str