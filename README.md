# Hardened Enterprise MLOps Platform (Production Blueprint)

**This repository is NOT a Proof of Concept (PoC). This is a functional MLOps Production Architecture Blueprint.** 

A Proof of Concept evaluates whether a machine learning model *can* make a prediction. This blueprint demonstrates *how* that model is safely governed, containerized, audited, and hardened to survive inside a zero-trust enterprise ecosystem. The focus of this codebase is the foundational software architecture, compliance guardrails, and self-healing infrastructure patterns wrapper surrounding the core data science tier.

---

## Business Value & Operational ROI

Standard ML initiatives frequently fail when raw pipelines violate data privacy laws or lack deployment stability. This platform explicitly mitigates engineering and legal liabilities through three core pillars:
* **Defensive Data Ingestion (GDPR/HIPAA Compliance):** Automates PII erasure using cryptographic HMAC-SHA256 tokenization before features can reach disk or model training cycles.
* **Adversarial System Defenses (Security):** Implements statistical outlier screening at the ingestion gate to intercept and drop data-poisoning attempts automatically.
* **High-Availability Infrastructure (SLA Protection):** Utilizes an automated Circuit Breaker pattern and asynchronous concurrency worker queues to ensure the web tier never crashes during downstream outages.

---

## System Architecture & File Registry

The platform completely separates legal pipelines, data governance, core modeling, and edge routing layers across explicit package boundaries:

```text
├── .github/workflows/
│   ├── cla-check.yml             # Programmatic legal consent gateway
│   └── mlops-pipeline.yml        # CI/CD: Linting, security audits, container builds
├── config/
│   └── security_policy.json      # Centralized governance rulebook and risk matrices
├── data_pipeline/
│   ├── __init__.py               # Core pipeline package facade interface
│   ├── anonymizer.py             # Irreversible PII masking (HMAC-SHA256)
│   ├── pipeline_manager.py       # Central orchestration and ingestion coordinator
│   └── validator.py              # Schema mapping and adversarial Z-score screening
├── legal/
│   ├── CCLA_TEMPLATE.md          # Corporate Contributor License Agreement terms
│   └── DATA_PROVENANCE_LOG.csv   # Immutable, queryable data-lineage ledger
├── signatures/production/
│   └── cla_signatures.json       # Local storage ledger database for CLA bot signatures
├── src/
│   ├── __init__.py               # Core source package facade interface
│   ├── api_gateway.py            # Microservice contract validation & Circuit Breaker engine
│   ├── app.py                    # FastAPI application initialization & async worker pools
│   ├── model_registry.py         # Versioned model serialization and compliance metadata logs
│   └── train.py                  # Orchestrated training loop with automated quality check gates
├── tests/
│   └── test_pipeline.py          # PyTest unit suite verifying quality gate thresholds
├── .env.example                  # Environment configuration template
├── .gitignore                    # Data-leak preventative filter rules
├── .pre-commit-config.yaml       # Client-side credential and data intercept hooks
├── Dockerfile                    # Multi-stage, non-root hardened runtime container configuration
└── requirements.txt              # Production-pinned dependency constraints
```

---

## Data Governance & Compliance Provenance Log

Every execution of the data ingestion pipeline automatically records an immutable trail to our data provenance ledger (`legal/DATA_PROVENANCE_LOG.csv`). This satisfies strict regulatory requirements for tracking data ancestry and consent grounds.

### Active Ledger History (Live Preview)


| Dataset ID | Ingestion Timestamp | Source URI | Consent / Legal Basis | PII Status | Encryption | Pipeline Version | Audit Signature |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `DS_MED_2026_Q2` | `2026-05-14T15:21:04Z` | `s3://prod-lake/medical/` | HIPAA Consent Form B |  `CLEANED` | `AES_256` | `v1.1.0` | `8f7b...21a9` |
| `DS_FIN_2026_A1` | `2026-05-12T08:14:22Z` | `gcs://prod-lake/finance/` | GDPR Article 6(1)(b) |  `CLEANED` | `AES_256` | `v1.1.0` | `3e4d...90f2` |

>  [View Full Functional Audit Trail History](./legal/DATA_PROVENANCE_LOG.csv)

---

##  Quick Start (Local Production Simulation)

### 1. Initialize Git Hooks & Environment
Configure security tools locally on your development workstation before committing changes:
```bash
pip install -r requirements.txt
pre-commit install
cp .env.example .env
```

### 2. Orchestrate and Train the Audited Model
Run the end-to-end training cycle. This script validates raw input data, hashes sensitive columns, writes data to the ledger, verifies evaluation thresholds, and versions the model artifact:
```bash
python -m src.train
```

### 3. Build and Run the Hardened Microservice Container
Compile your application image into a lightweight, secure deployment box and spin up the live API:
```bash
docker build -t enterprise-ml-service:v1 .
docker run -p 8000:8000 --env-file .env enterprise-ml-service:v1
```

### 4. Query the Live Interface Endpoints
* **Health/Kubernetes Probe:** `curl http://localhost:8000/health`
* **Real-time Synchronous Prediction:**
```bash
curl -X 'POST' \
  'http://localhost:8000/predict' \
  -H 'Content-Type: application/json' \
  -d '{"age": 34, "monthly_charges": 75.50}'
```
* **High-Throughput Asynchronous Queue Prediction:**
```bash
curl -X 'POST' 'http://localhost:8000/predict/async' \
  -H 'Content-Type: application/json' \
  -d '{"age": 45, "monthly_charges": 120.00}'
```

---

##  Advanced Design Patterns Implemented

1. **Self-Healing Circuit Breaker (`src/api_gateway.py`):** Protects cluster stability. If backend assets or models fail 3 consecutive times, the API gateway trips into an `OPEN` state and routes incoming requests to a deterministic, conservative backup calculation without crashing the application.
2. **Asynchronous Process Offloading (`src/app.py`):** Prevents thread blocking. High-concurrency inference tasks are offloaded instantly to a background worker queue, permitting immediate HTTP status code acknowledgments.
3. **Adversarial Mitigation (`data_pipeline/validator.py`):** Real-time Z-score filtering detects and strips out malicious data injection outliers from the processing stream before they can poison training iterations.
