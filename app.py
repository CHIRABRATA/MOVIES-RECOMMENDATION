import os
import pickle
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any, Tuple

import numpy as np
import pandas as pd
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG_500 = "https://image.tmdb.org/t/p/w500"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = None
indices_obj = None
tfidf_matrix = None
TITLE_TO_IDX = {}

def load_resources():
    global df, indices_obj, tfidf_matrix, TITLE_TO_IDX
    try:
        with open(os.path.join(BASE_DIR, "df.pkl"), "rb") as f:
            df = pickle.load(f)
        with open(os.path.join(BASE_DIR, "indices.pkl"), "rb") as f:
            indices_obj = pickle.load(f)
        with open(os.path.join(BASE_DIR, "tfidf_matrix.pkl"), "rb") as f:
            tfidf_matrix = pickle.load(f)
        
        
        for k, v in indices_obj.items():
            TITLE_TO_IDX[str(k).strip().lower()] = int(v)
        print("✅ Backend Resources Loaded (SciPy Matrix + DF)")
    except Exception as e:
        print(f"❌ Critical Error loading resources: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_resources()
    yield

app = FastAPI(title="Movie Rec API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# HELPER LOGIC
# =========================
async def tmdb_get(path: str, params: dict):
    params["api_key"] = TMDB_API_KEY
    url = f"{TMDB_BASE}{path}"
    
    print(f"\n📡 TMDB Request:")
    print(f"   URL: {url}")
    print(f"   Params: {params}")
    
    try:
        async with httpx.AsyncClient(timeout=10, verify=False) as client:
            r = await client.get(url, params=params)
            print(f"   Status: {r.status_code}")
            
            if r.status_code != 200:
                print(f"   Error Response: {r.text[:300]}")
                raise HTTPException(status_code=502, detail=f"TMDB API returned {r.status_code}")
            
            data = r.json()
            print(f"   Success! Got {len(data.get('results', []))} results")
            return data
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"   Network Error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Cannot reach TMDB API. Network error: {type(e).__name__}")

# =========================
# ENDPOINTS
# =========================
@app.get("/home")
async def home_feed(category: str = "popular"):
    try:
        path = "/trending/movie/day" if category == "trending" else f"/movie/{category}"
        data = await tmdb_get(path, {"language": "en-US"})
        results = data.get("results", [])
        return [{
            "tmdb_id": m.get("id"),
            "title": m.get("title", "Unknown"),
            "poster_url": f"{TMDB_IMG_500}{m['poster_path']}" if m.get('poster_path') else None
        } for m in results[:24]]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Home feed error: {str(e)}")

@app.get("/tmdb/search")
async def search(query: str):
    try:
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
        return await tmdb_get("/search/movie", {"query": query, "language": "en-US"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/movie/id/{tmdb_id}")
async def details(tmdb_id: int):
    try:
        data = await tmdb_get(f"/movie/{tmdb_id}", {"language": "en-US"})
        data["poster_url"] = f"{TMDB_IMG_500}{data.get('poster_path')}" if data.get('poster_path') else None
        data["backdrop_url"] = f"{TMDB_IMG_500}{data.get('backdrop_path')}" if data.get('backdrop_path') else None
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Details error: {str(e)}")

@app.get("/movie/search")
async def recommendation_bundle(query: str):
    # This matches your Streamlit's request for TF-IDF + Genre
    # 1. Get Similarity (TF-IDF)
    recs = []
    q_norm = query.strip().lower()
    if q_norm in TITLE_TO_IDX:
        idx = TITLE_TO_IDX[q_norm]
        qv = tfidf_matrix[idx]
        scores = (tfidf_matrix @ qv.T).toarray().ravel()
        order = np.argsort(-scores)[1:13] # skip self
        for i in order:
            t = df.iloc[i]['title']
            recs.append({"title": t, "score": float(scores[i]), "tmdb": {"tmdb_id": 1, "title": t}})
            
    return {"tfidf_recommendations": recs, "genre_recommendations": []}