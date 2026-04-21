import streamlit as st
from openai import OpenAI
import pystac_client
import planetary_computer as pc
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
import numpy as np
from PIL import Image
import io, base64

st.set_page_config(page_title="NAIP Chat", layout="wide")
st.title("🛰️ Chat with NAIP Imagery — Qwen3-VL")

# ---------- Ollama Cloud Client ----------
client = OpenAI(
    base_url="https://api.ollama.com/v1",
    api_key=st.secrets["OLLAMA_API_KEY"]
)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("📍 Area of Interest")
    lat = st.number_input("Latitude",  value=39.2737, format="%.4f")
    lon = st.number_input("Longitude", value=-76.7316, format="%.4f")
    buf = st.slider("Buffer (degrees)", 0.001, 0.01, 0.003, step=0.001)
    fetch_btn = st.button("🔍 Fetch NAIP Tile")

# ---------- NAIP fetch ----------
def fetch_naip(lat, lon, buf):
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=pc.sign_inplace
    )
    bbox = [lon - buf, lat - buf, lon + buf, lat + buf]
    results = catalog.search(
        collections=["naip"],
        bbox=bbox,
        limit=1,
        sortby="-properties.datetime"
    )
    items = list(results.items())
    if not items:
        raise ValueError("No NAIP tiles found for this location.")

    href = items[0].assets["image"].href
    with rasterio.open(href) as src:
        bounds = transform_bounds("EPSG:4326", src.crs, *bbox)
        window = from_bounds(*bounds, transform=src.transform)
        data = src.read([1, 2, 3], window=window)

    data = np.moveaxis(data, 0, -1)
    data = np.clip(data, 0, 255).astype(np.uint8)
    img = Image.fromarray(data)

    buf_io = io.BytesIO()
    img.save(buf_io, format="PNG")
    buf_io.seek(0)
    b64 = base64.b64encode(buf_io.read()).decode("utf-8")
    return img, b64

# ---------- Session state ----------
if "messages"  not in st.session_state: st.session_state.messages  = []
if "naip_img"  not in st.session_state: st.session_state.naip_img  = None
if "naip_b64"  not in st.session_state: st.session_state.naip_b64  = None

# ---------- Fetch ----------
if fetch_btn:
    with st.spinner("Fetching NAIP from Planetary Computer..."):
        try:
            img, b64 = fetch_naip(lat, lon, buf)
            st.session_state.naip_img = img
            st.session_state.naip_b64 = b64
            st.session_state.messages = []
            st.success(f"Loaded — {img.width}×{img.height} px")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------- Layout ----------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🗺️ NAIP Tile")
    if st.session_state.naip_img:
        st.image(st.session_state.naip_img, width=600)   # fixed deprecation
    else:
        st.info("Enter coordinates and click Fetch.")

with col2:
    st.subheader("💬 Ask Qwen3-VL")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about this image...", disabled=not st.session_state.naip_b64):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build messages — image only on first turn
        openai_messages = []
        for i, m in enumerate(st.session_state.messages):
            if i == 0:
                openai_messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": m["content"]},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/png;base64,{st.session_state.naip_b64}"
                        }}
                    ]
                })
            else:
                openai_messages.append({"role": m["role"], "content": m["content"]})

        with st.chat_message("assistant"):
            response_box = st.empty()
            full_response = ""
            stream = client.chat.completions.create(
                model="qwen3-vl:235b-cloud",
                messages=openai_messages,
                stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_response += delta
                response_box.markdown(full_response + "▌")
            response_box.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
