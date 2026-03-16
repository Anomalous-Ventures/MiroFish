# MiroFish Integration - Deployment Status

**Status**: ✅ Infrastructure Integration Complete - Ready for Image Build & Deployment

**Date**: 2026-03-16

## Completed Work

### 1. MiroFish Repository (`/home/pestilence/repos/personal/mirofish`)
**Branch**: `feat/infrastructure-integration`
**Commit**: `7d5ca8f`

**Files Created/Modified**:
- `Dockerfile.multiarch` - Multiarch build (linux/amd64,linux/arm64)
- `backend/app/config_infrastructure.py` - STAX infrastructure adapter
- `backend/app/services/qdrant_memory_adapter.py` - Qdrant memory replacement
- `.github/workflows/build-deploy.yml` - CI/CD pipeline with ARC runners
- `backend/requirements.txt` - Added qdrant-client>=1.7.0
- `INTEGRATION.md` - Comprehensive integration documentation
- `.claude/memory.md` - Project memory

### 2. STAX Infrastructure (`/home/pestilence/repos/personal/stax`)
**Branch**: `feat/add-mirofish-service`
**Commit**: `3f680ee`

**Files Created/Modified**:
- `pulumi/modules/services/mirofish.py` - Pulumi service module
- `pulumi/modules/service_stack.py` - Added MiroFish to SERVICE_REGISTRY
  - Service configuration
  - Homepage icon (mdi-fish)
  - Description ("Swarm intelligence prediction")

### 3. AI Stack Deployment (`/home/pestilence/repos/personal/stax-stack-08-ai`)
**Branch**: `feat/add-mirofish`
**Commit**: `63b1dff`

**Files Modified**:
- `__main__.py` - Added MiroFish deployment logic
  - Import MirofishService module
  - Configuration toggle: `enable_mirofish`
  - Deployment with infrastructure integration

## Architecture Summary

```
┌───────────────────────────────────────────────────────────┐
│                 MiroFish Service                           │
│          (harbor.spooty.io/library/mirofish)              │
│                                                            │
│  Frontend (Port 3000) ←─┐  Backend (Port 5001)           │
│                          │                                 │
│  React UI               │  Flask API + OASIS Simulation   │
│  Project Management     │  GraphRAG + Multi-Agent Engine  │
└─────────────────────────┼────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│           STAX Infrastructure (inference namespace)        │
│                                                            │
│  LiteLLM Gateway ────► vLLM/Ollama/Qwen Models           │
│  (Port 4000)                                              │
│                                                            │
│  Qdrant Vector DB ───► Agent Memory + Entities           │
│  (Port 6333)          Collections: mirofish_*             │
│                                                            │
│  Langfuse (Optional)─► LLM Observability                 │
│  (Port 3000)          Traces + Metrics                    │
└───────────────────────────────────────────────────────────┘
```

## Next Steps

### Phase 1: Build & Push Docker Image

```bash
# Navigate to mirofish repo
cd /home/pestilence/repos/personal/mirofish

# Option A: Manual build and push
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --file Dockerfile.multiarch \
  --tag harbor.spooty.io/library/mirofish:latest \
  --tag harbor.spooty.io/library/mirofish:v0.1.0 \
  --push .

# Option B: Push to GitHub and let Actions build
git push origin feat/infrastructure-integration

# Then merge to main via PR or directly:
git checkout main
git merge feat/infrastructure-integration
git push origin main
# GitHub Actions will automatically build and push multiarch image
```

### Phase 2: Deploy to Cluster

```bash
# Add Pulumi configuration
cd /home/pestilence/repos/personal/stax-stack-08-ai
pulumi config set enable_mirofish true

# Optional: Configure Langfuse observability
pulumi config set enable_langfuse true --secret

# Preview deployment
pulumi preview

# Deploy to cluster
pulumi up --yes
```

### Phase 3: Validation

```bash
# Wait for deployment
kubectl rollout status deployment/mirofish -n inference

# Check pod status
kubectl get pods -n inference -l app=mirofish

# Check service endpoints
kubectl get svc mirofish-frontend -n inference
kubectl get svc mirofish -n inference

# Test backend health
kubectl port-forward -n inference svc/mirofish 5001:5001 &
curl http://localhost:5001/health

# Test frontend
kubectl port-forward -n inference svc/mirofish-frontend 3000:3000 &
curl http://localhost:3000

# Check logs
kubectl logs -n inference deployment/mirofish -f

# Verify LiteLLM connectivity
kubectl exec -it -n inference deployment/mirofish -- \
  curl -H "Authorization: Bearer sk-internal" \
  http://litellm.inference.svc.cluster.local:4000/v1/models

# Verify Qdrant connectivity
kubectl exec -it -n inference deployment/mirofish -- \
  curl http://qdrant.inference.svc.cluster.local:6333/health
```

### Phase 4: Access & Testing

**Frontend URL**: `https://mirofish.spooty.io` (after Pulumi deployment creates IngressRoute)

