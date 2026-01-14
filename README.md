# Fast Houses Search Scraper

A **Facebook group post scraper browser extension** designed to quickly extract and structure **housing-related listings** (rentals, sales, roommates, etc.) from Facebook groups.

The project also includes a **Gradio web app** that uses the **Gemini 2.0 Flash Lite (free tier)** API to extract and summarize useful information from scraped posts using an LLM.

---

## 🏠 Motivation

Searching for houses in Facebook groups is often:
- Manual
- Time-consuming
- Unstructured
- Difficult to filter

This project automates the process by:
- Scraping posts directly from Facebook groups via a browser extension
- Extracting structured information from raw text using an LLM
- Making housing search faster and more efficient

---

## ✨ Features

- 🧩 **Browser Extension** for scraping Facebook group posts
- 🏘️ Optimized for **housing-related posts**
- 📄 Extracts raw post text and metadata
- 🤖 **LLM-powered information extraction** using Gemini 2.0 Flash Lite
- 🖥️ **Gradio app** for interactive post analysis
- ⚡ Uses **free-tier APIs** only

---

## 🧠 System Overview

```
Facebook Group Page
        ↓
Browser Extension Scraper
        ↓
Raw Post Text
        ↓
Gradio Web App
        ↓
Gemini 2.0 Flash Lite API
        ↓
Structured Housing Information
```

---

## 🧩 Browser Extension

### What it Does

The browser extension:
- Runs directly in the browser
- Scrapes visible Facebook group posts
- Extracts:
  - Post content
  - Timestamps
  - Author (when available)
- Outputs raw text suitable for downstream processing

⚠️ **Note:** The scraper only accesses content visible to the logged-in user.

---

## 🤖 LLM-Powered Information Extraction

The Gradio app uses **Gemini 2.0 Flash Lite** to extract useful housing information from posts, such as:

- Location
- Price
- Type (rent / sale)
- Number of rooms
- Contact details
- Availability dates

This transforms unstructured Facebook posts into **structured, searchable data**.

---

## 🖥️ Gradio App

### Features

- Paste or upload scraped Facebook posts
- Run LLM-based extraction
- View structured output instantly
- Lightweight and easy to deploy locally

---

## 🔑 Gemini API

- Model: **gemini-2.0-flash-lite**
- API Tier: **Free**
- Used for:
  - Text understanding
  - Entity extraction
  - Post summarization

---

## 🛠️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/leonardokoen/Fast-Houses-Search-Scraper.git
cd Fast-Houses-Search-Scraper
```

---

### 2️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Set Up Gemini API Key

Create an environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"
```

(Windows PowerShell)
```powershell
setx GEMINI_API_KEY "your_api_key_here"
```

---

### 4️⃣ Run the Gradio App

```bash
python app.py
```

The app will be available at:

```
http://localhost:7860
```

---

## 🧪 Usage Workflow

1. Install and run the browser extension
2. Navigate to a Facebook housing group
3. Scroll to load posts
4. Scrape posts using the extension
5. Paste scraped text into the Gradio app
6. Extract structured housing information using Gemini

---

## ⚠️ Disclaimer

This project is intended for **educational and personal use only**.

- It does **not bypass Facebook authentication**
- It only processes content visible to the user
- Users are responsible for complying with Facebook’s Terms of Service

---

## 🔮 Roadmap

- [x] Facebook group scraper extension
- [x] Housing-focused post extraction
- [x] Gradio UI
- [x] Gemini LLM integration
- [x] Export to CSV / JSON

---

## 👤 Author

**Leonardokoen**

---

## 📜 License

This project is released under the MIT License.
