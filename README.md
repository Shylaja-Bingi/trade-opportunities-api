# Trade Opportunities API

A FastAPI service that analyzes market data and provides trade opportunity insights for specific sectors in India.

## Features

- **Single Endpoint**: GET `/analyze/{sector}` for market analysis
- **AI-Powered Analysis**: Uses Google Gemini API for intelligent insights
- **Real-time Data**: Web search integration for current market information
- **Security**: JWT authentication and rate limiting
- **Markdown Reports**: Structured, downloadable analysis reports
- **API Documentation**: Auto-generated Swagger UI at `/docs`

## Quick Start

### 1. Installation
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt