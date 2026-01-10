import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Cinematic Recs", page_icon="🎬", layout="wide")

# =============================
# PREMIUM CSS
# =============================
st.markdown("""
<style>
    .stApp { background: #020617; color: #f8fafc; }
    .movie-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    .hero-overlay {
        background: linear-gradient(to right, rgba(2,6,23,1) 30%, rgba(2,6,23,0) 100%);
        padding: 60px;
        border-radius: 20px;
    }
    .movie-title-text { font-size: 0.85rem; font-weight: 600; margin-top: 8px; height: 40px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# =============================
# NAVIGATION
# =============================
if "view" not in st.session_state: st.session_state.view = "home"
if "selected_id" not in st.session_state: st.session_state.selected_id = None

def goto_details(id):
    st.session_state.selected_id = id
    st.session_state.view = "details"
    st.rerun()

# =============================
# UI COMPONENTS
# =============================
def movie_grid(movies, key_prefix):
    if not movies: return st.info("No movies found.")
    cols = st.columns(6)
    for idx, m in enumerate(movies):
        with cols[idx % 6]:
            st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
            if m.get("poster_url"): st.image(m["poster_url"])
            else: st.write("🖼️ No Poster")
            
            if st.button("Details", key=f"{key_prefix}_{m['tmdb_id']}_{idx}"):
                goto_details(m['tmdb_id'])
            st.markdown(f"<div class='movie-title-text'>{m['title']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

# =============================
# VIEWS
# =============================
if st.session_state.view == "home":
    st.title("🎬 Movie Discover")
    search_q = st.text_input("Search movie...", placeholder="Enter title (e.g. Interstellar)")
    
    if search_q:
        try:
            response = requests.get(f"{API_BASE}/tmdb/search", params={"query": search_q}, timeout=5)
            if response.status_code == 200:
                res = response.json()
                results = res.get("results", [])
                processed = [{"tmdb_id": r["id"], "title": r["title"], "poster_url": f"https://image.tmdb.org/t/p/w500{r['poster_path']}" if r.get('poster_path') else None} for r in results]
                movie_grid(processed, "search")
            else:
                st.error(f"Backend Error {response.status_code}: Check your TMDB API Key.")
        except Exception as e:
            st.error(f"Connection Failed: Is the FastAPI server running? {e}")
    else:
        cat = st.radio("Browse By", ["trending", "popular", "top_rated"], horizontal=True)
        try:
            response = requests.get(f"{API_BASE}/home", params={"category": cat}, timeout=5)
            if response.status_code == 200:
                home_data = response.json()
                movie_grid(home_data, "home")
            else:
                st.error(f"Backend Error {response.status_code}: Check your TMDB API Key.")
        except Exception as e:
            st.error(f"Connection Failed: Is the FastAPI server running? {e}")

elif st.session_state.view == "details":
    m_id = st.session_state.selected_id
    try:
        response = requests.get(f"{API_BASE}/movie/id/{m_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
        else:
            st.error(f"Backend Error {response.status_code}: Could not load movie details.")
            if st.button("← Back"):
                st.session_state.view = "home"
                st.rerun()
            st.stop()
    except Exception as e:
        st.error(f"Connection Failed: Is the FastAPI server running? {e}")
        if st.button("← Back"):
            st.session_state.view = "home"
            st.rerun()
        st.stop()

    if st.button("← Back"):
        st.session_state.view = "home"
        st.rerun()

    # HERO HEADER
    st.markdown(f"""
        <div style="background-image: url('{data.get('backdrop_url')}'); background-size: cover; background-position: center; border-radius: 20px; height: 350px;">
            <div class="hero-overlay" style="height: 100%;">
                <h1 style="font-size: 3.5rem; margin: 0;">{data.get('title')}</h1>
                <p style="color: #94a3b8; font-size: 1.2rem;">{data.get('tagline', '')}</p>
                <p>⭐ {data.get('vote_average')} | 📅 {data.get('release_date')}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(data.get("poster_url"), use_column_width=True)
    with c2:
        st.subheader("Storyline")
        st.write(data.get("overview"))
        
        # Recommendation Call
        st.divider()
        st.subheader("🤖 AI Similarity Recommendations")
        # You would call your /movie/search endpoint here to populate a grid