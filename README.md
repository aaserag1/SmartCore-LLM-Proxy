# 🚀 Multi-LLM API Load Balancer & Fallback Router
**Developed by: Ahmed Adel (Abo Adel)**

A robust, lightweight, and open-source load balancer designed for backend developers to bypass AI API Rate Limits seamlessly. 

## 📌 Overview
When building heavy backend systems or ERPs, hitting API rate limits on language models can crash your operations. This tool sets up a **Local Gateway** using `LiteLLM` that aggregates multiple API keys (e.g., Google Gemini, DeepSeek, Anthropic) and provides automatic fallback routing and latency-based load balancing. 

If your primary model hits a rate limit (429) or experiences downtime, requests are instantly routed to the next available model with automatic cooldown periods, ensuring **100% system uptime**.

## ✨ Key Features
* **Zero Downtime:** Automatic fallback routing and retry mechanism keep your application running smoothly.
* **Smart Cooldown & Retries:** Automatically puts rate-limited models on a 60-second cooldown period before retrying.
* **Cost Efficiency:** Combine multiple free-tier API keys into a single, highly available endpoint.
* **Plug & Play:** Easily integrates with any UI (like Hermes AI) or custom backend code.
* **One-Click Startup:** Includes a Batch script (`Run_LiteLLM.bat`) for instant local server deployment.

## ⚙️ Prerequisites
* **Python 3.8+** installed on your system.

## 🛠️ Step-by-Step Setup Guide

### Step 1: Install Dependencies
Open your terminal (CMD or PowerShell) and run the following command to install the required proxy library:

```bash
pip install "litellm[proxy]"
```

### Step 2: Configure Your API Keys
1. Open `config.yaml` in any text editor.
2. Replace placeholder values (e.g., `"YOUR_GOOGLE_KEY_HERE"`, `"YOUR_DEEPSEEK_KEY_HERE"`) with your actual API keys.
3. Adjust fallbacks and routing rules if desired.
4. Save the file.

> ⚠️ **SECURITY WARNING:** NEVER commit or upload your `config.yaml` with live API keys to public repositories.

### Step 3: Run the Local Gateway
Double-click `Run_LiteLLM.bat` or run:

```bash
python -m litellm --config config.yaml --port 4000 --host 127.0.0.1
```

A command window will open, starting the proxy server at:
`http://127.0.0.1:4000`

Keep this window running while using your application.

### Step 4: Connect Your Application (e.g. Hermes AI)
1. Go to your application's API or Gateway settings.
2. Set the **BASE URL** / **GATEWAY PROXY URL** to:
   `http://127.0.0.1:4000`
3. Enjoy uninterrupted model switching!

---
*Developed by Ahmed Adel (Abo Adel)*
