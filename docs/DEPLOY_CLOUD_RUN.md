# Google Cloud Run Deployment Guide

This document provides the exact, production-ready `gcloud` commands to manually deploy the **Enterprise Knowledge AI Backend** and **Frontend** to Google Cloud Run.

---

## 1. Prerequisites and Google Cloud Setup

### 1.1 Set Environment Variables
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export ARTIFACT_REPO="enterprise-knowledge-repo"
export BACKEND_SERVICE="ekai-backend"
export FRONTEND_SERVICE="ekai-frontend"

# Configure gcloud
gcloud config set project ${PROJECT_ID}
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com
```

### 1.2 Create Artifact Registry Repository
```bash
gcloud artifacts repositories create ${ARTIFACT_REPO} \
    --repository-format=docker \
    --location=${REGION} \
    --description="Docker repository for Enterprise Knowledge AI"

# Configure local docker authentication for Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev
```

---

## 2. Store Secrets in Google Secret Manager

Never store API keys in plaintext environment variables. Use Secret Manager:

```bash
# 1. Store Groq API Key
echo -n "your_groq_api_key_here" | gcloud secrets create groq-api-key \
    --data-file=- \
    --replication-policy="automatic"

# 2. Store Qdrant Cloud API Key
echo -n "your_qdrant_api_key_here" | gcloud secrets create qdrant-api-key \
    --data-file=- \
    --replication-policy="automatic"

# 3. Store Application Secret API Key
echo -n "ekai_production_secret_key_98765" | gcloud secrets create ekai-app-api-key \
    --data-file=- \
    --replication-policy="automatic"
```

Grant the Cloud Run default service account permission to read these secrets:
```bash
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format='value(projectNumber)')

for SECRET in groq-api-key qdrant-api-key ekai-app-api-key; do
  gcloud secrets add-iam-policy-binding ${SECRET} \
      --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
      --role="roles/secretmanager.secretAccessor"
done
```

---

## 3. Build & Deploy Backend to Cloud Run

### 3.1 Build & Push Backend Docker Image
```bash
export BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/backend:latest"

# Build using Cloud Build or local Docker
gcloud builds submit backend \
    --tag ${BACKEND_IMAGE} \
    --timeout="20m"
```

### 3.2 Deploy Backend Service
```bash
gcloud run deploy ${BACKEND_SERVICE} \
    --image ${BACKEND_IMAGE} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --min-instances 1 \
    --max-instances 10 \
    --concurrency 40 \
    --timeout 300 \
    --set-env-vars "\
APP_ENV=production,\
LOG_LEVEL=INFO,\
QDRANT_URL=https://your-qdrant-cluster.cloud.qdrant.io:6333,\
QDRANT_COLLECTION=enterprise_knowledge,\
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5,\
EMBEDDING_DIMENSION=384,\
SPARSE_MODEL=Qdrant/bm25,\
RETRIEVAL_TOP_K=5,\
RELEVANCE_SCORE_THRESHOLD=0.35" \
    --set-secrets "\
GROQ_API_KEY=groq-api-key:latest,\
QDRANT_API_KEY=qdrant-api-key:latest,\
API_KEY=ekai-app-api-key:latest"
```

Obtain the Backend URL:
```bash
export BACKEND_URL=$(gcloud run services describe ${BACKEND_SERVICE} --region ${REGION} --format='value(status.url)')
echo "Backend URL: ${BACKEND_URL}"
```

---

## 4. Build & Deploy Frontend to Cloud Run

### 4.1 Build & Push Frontend Docker Image
```bash
export FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPO}/frontend:latest"

# Build with backend URL injected as build-arg
gcloud builds submit frontend \
    --tag ${FRONTEND_IMAGE} \
    --timeout="10m"
```

### 4.2 Deploy Frontend Service
```bash
gcloud run deploy ${FRONTEND_SERVICE} \
    --image ${FRONTEND_IMAGE} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 5 \
    --concurrency 80
```

Obtain the Frontend URL:
```bash
export FRONTEND_URL=$(gcloud run services describe ${FRONTEND_SERVICE} --region ${REGION} --format='value(status.url)')
echo "Frontend URL: ${FRONTEND_URL}"
```

---

## 5. Wire CORS Between Services

Update the backend CORS origins to authorize requests from the deployed frontend domain:

```bash
gcloud run services update ${BACKEND_SERVICE} \
    --region ${REGION} \
    --update-env-vars "CORS_ORIGINS=${FRONTEND_URL}"
```

---

## 6. Verification and Health Checks

```bash
# Verify backend liveness
curl -f ${BACKEND_URL}/healthz

# Verify backend readiness (Qdrant & Groq)
curl -f ${BACKEND_URL}/readyz

# Inspect Prometheus metrics
curl -f ${BACKEND_URL}/metrics

# Open the frontend in browser
open ${FRONTEND_URL}
```
