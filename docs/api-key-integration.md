# FORENZA API Key & Production Integration Guide

## Overview

FORENZA is engineered with a **Dual-Engine Architecture**:
1. **Demo / Showcase Simulation Engine:** Instant out-of-the-box operation with zero external dependencies. Uses high-fidelity biocomputational models, simulated MCMC deconvolution, and local ZK-SNARK mock proofs.
2. **Live Production / BYO-Key (Bring Your Own Key) Engine:** Full live execution powered by user-configured API credentials, connecting to live AI models (Google Gemini 2.0 Flash, OpenAI GPT-4o, Groq LLaMA 3.3), NCBI Entrez E-utilities, Ensembl REST, OpenFDA, custom Python FastAPI microservices, and Polygon RPC ZK-SNARK provers.

---

## 1. Supported API Providers & Environment Variables

| Category | Provider / Service | Environment Variable | Header / Client Modal Key | Supported Features |
|---|---|---|---|---|
| **AI LLM** | Google Gemini API | `GEMINI_API_KEY` | `geminiKey` | Aura Logic AI chat, natural language court testimony synthesis |
| **AI LLM** | OpenAI API | `OPENAI_API_KEY` | `openaiKey` | GPT-4o / GPT-4o-mini ad-hoc forensic query processing |
| **AI LLM** | Groq Cloud | `GROQ_API_KEY` | `groqKey` | LLaMA 3.3 70B high-speed inference |
| **AI LLM** | Local Ollama | `OLLAMA_BASE_URL` | `ollamaUrl` | Air-gapped / local LLM inference |
| **Genomics** | NCBI Entrez E-utilities | `NCBI_API_KEY` | `ncbiKey` | High-throughput rsID, SRA, and PubMed bibliography queries |
| **Backend** | Python FastAPI Engine | `FASTAPI_BACKEND_URL` | `backendUrl` | 30 microservice endpoints (MCMC, BPA, Horvath Clock) |
| **Ledger** | Polygon Testnet/Mainnet | `POLYGON_RPC_URL` | `polygonRpc` | ZK-SNARK Circom Groth16 proof anchoring |

---

## 2. Setting Up API Credentials

### Option A: Interactive In-App Key Manager (Recommended for Users)
1. Open the FORENZA web app.
2. Click the **`[DEMO SİMÜLASYON MODU]`** / **`[DEMO SIMULATION MODE]`** badge in the top navigation header.
3. Enter your API credentials into the maskable input fields.
4. Click **`Save & Activate Mode`**. The header badge will immediately switch to **`[CANLI ÜRETİM MODU]`** / **`[LIVE PRODUCTION MODE]`**.

### Option B: Self-Hosted Environment Variables (Recommended for Accredited Labs)
Create a `.env.local` file in the `frontend` root directory:

```env
# AI Assistant Keys
GEMINI_API_KEY="AIzaSyYourGeminiKeyHere..."
OPENAI_API_KEY="sk-proj-YourOpenAIKeyHere..."
GROQ_API_KEY="gsk_YourGroqKeyHere..."

# Science & LIMS Connections
NCBI_API_KEY="ncbi_api_key_here"
FASTAPI_BACKEND_URL="http://localhost:8000"
POLYGON_RPC_URL="https://rpc-amoy.polygon.technology"
```

---

## 3. Security & Zero-Data-Leakage Guarantee

- **Client-Side Encryption & Local Storage:** User-entered keys in the UI modal are stored exclusively in the user's browser `localStorage` under the key `forenza_api_keys_v1`.
- **No Third-Party Key Persistence:** Keys are never transmitted to external analytics, logging frameworks, or persistent databases.
- **ISO/IEC 17025 Compliance:** All genomic payloads and raw STR allele counts remain strictly within the local environment or encrypted serverless proxy routes.
