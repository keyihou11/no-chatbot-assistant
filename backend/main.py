"""FastAPI backend server for No-Chatbot."""
import logging
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from models import AnalyzeRequest, AnalyzeResponse, Issue, FixSuggestion
from analyzer import PylintAnalyzer
from llm_client import LLMClient
from patch_generator import PatchGenerator

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="No-Chatbot Backend", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = PylintAnalyzer()
llm_client = LLMClient()
patch_gen = PatchGenerator()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "no-chatbot-backend"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: AnalyzeRequest):
    """
    Analyze Python code and generate fix suggestions.
    
    Args:
        request: AnalyzeRequest containing code content and metadata
        
    Returns:
        AnalyzeResponse with issues and fix suggestions
    """
    logger.info(f"Analyzing code from {request.file_path}")
    
    try:
        # Run Pylint analysis
        raw_issues = analyzer.analyze(request.code_content, request.file_path)
        
        # Generate fix suggestions for each issue using LLM
        issues = []
        for raw_issue in raw_issues[:5]:  # Limit to 5 issues for MVP
            issue = Issue(**raw_issue)
            
            # Generate fix suggestion from LLM
            try:
                fix_data = llm_client.generate_fix(
                    code_snippet=request.code_content,
                    line=issue.line,
                    message=issue.message,
                    rule_id=issue.rule_id
                )
                
                if fix_data:
                    logger.debug(f"AI fix for line {issue.line}: {json.dumps(fix_data, indent=2)}")
                    issue.fix = FixSuggestion(**fix_data)
                    logger.info(f"Generated fix for issue at line {issue.line}")
                else:
                    logger.warning(f"LLM returned None for issue at line {issue.line}")
                
            except Exception as e:
                logger.warning(f"Failed to generate fix for issue at line {issue.line}: {e}")
            
            issues.append(issue)
        
        logger.info(f"Analysis complete: {len(issues)} issues with fixes")
        
        return AnalyzeResponse(issues=issues, analyzed_with="pylint")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Detailed health check."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = None
    
    if provider == "openai":
        model = os.getenv("OPENAI_MODEL", "gpt-4")
    elif provider == "claude":
        model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    elif provider == "google":
        model = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
    
    return {
        "status": "healthy",
        "services": {
            "analyzer": "pylint",
            "llm_provider": provider,
            "llm_model": model
        }
    }


if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "localhost")
    
    logger.info(f"Starting No-Chatbot backend on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