**Test Simulation**:
1. Upload seed data (text document or PDF)
2. Configure simulation parameters
3. Run prediction with small agent count (10-20)
4. Review generated report
5. Interact with simulated agents

### Phase 5: Integration with Existing Agents

**Finance Agent + MiroFish**:
```python
# Use MiroFish API to predict market reactions
import requests

mirofish_api = "http://mirofish.inference.svc.cluster.local:5001"

# Create prediction project
response = requests.post(f"{mirofish_api}/api/projects", json={
    "name": "Market Reaction Simulation",
    "seed_data": market_analysis_text,
    "prediction_query": "How will retail investors react to Fed rate decision?"
})

project_id = response.json()["project_id"]

# Run simulation
simulation = requests.post(f"{mirofish_api}/api/simulations", json={
    "project_id": project_id,
    "agent_count": 100,
    "simulation_rounds": 30
})

# Get prediction report
report = requests.get(f"{mirofish_api}/api/reports/{simulation['report_id']}")
print(report.json()["prediction_summary"])
```

## Resource Requirements

**Storage**:
- PVC: 20Gi (Longhorn)
- Qdrant collections scale with project count

**Compute**:
- CPU Request: 500m
- CPU Limit: 4000m
- Memory Request: 2Gi
- Memory Limit: 8Gi
- GPU: Not required (LLM inference via LiteLLM)

**Network**:
- Internal cluster communication (low latency)
- No external network access required

## Configuration Reference

**Environment Variables** (set via Pulumi):
```bash
LITELLM_BASE_URL=http://litellm.inference.svc.cluster.local:4000/v1
LITELLM_API_KEY=sk-internal
LITELLM_MODEL=qwen2.5-coder-32b
QDRANT_URL=http://qdrant.inference.svc.cluster.local:6333
QDRANT_COLLECTION_PREFIX=mirofish
LANGFUSE_ENABLED=true  # Optional
```

**Pulumi Configuration**:
```yaml
# Pulumi.stage.yaml
config:
  stax-stack-08-ai:enable_mirofish: "true"
  stax-stack-08-ai:enable_langfuse: "true"  # Optional
```

## Troubleshooting

**Issue**: Image pull failures
```bash
# Check Harbor credentials
kubectl get secret harbor-credentials -n inference

# Manual image pull test
kubectl run -it --rm debug --image=harbor.spooty.io/library/mirofish:latest \
  --restart=Never -- /bin/sh
```

**Issue**: Backend health check failures
```bash
# Check logs
kubectl logs -n inference deployment/mirofish --tail=100

# Check environment variables
kubectl exec -n inference deployment/mirofish -- env | grep -E "(LITELLM|QDRANT)"

# Test LiteLLM connectivity
kubectl exec -n inference deployment/mirofish -- \
  curl -v http://litellm.inference.svc.cluster.local:4000/health
```

**Issue**: Simulation failures
```bash
# Check Qdrant collections
kubectl port-forward -n inference svc/qdrant 6333:6333 &
curl http://localhost:6333/collections

# Check memory usage
kubectl top pod -n inference -l app=mirofish
```

## Rollback Plan

```bash
# Disable MiroFish in Pulumi
pulumi config set enable_mirofish false
pulumi up --yes

# Or delete deployment directly
kubectl delete deployment mirofish -n inference
kubectl delete svc mirofish mirofish-frontend -n inference
kubectl delete pvc mirofish-data -n inference
```

## Success Criteria

- [ ] Docker image built for both linux/amd64 and linux/arm64
- [ ] Image pushed to harbor.spooty.io/library/mirofish
- [ ] Pulumi deployment successful (no errors)
- [ ] Pod status: Running, READY 1/1
- [ ] Backend health check: 200 OK on /health
- [ ] Frontend accessible via HTTPS
- [ ] LiteLLM connectivity verified
- [ ] Qdrant collections created successfully
- [ ] Test simulation completes without errors
- [ ] Report generation produces output
- [ ] Langfuse traces visible (if enabled)

## Monitoring

**Metrics** (via Prometheus):
- Pod CPU/memory usage
- HTTP request rate/latency
- Simulation execution time
- LLM API call rate
- Qdrant query performance

**Logs** (via Loki):
```bash
# View logs in Grafana
kubectl port-forward -n monitoring svc/grafana 3000:80 &
# Navigate to: http://localhost:3000
# Explore > Loki > {namespace="inference", app="mirofish"}
```

**Alerts** (via Prometheus rules):
- Pod restart loops
- High memory usage (>90%)
- Health check failures
- Slow simulation execution (>5min for 100 agents)

## Documentation

- **Integration Guide**: `/home/pestilence/repos/personal/mirofish/INTEGRATION.md`
- **Upstream README**: `/home/pestilence/repos/personal/mirofish/README-EN.md`
- **Project Memory**: `/home/pestilence/repos/personal/mirofish/.claude/memory.md`
- **This Status**: `/home/pestilence/repos/personal/mirofish/DEPLOYMENT_STATUS.md`

---

**Questions?** Refer to INTEGRATION.md or review the upstream MiroFish documentation.
