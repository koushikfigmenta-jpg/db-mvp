"""
Brand Intelligence API - FastAPI Backend with Supabase Integration
====================================================================
Production-ready API for brand discovery, content tracking, and intelligence signals.

Features:
- RESTful v1 API with advanced filtering
- CORS enabled for frontend integration
- Supabase integration for all tables
- Type-safe Pydantic models
- Pagination with metadata
- Advanced brand discovery with multi-parameter filtering
- Signal feed with time-based filtering
- Content feed with platform/type filtering
- Many-to-many signal-content relationships
- Website snapshots with creative identity data

Environment Variables:
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_KEY - Your Supabase anon/public key
    FRONTEND_URL - Your frontend URL (for CORS)
"""

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: supabase not installed. Run: pip install supabase")
    exit(1)


# =============================================================================
# ENVIRONMENT HANDLING (LOCAL & PRODUCTION)
# =============================================================================

def is_production():
    """Check if running in production (Vercel)."""
    return os.environ.get("VERCEL_ENV") == "production" or os.environ.get("RAILWAY_ENVIRONMENT") == "production"

def get_allowed_origins():
    """Get CORS allowed origins based on environment."""
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    origins = [url.strip() for url in frontend_url.split(",")]
    
    if not is_production():
        origins.extend(["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"])
    
    return origins

# =============================================================================
# SUPABASE INITIALIZATION
# =============================================================================

