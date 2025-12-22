import google.generativeai as genai
from typing import List, Dict, Any
from app.models import MarketData, TradeOpportunity, AnalysisResponse
from app.config import settings
import json
from datetime import datetime

def initialize_gemini():
    """Initialize Gemini API"""
    if settings.gemini_api_key:
        genai.configure(api_key=settings.gemini_api_key)
        return True
    return False

def analyze_with_gemini(sector: str, market_data: List[MarketData]) -> Dict[str, Any]:
    """
    Use Gemini API to analyze market data and generate insights
    """
    if not initialize_gemini():
        return generate_mock_analysis(sector, market_data)
    
    try:
        # Prepare prompt for Gemini
        prompt = f"""
        Analyze the following market data for the {sector} sector in India and provide:
        1. A brief summary of current market conditions
        2. 3-5 key market trends
        3. 3-5 specific trade opportunities with reasoning, risk level (low/medium/high), and time horizon
        4. 3-5 potential risks
        
        Market Data:
        {json.dumps([item.dict() for item in market_data], indent=2)}
        
        Respond in JSON format with this structure:
        {{
            "summary": "string",
            "market_trends": ["trend1", "trend2", ...],
            "trade_opportunities": [
                {{
                    "opportunity": "string",
                    "reasoning": "string",
                    "risk_level": "low/medium/high",
                    "time_horizon": "short/medium/long-term"
                }}
            ],
            "risks": ["risk1", "risk2", ...]
        }}
        """
        
        # Use Gemini model
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Parse response (Gemini might return markdown with JSON)
        response_text = response.text
        
        # Extract JSON from response
        if '```json' in response_text:
            json_str = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            json_str = response_text.split('```')[1].split('```')[0]
        else:
            json_str = response_text
        
        analysis = json.loads(json_str)
        
    except Exception as e:
        print(f"Gemini analysis failed: {e}")
        analysis = generate_mock_analysis(sector, market_data)
    
    return analysis

def generate_mock_analysis(sector: str, market_data: List[MarketData]) -> Dict[str, Any]:
    """Generate mock analysis if Gemini fails"""
    return {
        "summary": f"The {sector} sector in India shows promising growth potential with increasing digital adoption and government support.",
        "market_trends": [
            f"Growing demand in {sector} services",
            "Increased foreign investment",
            "Government policy support",
            "Technology integration",
            "Export opportunities"
        ],
        "trade_opportunities": [
            {
                "opportunity": f"Invest in leading {sector} companies",
                "reasoning": "Market leaders showing consistent growth and innovation",
                "risk_level": "medium",
                "time_horizon": "medium-term"
            },
            {
                "opportunity": "Sector-specific ETFs",
                "reasoning": "Diversified exposure with lower risk",
                "risk_level": "low",
                "time_horizon": "long-term"
            }
        ],
        "risks": [
            "Regulatory changes",
            "Market volatility",
            "Global economic factors",
            "Competition intensity"
        ]
    }

def generate_markdown_report(sector: str, analysis: Dict[str, Any], market_data: List[MarketData]) -> str:
    """Generate structured markdown report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    markdown = f"""# Market Analysis Report: {sector.title()} Sector
**Generated:** {timestamp}

## Executive Summary
{analysis.get('summary', '')}

## Market Trends
"""
    
    for trend in analysis.get('market_trends', []):
        markdown += f"- {trend}\n"
    
    markdown += "\n## Key Market Information\n"
    for data in market_data[:5]:  # Show top 5 news items
        markdown += f"### {data.title}\n"
        markdown += f"**Source:** {data.source} | **Date:** {data.date}\n"
        markdown += f"{data.snippet}\n\n"
    
    markdown += "## Trade Opportunities\n"
    for i, opp in enumerate(analysis.get('trade_opportunities', []), 1):
        markdown += f"### Opportunity {i}: {opp.get('opportunity', '')}\n"
        markdown += f"- **Reasoning:** {opp.get('reasoning', '')}\n"
        markdown += f"- **Risk Level:** {opp.get('risk_level', '').title()}\n"
        markdown += f"- **Time Horizon:** {opp.get('time_horizon', '')}\n\n"
    
    markdown += "## Potential Risks\n"
    for risk in analysis.get('risks', []):
        markdown += f"- ⚠️ {risk}\n"
    
    markdown += "\n---\n"
    markdown += "*Report generated by Trade Opportunities API. This is for informational purposes only.*"
    
    return markdown