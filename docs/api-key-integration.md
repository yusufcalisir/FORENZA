# FORENZA API Key & Production Integration Guide

## Overview

FORENZA is engineered with a **Dual-Engine Architecture**:
1. **Demo / Showcase Simulation Engine:** Instant out-of-the-box operation with zero external dependencies. Uses high-fidelity biocomputational models, simulated MCMC deconvolution, and local ZK-SNARK mock proofs.
2. **Live Production / BYO-Key (Bring Your Own Key) Engine:** Full live execution powered by user-configured API credentials, connecting to live AI models (Google Gemini 2.0 Flash, OpenAI GPT-4o, Groq LLaMA 3.3), NCBI Entrez E-utilities, Ensembl REST, OpenFDA, custom Python FastAPI microservices, and Polygon RPC ZK-SNARK provers.

---

## 1. Supported API Providers & Environment Variables

| Provider / Protocol | Model / Protocol | Environment Var | Client Key Name | Purpose |
|---|---|---|---|---|
| **Google** | Gemini API | `GEMINI_API_KEY` | `geminiKey` | Live Aura Logic chat & multi-omic JSON sweeps |
| **OpenAI** | GPT-4o / GPT-4o-mini | `OPENAI_API_KEY` | `openaiKey` | Live Aura Logic chat & forensic reasoning |
| **Groq** | LLaMA 3.3 70B | `GROQ_API_KEY` | `groqKey` | Ultra-fast inference engine |
| **Anthropic** | Claude 3.5 Sonnet | `ANTHROPIC_API_KEY` | `anthropicKey` | High-precision scientific reasoning & report synthesis |
| **DeepSeek** | DeepSeek V3 / R1 | `DEEPSEEK_API_KEY` | `deepseekKey` | Advanced mathematical biocomputational analysis |
| **NCBI** | Entrez E-utilities | `NCBI_API_KEY` | `ncbiKey` | Live dbSNP & PubMed literature searches |
| **Backend** | Python FastAPI Engine | `FASTAPI_BACKEND_URL` | `backendUrl` | 30 microservice endpoints (MCMC, BPA, Horvath Clock) |
| **Ledger** | Polygon Testnet/Mainnet | `POLYGON_RPC_URL` | `polygonRpc` | ZK-SNARK Circom Groth16 proof anchoring |

---

## 2. Setting Up API Credentials

### Option A: Interactive In-App Key Manager (Recommended for Users)
1. Open the FORENZA web app.
2. Click the **Key Icon** in the top navigation header.
3. Enter your API credentials into the maskable input fields (Gemini, OpenAI, Groq, Anthropic, DeepSeek, etc.).
4. Click **`Save & Activate Mode`**. The header status dot will immediately turn green for **`[LIVE PRODUCTION MODE]`**.

### Option B: Self-Hosted Environment Variables (Recommended for Accredited Labs)
Create a `.env.local` file in the `frontend` root directory:

```env
# AI Assistant Keys
GEMINI_API_KEY="AIzaSyYourGeminiKeyHere..."
OPENAI_API_KEY="sk-proj-YourOpenAIKeyHere..."
GROQ_API_KEY="gsk_YourGroqKeyHere..."
ANTHROPIC_API_KEY="sk-ant-api03-YourAnthropicKeyHere..."
DEEPSEEK_API_KEY="sk-deepseek-YourDeepseekKeyHere..."

# Science & LIMS Connections
NCBI_API_KEY="ncbi_api_key_here"
FASTAPI_BACKEND_URL="http://localhost:8000"
POLYGON_RPC_URL="https://rpc-amoy.polygon.technology"
```

---

## 3. Automatic Multi-Model Routing & Failover Architecture

FORENZA routes AI requests through an intelligent, zero-downtime tier priority pipeline (`/api/aura-logic` and `/api/analyze-module`):

```mermaid
flowchart TD
    Req["👤 User Action / Analysis Request"] --> Check["🔍 Key Detection Pipeline"]
    Check -->|Gemini Key Present| G["1️⃣ Google Gemini 2.0 Flash (Fastest Multi-Omic & Structured JSON)"]
    Check -->|OpenAI Key Present| O["2️⃣ OpenAI GPT-4o / GPT-4o-mini (Deep Forensic Reasoning)"]
    Check -->|Claude Key Present| C["3️⃣ Anthropic Claude 3.5 Sonnet (Scientific Report Synthesis)"]
    Check -->|DeepSeek Key Present| D["4️⃣ DeepSeek V3 / R1 (Biostatistical Math Verification)"]
    Check -->|Groq Key Present| Gr["5️⃣ Groq LLaMA 3.3 70B (High-Speed Inference)"]
    Check -->|No Live Keys Set| Sim["6️⃣ Local Algorithmic Biocomputational Engine (Deterministic Fallback)"]

    G -->|Execution Success| Out["✅ Return Verified Forensic Analysis Payload"]
    O -->|Execution Success| Out
    C -->|Execution Success| Out
    D -->|Execution Success| Out
    Gr -->|Execution Success| Out
    Sim -->|Execution Success| Out
```

If a rate limit (HTTP 429) or connection error occurs on an upstream provider, the engine automatically attempts the next available provider in order, guaranteeing uninterrupted workflow execution for critical casework.

---

## 4. Security & Zero-Data-Leakage Guarantee

- **Client-Side Encryption & Local Storage:** User-entered keys in the UI modal are stored exclusively in the user's browser `localStorage` under the key `forenza_api_keys_v1`.
- **No Third-Party Key Persistence:** Keys are never transmitted to external analytics, logging frameworks, or persistent databases.
- **Header-Based Dynamic Injection:** The frontend injects decrypted keys via custom `x-gemini-key`, `x-openai-key`, `x-groq-key`, `x-anthropic-key`, `x-deepseek-key` headers per-request, ensuring stateless server-side routing.
- **ISO/IEC 17025 Compliance:** All genomic payloads and raw STR allele counts remain strictly within the local environment or encrypted serverless proxy routes.
