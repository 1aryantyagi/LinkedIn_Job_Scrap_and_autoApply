from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio

# Import your scraper
from jobs import LinkedInPostScraperPlaywright

app = FastAPI(
    title="LinkedIn Job Scraper API",
    version="1.0.0",
    description="API for scraping LinkedIn job posts based on keywords"
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ MODELS ------------------
class ScrapeRequest(BaseModel):
    input_keyword: str
    target_posts: int = 50
    headless: bool = True

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    total_posts: int
    links: List[str]
    timestamp: str
    keyword: str
    csv_filename: Optional[str] = None
    json_filename: Optional[str] = None

# ------------------ STORAGE ------------------
scraping_results: Dict[str, Any] = {}
scraping_status: Dict[str, str] = {}

# ------------------ ROUTES ------------------
@app.get("/")
async def root():
    return {
        "message": "LinkedIn Job Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "POST /scrape": "Start scraping job posts",
            "GET /results/{keyword}": "Get scraping results",
            "GET /status/{keyword}": "Check scraping status",
            "GET /health": "Health check"
        }
    }

@app.post("/scrape")
async def scrape_linkedin_jobs(request: ScrapeRequest, background_tasks: BackgroundTasks):
    keyword = request.input_keyword.lower().strip()

    if keyword in scraping_status and scraping_status[keyword] == "in_progress":
        return {
            "success": False,
            "message": f"Scraping already in progress for keyword: {keyword}",
            "status": "in_progress"
        }

    scraping_status[keyword] = "in_progress"
    background_tasks.add_task(run_scraping_task, request)

    return {
        "success": True,
        "message": f"Scraping started for keyword: {keyword}",
        "status": "in_progress",
        "keyword": keyword,
        "target_posts": request.target_posts
    }

async def run_scraping_task(request: ScrapeRequest):
    keyword = request.input_keyword.lower().strip()

    try:
        logger.info(f"Starting scraping for keyword: {keyword}")

        EMAIL = "mathsfodnahai@gmail.com"
        PASSWORD = "Anjaliandanuj19"
        HASHTAGS = [request.input_keyword + " hiring"]

        scraper = LinkedInPostScraperPlaywright(
            EMAIL, PASSWORD, headless=request.headless
        )
        collected_links = await scraper.run_scraping(
            hashtags=HASHTAGS,
            target_posts=request.target_posts,
            save_format="both"   # will auto-save CSV + JSON
        )

        timestamp = datetime.now().isoformat()
        csv_filename = "linkedin_posts_playwright.csv"
        json_filename = "linkedin_posts_playwright.json"

        scraping_results[keyword] = {
            "success": True,
            "links": collected_links,
            "total_posts": len(collected_links),
            "timestamp": timestamp,
            "keyword": request.input_keyword,
            "csv_filename": csv_filename,
            "json_filename": json_filename
        }

        scraping_status[keyword] = "completed"
        logger.info(f"Scraping completed for keyword: {keyword}. Found {len(collected_links)} posts")

    except Exception as e:
        logger.error(f"Scraping failed for keyword {keyword}: {str(e)}")
        scraping_results[keyword] = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "keyword": request.input_keyword
        }
        scraping_status[keyword] = "failed"

@app.get("/status/{keyword}")
async def get_scraping_status(keyword: str):
    keyword = keyword.lower().strip()
    status = scraping_status.get(keyword, "not_found")
    return {"keyword": keyword, "status": status, "timestamp": datetime.now().isoformat()}

@app.get("/results/{keyword}")
async def get_results(keyword: str):
    keyword = keyword.lower().strip()

    if keyword not in scraping_results:
        raise HTTPException(status_code=404, detail=f"No results found for {keyword}. Start scraping first.")

    result = scraping_results[keyword]
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=f"Scraping failed: {result.get('error', 'Unknown error')}")
    return result

@app.get("/results")
async def get_all_results():
    return {"total_keywords": len(scraping_results), "results": scraping_results}

@app.delete("/results/{keyword}")
async def delete_results(keyword: str):
    keyword = keyword.lower().strip()
    scraping_results.pop(keyword, None)
    scraping_status.pop(keyword, None)
    return {"message": f"Results deleted for keyword: {keyword}"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_scraping_tasks": len([k for k,v in scraping_status.items() if v=="in_progress"]),
        "total_results": len(scraping_results)
    }

@app.get("/keywords")
async def get_keywords():
    return {"keywords": list(scraping_results.keys()), "count": len(scraping_results)}

# ------------------ RUN ------------------
if __name__ == "__main__":
    import uvicorn
    print("Starting LinkedIn Scraper API at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)