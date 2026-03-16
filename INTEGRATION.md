# MiroFish STAX Infrastructure Integration

## Overview

MiroFish has been adapted to run on STAX infrastructure with the following modifications:

### Key Changes

1. **LLM Integration**
   - Uses LiteLLM gateway instead of direct OpenAI API
   - Routes through cluster service: `litellm.inference.svc.cluster.local:4000`
   - Supports all models available in the STAX LLM stack (Qwen, vLLM, etc.)

2. **Vector Memory Migration**
   - Replaced Zep Cloud with Qdrant vector database
   - Memory and entity storage now use existing Qdrant infrastructure
   - Adapter implements same interface as Zep for compatibility

3. **Observability**
   - Optional Langfuse integration for LLM tracing
   - Connects to existing Langfuse instance in inference namespace

4. **Containerization**
   - Multiarch Docker builds (linux/amd64, linux/arm64)
   - Compatible with heterogeneous cluster nodes
   - Pushes to Harbor registry: `harbor.spooty.io/library/mirofish`

5. **CI/CD**
   - GitHub Actions using ARC self-hosted runners (stax-builder, stax-python)
   - Automated build, test, and deploy pipeline
   - Pulumi deployment to stax-stack-08-ai

## Architecture Integration

```
┌─────────────────────────────────────────────────────────────┐
│                      MiroFish Frontend                       │
│                    (React - Port 3000)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      MiroFish Backend                        │
│                   (Flask API - Port 5001)                    │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │Graph Builder │  │  Simulation  │  │Report Agent  │       │
│  │  (GraphRAG)  │  │   Manager    │  │              │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │               │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  STAX Infrastructure                         │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   LiteLLM    │  │   Qdrant     │  │  Langfuse    │       │
│  │   Gateway    │  │Vector Memory │  │Observability │       │
│  │              │  │              │  │              │       │
│  │  (Port 4000) │  │  (Port 6333) │  │  (Port 3000) │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │               │
│         ▼                  ▼                  ▼               │
│  ┌─────────────────────────────────────────────────┐         │
│  │     vLLM / Ollama / Reasoning Models           │         │
│  │  (Qwen2.5-Coder-32B, QwQ-32B, etc.)            │         │
│  └─────────────────────────────────────────────────┘         │
│                                                               │
│                 namespace: inference                         │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Variables

**Required:**
```bash
# LLM (via LiteLLM)
LITELLM_BASE_URL=http://litellm.inference.svc.cluster.local:4000/v1
LITELLM_API_KEY=sk-internal
LITELLM_MODEL=qwen2.5-coder-32b

# Qdrant Vector Memory
QDRANT_URL=http://qdrant.inference.svc.cluster.local:6333
QDRANT_COLLECTION_PREFIX=mirofish
```

**Optional:**
```bash
# Qdrant authentication (if enabled)
QDRANT_API_KEY=<your-key>

# Langfuse observability
LANGFUSE_PUBLIC_KEY=<public-key>
LANGFUSE_SECRET_KEY=<secret-key>
LANGFUSE_HOST=http://langfuse.inference.svc.cluster.local:3000

# Legacy Zep fallback (not recommended)
USE_ZEP=false
ZEP_API_KEY=<zep-key>
```

## Deployment

### Option 1: Pulumi (Recommended)

```bash
cd /path/to/stax/pulumi
pulumi stack select stax-stack-08-ai
pulumi up
```

### Option 2: Kubernetes Manifests

```bash
kubectl apply -f k8s/mirofish-deployment.yaml -n inference
```

### Option 3: Docker Compose (Development)

```bash
cd /path/to/mirofish
docker-compose up -d
```

## Usage Examples

### Financial Prediction
Upload market analysis report and ask:
> "Predict how retail investors will react to the Fed's interest rate decision over the next 30 days"

### Policy Simulation
Upload policy draft and ask:
> "Simulate public opinion response to this healthcare reform proposal across different demographic groups"

### Creative Scenarios
Upload novel chapters and ask:
> "Predict how the characters would interact if [scenario injection]"

## Integration with Existing Agents

### Finance Agent
- Use MiroFish to simulate market reactions before executing trades
- Test trading strategies in parallel digital environment
- Predict competitor behavior

### Healthcare Agent
- Simulate patient response to treatment protocols
- Predict healthcare policy impacts on patient populations
- Test intervention strategies

### SRE Agent
- Simulate infrastructure changes before deployment
- Predict system behavior under load scenarios
- Test disaster recovery procedures

## Performance Considerations

- **Memory Usage**: Each simulation with 100 agents ~2GB RAM
- **GPU**: Not required (LLM inference handled by vLLM)
- **Storage**: Qdrant collections scale with project count
- **Network**: Internal cluster communication (low latency)

## Validation Checklist

- [ ] LiteLLM connectivity verified
- [ ] Qdrant collections created successfully
- [ ] Simulation runs complete without errors
- [ ] Report generation produces output
- [ ] Frontend accessible and responsive
- [ ] Langfuse traces visible (if enabled)
- [ ] Multiarch images pulled correctly on ARM/AMD nodes

## Troubleshooting

### LLM Connection Issues
```bash
# Test LiteLLM connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never \
  -- curl -H "Authorization: Bearer sk-internal" \
  http://litellm.inference.svc.cluster.local:4000/v1/models
```

### Qdrant Issues
```bash
# Check Qdrant health
kubectl run -it --rm debug --image=curlimages/curl --restart=Never \
  -- curl http://qdrant.inference.svc.cluster.local:6333/health
```

### Pod Logs
```bash
kubectl logs -n inference deployment/mirofish-backend -f
```

## License

AGPL-3.0 (inherited from upstream MiroFish)

## Acknowledgments

- Original MiroFish by Shanda Group
- OASIS simulation engine by CAMEL-AI
- STAX infrastructure integration