def get_supabase_client() -> Client:
    """Initialize Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY environment variables required")
    
    return create_client(url, key)


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class BrandCreate(BaseModel):
    """Create brand."""
    name: str
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    market: Optional[str] = None
    tier: Optional[str] = None
    aesthetic: Optional[List[str]] = None


class BrandResponse(BrandCreate):
    """Brand response."""
    id: str
    created_at: datetime


class BrandDetailResponse(BrandResponse):
    """Brand detail with optional related data."""
    content: Optional[List[Dict[str, Any]]] = None
    signals: Optional[List[Dict[str, Any]]] = None


class ContentMediaCreate(BaseModel):
    """Create content media."""
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_sec: Optional[int] = None


class ContentCreate(BaseModel):
    """Create content from scraper."""
    brand_id: str
    platform: str
    content_type: Optional[str] = None
    url: str
    caption: Optional[str] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    tagged_users: Optional[List[str]] = None
    created_at: datetime
    media: Optional[List[ContentMediaCreate]] = None


class ContentResponse(BaseModel):
    """Content response."""
    id: str
    brand_id: str
    platform: str
    content_type: Optional[str]
    url: str
    caption: Optional[str]
    hashtags: Optional[List[str]]
    mentions: Optional[List[str]]
    tagged_users: Optional[List[str]]
    created_at: datetime
    inserted_at: datetime


class ContentMetricsCreate(BaseModel):
    """Update content metrics."""
    likes: int
    comments: int
    views: Optional[int] = None


class ContentMetricsResponse(BaseModel):
    """Content metrics response."""
    id: str
    content_id: str
    likes: int
    comments: int
    views: Optional[int]
    collected_at: datetime


class SignalCreate(BaseModel):
    """Create signal with optional content associations."""
    brand_id: str
    signal_type: str
    confidence: float
    reason: Optional[str] = None
    detected_at: datetime
    content_ids: Optional[List[str]] = None


class SignalResponse(SignalCreate):
    """Signal response."""
    id: str
    created_at: datetime


class WebsiteSnapshotCreate(BaseModel):
    """Create website snapshot."""
    brand_id: str
    page_url: str
    captured_at: datetime
    visual_identity: Optional[dict] = None
    typography: Optional[dict] = None
    messaging: Optional[dict] = None
    navigation: Optional[dict] = None
    screenshots: Optional[dict] = None
    stats: Optional[dict] = None


class WebsiteSnapshotResponse(WebsiteSnapshotCreate):
    """Website snapshot response."""
    id: str
    created_at: datetime


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    total: int
    limit: int
    offset: int


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="Brand Intelligence API",
    description="Advanced API for brand discovery, content tracking, and intelligence signals",
    version="1.0.0"
)

# CORS Configuration for frontend
allowed_origins = os.environ.get("FRONTEND_URL", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "Brand Intelligence API",
        "timestamp": datetime.now().isoformat()
    }


# =============================================================================
# BRAND DISCOVERY ENDPOINTS (v1)
# =============================================================================

@app.post("/v1/brands", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(brand: BrandCreate):
    """Create a new brand."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("brands").insert({
            "name": brand.name,
            "logo_url": brand.logo_url,
            "industry": brand.industry,
            "market": brand.market,
            "tier": brand.tier,
            "aesthetic": brand.aesthetic,
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create brand")
        
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/brands")
async def list_brands(
    industry: Optional[str] = Query(None),
    market: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    aesthetic: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    ids: Optional[List[str]] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Advanced brand discovery with filtering.
    
    Query Parameters:
    - industry: Filter by industry
    - market: Filter by market/region
    - tier: Filter by tier (luxury, premium, standard)
    - aesthetic: Filter by aesthetic tag
    - search: Keyword search on brand name
    - ids: Get specific brands by IDs (watchlist support)
    - limit: Results per page (1-100)
    - offset: Pagination offset
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("brands").select("*")
        
        if ids:
            query = query.in_("id", ids)
        
        if search:
            query = query.ilike("name", f"%{search}%")
        
        if industry:
            query = query.eq("industry", industry)
        
        if market:
            query = query.eq("market", market)
        
        if tier:
            query = query.eq("tier", tier)
        
        if aesthetic:
            query = query.cs("aesthetic", json.dumps([aesthetic]))
        
        query = query.range(offset, offset + limit - 1).order("created_at", desc=True)
        response = query.execute()
        
        total_response = supabase.table("brands").select("*", count="exact").execute()
        total = total_response.count if hasattr(total_response, 'count') else len(total_response.data) if total_response.data else 0
        
        return {
            "data": response.data,
            "meta": {
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/brands/{brand_id}", response_model=BrandDetailResponse)
async def get_brand_detail(
    brand_id: str,
    include: Optional[str] = Query(None)
):
    """
    Get brand profile detail with optional related data.
    
    Query Parameters:
    - include: Comma-separated list (content, signals)
    
    Example: GET /v1/brands/brand-id?include=content,signals
    """
    try:
        supabase = get_supabase_client()
        
        brand_response = supabase.table("brands").select("*").eq("id", brand_id).execute()
        
        if not brand_response.data:
            raise HTTPException(status_code=404, detail="Brand not found")
        
        brand = brand_response.data[0]
        
        if include:
            includes = [i.strip() for i in include.split(",")]
            
            if "content" in includes:
                content_response = supabase.table("content").select("*").eq(
                    "brand_id", brand_id
                ).order("created_at", desc=True).limit(10).execute()
                brand["content"] = content_response.data
            
            if "signals" in includes:
                signals_response = supabase.table("signals").select("*").eq(
                    "brand_id", brand_id
                ).order("detected_at", desc=True).limit(10).execute()
                brand["signals"] = signals_response.data
        
        return brand
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# INTELLIGENCE SIGNALS ENDPOINTS (v1)
# =============================================================================

@app.post("/v1/signals", response_model=SignalResponse, status_code=status.HTTP_201_CREATED)
async def create_signal(signal: SignalCreate):
    """Create a signal with optional content associations."""
    try:
        supabase = get_supabase_client()
        
        signal_response = supabase.table("signals").insert({
            "brand_id": signal.brand_id,
            "signal_type": signal.signal_type,
            "confidence": signal.confidence,
            "reason": signal.reason,
            "detected_at": signal.detected_at.isoformat(),
        }).execute()
        
        if not signal_response.data:
            raise HTTPException(status_code=400, detail="Failed to create signal")
        
        signal_id = signal_response.data[0]["id"]
        
        if signal.content_ids:
            for content_id in signal.content_ids:
                supabase.table("signal_content").insert({
                    "signal_id": signal_id,
                    "content_id": content_id,
                }).execute()
        
        return signal_response.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/signals")
async def get_signals(
    signal_type: Optional[str] = Query(None),
    brand_id: Optional[str] = Query(None),
    since: Optional[datetime] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get intelligence signals feed with advanced filtering.
    
    Query Parameters:
    - signal_type: Filter by type (launch, style_shift, overperformance, etc.)
    - brand_id: Filter by specific brand
    - since: Get signals detected after this timestamp (for alerts)
    - limit: Results per page (1-100)
    - offset: Pagination offset
    
    Example: GET /v1/signals?since=2023-10-24T00:00:00Z&signal_type=launch
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("signals").select("*")
        
        if signal_type:
            query = query.eq("signal_type", signal_type)
        
        if brand_id:
            query = query.eq("brand_id", brand_id)
        
        if since:
            query = query.gte("detected_at", since.isoformat())
        
        query = query.order("detected_at", desc=True).range(offset, offset + limit - 1)
        response = query.execute()
        
        total_response = supabase.table("signals").select("*", count="exact").execute()
        total = total_response.count if hasattr(total_response, 'count') else len(total_response.data) if total_response.data else 0
        
        return {
            "data": response.data,
            "meta": {
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/brands/{brand_id}/signals")
async def get_brand_signals(brand_id: str):
    """Get all signals for a brand."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("signals").select("*").eq(
            "brand_id", brand_id
        ).order("detected_at", desc=True).execute()
        
        return {
            "brand_id": brand_id,
            "signals": response.data,
            "count": len(response.data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CONTENT ENDPOINTS (v1)
# =============================================================================

@app.post("/v1/content", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(content: ContentCreate):
    """Create content from scraper."""
    try:
        supabase = get_supabase_client()
        
        content_data = {
            "brand_id": content.brand_id,
            "platform": content.platform,
            "content_type": content.content_type,
            "url": content.url,
            "caption": content.caption,
            "hashtags": content.hashtags,
            "mentions": content.mentions,
            "tagged_users": content.tagged_users,
            "created_at": content.created_at.isoformat(),
        }
        
        response = supabase.table("content").insert(content_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create content")
        
        content_id = response.data[0]["id"]
        
        if content.media:
            for media in content.media:
                supabase.table("content_media").insert({
                    "content_id": content_id,
                    "image_url": media.image_url,
                    "video_url": media.video_url,
                    "width": media.width,
                    "height": media.height,
                    "duration_sec": media.duration_sec,
                }).execute()
        
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/content/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str):
    """Get content by ID."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("content").select("*").eq("id", content_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/brands/{brand_id}/content")
async def get_brand_content(
    brand_id: str,
    platform: Optional[str] = Query(None),
    content_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get brand's content feed with filtering.
    
    Query Parameters:
    - platform: Filter by platform (instagram, tiktok)
    - content_type: Filter by type (post, reel, video, etc.)
    - limit: Results per page
    - offset: Pagination offset
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("content").select("*").eq("brand_id", brand_id)
        
        if platform:
            query = query.eq("platform", platform)
        
        if content_type:
            query = query.eq("content_type", content_type)
        
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)
        response = query.execute()
        
        total_response = supabase.table("content").select("*", count="exact").eq(
            "brand_id", brand_id
        ).execute()
        total = total_response.count if hasattr(total_response, 'count') else len(total_response.data) if total_response.data else 0
        
        return {
            "brand_id": brand_id,
            "data": response.data,
            "meta": {
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/content/{content_id}/media")
async def get_content_media(content_id: str):
    """Get media for content."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("content_media").select("*").eq(
            "content_id", content_id
        ).execute()
        
        return {
            "content_id": content_id,
            "media": response.data,
            "count": len(response.data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# CONTENT METRICS ENDPOINTS (v1)
# =============================================================================

@app.post("/v1/content/{content_id}/metrics", status_code=status.HTTP_201_CREATED)
async def create_metrics(content_id: str, metrics: ContentMetricsCreate):
    """Create or update content metrics."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("content_metrics").insert({
            "content_id": content_id,
            "likes": metrics.likes,
            "comments": metrics.comments,
            "views": metrics.views,
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create metrics")
        
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/content/{content_id}/metrics")
async def get_metrics(content_id: str):
    """Get all metrics for content."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("content_metrics").select("*").eq(
            "content_id", content_id
        ).order("collected_at", desc=True).execute()
        
        return {
            "content_id": content_id,
            "metrics": response.data,
            "count": len(response.data)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# WEBSITE SNAPSHOTS ENDPOINTS (v1)
# =============================================================================

@app.post("/v1/website-snapshots", response_model=WebsiteSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def create_snapshot(snapshot: WebsiteSnapshotCreate):
    """Create website snapshot."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("website_snapshots").insert({
            "brand_id": snapshot.brand_id,
            "page_url": snapshot.page_url,
            "captured_at": snapshot.captured_at.isoformat(),
            "visual_identity": snapshot.visual_identity or {},
            "typography": snapshot.typography or {},
            "messaging": snapshot.messaging or {},
            "navigation": snapshot.navigation or {},
            "screenshots": snapshot.screenshots or {},
            "stats": snapshot.stats or {},
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create snapshot")
        
        return response.data[0]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/brands/{brand_id}/snapshots")
async def get_brand_latest_snapshot(brand_id: str):
    """Get latest website snapshot for a brand."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.table("website_snapshots").select("*").eq(
            "brand_id", brand_id
        ).order("captured_at", desc=True).limit(1).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="No snapshots found")
        
        return {
            "brand_id": brand_id,
            "snapshot": response.data[0]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)