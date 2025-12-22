from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging
from datetime import datetime

from app.config import settings
from app.auth import authenticate_user, create_access_token, get_current_user
from app.models import Token, User, AnalysisRequest, AnalysisResponse, TradeOpportunity
from app.rate_limit import check_rate_limit, rate_limiter
from app.search import search_market_data
from app.analysis import analyze_with_gemini, generate_markdown_report

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trade Opportunities API",
    description="API for market analysis and trade opportunity insights in Indian sectors",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# In-memory session tracking
sessions = {}

# Pydantic model for login
class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
async def root():
    return {
        "message": "Trade Opportunities API",
        "version": "1.0.0",
        "endpoints": {
            "login": "/token",
            "analyze": "/analyze/{sector}",
            "docs": "/docs"
        }
    }

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: LoginRequest):
    """
    Get access token for API authentication
    Example: {"username": "guest", "password": "guest"}
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    # Track session
    sessions[user.username] = {
        "last_login": datetime.now().isoformat(),
        "token": access_token
    }
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/analyze/{sector}", response_model=AnalysisResponse)
async def analyze_sector(
    sector: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze a specific sector and return trade opportunities
    
    - **sector**: Name of the sector to analyze (e.g., pharmaceuticals, technology, agriculture)
    - Returns structured market analysis with trade opportunities
    """
    
    # Input validation
    sector_lower = sector.lower()
    if sector_lower not in settings.allowed_sectors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sector not supported. Allowed sectors: {', '.join(settings.allowed_sectors)}"
        )
    
    # Authentication
    try:
        current_user = await get_current_user(credentials.credentials)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Rate limiting
    user_identifier = f"{current_user.username}_{request.client.host}"
    check_rate_limit(request, user_identifier)
    
    try:
        logger.info(f"Analyzing sector: {sector_lower} for user: {current_user.username}")
        
        # Step 1: Search for market data
        market_data = await search_market_data(sector_lower)
        
        # Step 2: Analyze with AI
        analysis = analyze_with_gemini(sector_lower, market_data)
        
        # Step 3: Generate markdown report
        markdown_report = generate_markdown_report(sector_lower, analysis, market_data)
        
        # Step 4: Prepare response
        response_data = AnalysisResponse(
            sector=sector_lower,
            timestamp=datetime.now().isoformat(),
            summary=analysis.get("summary", ""),
            market_trends=analysis.get("market_trends", []),
            key_news=market_data[:5],  # Top 5 news items
            trade_opportunities=[
                TradeOpportunity(**opp) for opp in analysis.get("trade_opportunities", [])
            ],
            risks=analysis.get("risks", []),
            markdown_report=markdown_report
        )
        
        # Update session
        if current_user.username in sessions:
            sessions[current_user.username]["last_analysis"] = datetime.now().isoformat()
            sessions[current_user.username]["analysis_count"] = \
                sessions[current_user.username].get("analysis_count", 0) + 1
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error analyzing sector {sector}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/analyze/{sector}/markdown", response_class=PlainTextResponse)
async def analyze_sector_markdown(
    sector: str,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get analysis report in markdown format (downloadable .md file)
    """
    analysis = await analyze_sector(sector, request, credentials)
    return PlainTextResponse(
        content=analysis.markdown_report,
        headers={
            "Content-Disposition": f"attachment; filename={sector}_analysis_{datetime.now().strftime('%Y%m%d')}.md"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "rate_limiter_status": "active"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)