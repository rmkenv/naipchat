# 🛰️ NAIP Chat — Conversational Earth Observation with Qwen3-VL

A Streamlit app that lets you fetch free 0.6-meter aerial imagery of any location 
in the continental United States and have a real-time conversation about what's in 
it — powered by the Qwen3-VL 235B vision-language model.

🔗 **Live Demo:** https://naipchat.streamlit.app

---

## What It Does

1. Enter any latitude/longitude (defaults to Catonsville, MD)
2. Fetch a NAIP aerial tile from Microsoft Planetary Computer — free, no account needed
3. Ask the AI anything about the image in natural language
4. Get expert-level geospatial analysis streamed back in real time

The model is prompted as a remote sensing scientist, so responses focus on land cover, 
infrastructure, vegetation patterns, impervious surfaces, water features, and 
real-world geographic context — not generic image captions.

---

## Demo Questions to Try

- *"What is the dominant land cover type in this image?"*
- *"Describe the road network and connectivity visible here."*
- *"How much of this tile appears to be impervious surface?"*
- *"Are there any signs of vegetation stress near water bodies?"*
- *"What kind of neighborhood is this — urban, suburban, or rural fringe?"*
- *"Describe any visible agricultural field patterns."*

---

## Stack

| Component | Tool |
|---|---|
| Aerial imagery | [NAIP via Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/dataset/naip) |
| Vision-language model | [Qwen3-VL 235B](https://ollama.com/library/qwen3-vl) via Ollama Cloud API |
| Image I/O | Rasterio, Pillow |
| UI | Streamlit |
| API client | OpenAI-compatible (`openai` Python SDK) |

---

## Why NAIP?

NAIP (National Agriculture Imagery Program) is collected by the USDA at **0.6-meter 
resolution** across the continental US every 2–3 years. At that resolution, individual 
trees, building footprints, parked cars, and vegetation edges are clearly visible — 
making it far more useful for parcel-level analysis than Sentinel-2 (10m) or Landsat (30m).

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/naipchat.git
cd naipchat
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** On Windows, install rasterio via conda:
> `conda install -c conda-forge rasterio`

### 3. Configure secrets

Create `.streamlit/secrets.toml`:

```toml
OLLAMA_API_KEY = "your_ollama_api_key"
OLLAMA_HOST    = "https://ollama.com"
OLLAMA_MODEL   = "qwen3-vl:235b-cloud"
```

Get your Ollama API key at [ollama.com](https://ollama.com).

### 4. Run

```bash
streamlit run app.py
```

---

## Deploying to Streamlit Cloud

1. Push repo to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Add the three secrets above under **App Settings → Secrets**
4. Add a `packages.txt` file to the repo root for rasterio's GDAL dependency:

```txt
libgdal-dev
```

---

## Requirements

```txt
streamlit>=1.35.0
openai>=1.30.0
pystac-client>=0.7.0
planetary-computer>=1.0.0
rasterio>=1.3.0
Pillow>=10.0.0
numpy>=1.26.0
```

---

## Features

- 📍 **Configurable AOI** — any lat/lon in the continental US, adjustable buffer radius
- 🖼️ **Live tile preview** — NAIP image displayed alongside the chat
- 💬 **Persistent conversation** — multi-turn chat with full context retained
- 🧠 **Editable system prompt** — swap analyst personas in the sidebar without touching code
- ⚡ **Streaming responses** — answers appear token by token in real time
- 🆓 **No imagery account needed** — Planetary Computer NAIP access is fully open

---

## Limitations

- NAIP coverage is **US only** and updated every 2–3 years per state — recently changed 
  areas may not reflect current conditions
- The model is a **general-purpose VLM**, not fine-tuned on remote sensing benchmarks — 
  responses are best suited for scene interpretation and Q&A, not precise pixel-level 
  classification
- Large buffer values may produce very large image tiles and slow API responses

---

## License

MIT

---

## Author

Built by [R K](https://github.com/rmkenv) — geospatial data scientist and Earth 
observation researcher 

