# MiroFish Deployment Plan

## Current Status

**Image Build**: In progress (PID 253862)
- Building: `harbor.spooty.io/library/mirofish:latest`
- Platform: linux/amd64 (current architecture)
- Multi-stage build: backend-builder → frontend-builder → production

## Deployment Sequence

### Step 1: Complete Image Build ✓ (In Progress)
```bash
# Currently running:
podman build -f Dockerfile.multiarch \
  -t harbor.spooty.io/library/mirofish:latest .
```

**Expected output**:
- Backend dependencies installed via `uv`
- Frontend built via `npm run build`
- Final image tagged and ready

### Step 2: Push Image to Harbor
```bash
cd /home/pestilence/repos/personal/mirofish

# Push to Harbor
podman push harbor.spooty.io/library/mirofish:latest

# Tag with version
podman tag harbor.spooty.io/library/mirofish:latest \
  harbor.spooty.io/library/mirofish:v0.1.0
podman push harbor.spooty.io/library/mirofish:v0.1.0
```

### Step 3: Configure Pulumi
```bash
cd /home/pestilence/repos/personal/stax-stack-08-ai

# Enable MiroFish
pulumi config set enable_mirofish true

# Verify configuration
pulumi config get enable_mirofish
pulumi config get enable_litellm  # Should be true
pulumi config get enable_qdrant   # Should be true
pulumi config get enable_langfuse # Should be true (optional)
```

### Step 4: Deploy to Cluster
```bash
cd /home/pestilence/repos/personal/stax-stack-08-ai

# Preview changes
pulumi preview

# Deploy
pulumi up --yes

# Monitor deployment
kubectl rollout status deployment/mirofish -n inference --timeout=5m
```

### Step 5: Verification
```bash
# Check pod status
kubectl get pods -n inference -l app=mirofish

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# mirofish-xxxxxxxxxx-xxxxx   1/1     Running   0          2m

# Check services
kubectl get svc -n inference | grep mirofish

# Expected output:
# mirofish                ClusterIP   10.x.x.x   <none>        5001/TCP   2m
# mirofish-frontend       ClusterIP   10.x.x.x   <none>        3000/TCP   2m

# Test backend health
kubectl port-forward -n inference svc/mirofish 5001:5001 &
curl http://localhost:5001/health

# Expected: {"status": "healthy", ...}

# Test frontend
kubectl port-forward -n inference svc/mirofish-frontend 3000:3000 &
curl -I http://localhost:3000

# Expected: HTTP/1.1 200 OK
```

### Step 6: Access via Ingress
```bash
# MiroFish should be accessible at:
https://mirofish.spooty.io

# Frontend: React UI for creating simulations
# Backend API: http://mirofish.spooty.io:5001/api/*
```

### Step 7: Integration Testing
```bash
# Test LiteLLM connectivity from pod
kubectl exec -it -n inference deployment/mirofish -- \
  curl -H "Authorization: Bearer sk-internal" \
  http://litellm.inference.svc.cluster.local:4000/v1/models

# Expected: {"object": "list", "data": [...]}

# Test Qdrant connectivity
kubectl exec -it -n inference deployment/mirofish -- \
  curl http://qdrant.inference.svc.cluster.local:6333/collections

# Expected: {"result": {"collections": []}}
```

### Step 8: Run Test Simulation
1. Access `https://mirofish.spooty.io`
2. Upload test document (e.g., sample market analysis)
3. Create project with prediction query
4. Configure simulation:
   - Agent count: 20 (small test)
   - Simulation rounds: 10
5. Run simulation
6. Verify report generation
7. Check Qdrant collections created:
```bash
kubectl exec -it -n inference deployment/mirofish -- \
  curl http://qdrant.inference.svc.cluster.local:6333/collections
# Should show: mirofish_*_memories, mirofish_*_entities
```

## Rollback Plan

If deployment fails:
```bash
# Disable MiroFish
cd /home/pestilence/repos/personal/stax-stack-08-ai
pulumi config set enable_mirofish false
pulumi up --yes

# Or manually delete resources
kubectl delete deployment mirofish -n inference
kubectl delete svc mirofish mirofish-frontend -n inference
kubectl delete pvc mirofish-data -n inference
```

## Troubleshooting

### Issue: ImagePullBackOff
```bash
# Check image exists in Harbor
curl -u admin:$HARBOR_PASSWORD \
  https://harbor.spooty.io/api/v2.0/projects/library/repositories/mirofish/artifacts

# Check pod events
kubectl describe pod -n inference -l app=mirofish

# Verify Harbor secret
kubectl get secret harbor-credentials -n inference
```

### Issue: CrashLoopBackOff
```bash
# Check logs
kubectl logs -n inference deployment/mirofish --tail=100

# Common issues:
# - Missing environment variables
# - LiteLLM/Qdrant connectivity
# - Port conflicts
# - Memory limits too low
```

### Issue: Health Check Failures
```bash
# Check backend logs
kubectl logs -n inference deployment/mirofish -f

# Test health endpoint directly
kubectl exec -it -n inference deployment/mirofish -- \
  curl -v http://localhost:5001/health

# Check if Flask is running
kubectl exec -it -n inference deployment/mirofish -- \
  ps aux | grep python
```

## Post-Deployment Tasks

1. **Update Documentation**
   - Add MiroFish to service inventory
   - Document API endpoints
   - Create user guide for simulations

2. **Configure Monitoring**
   - Verify Prometheus metrics scraping
   - Check Grafana dashboards
   - Set up alerts for:
     - Pod restarts
     - High memory usage
     - Slow simulations
     - LLM API errors

3. **Integrate with Existing Agents**
   - Finance Agent: Add market prediction workflow
   - Healthcare Agent: Add treatment response simulation
   - SRE Agent: Add infrastructure change prediction

4. **Performance Optimization**
   - Monitor resource usage during simulations
   - Adjust CPU/memory limits if needed
   - Tune agent count for optimal performance
   - Configure Qdrant collection settings

5. **Security Review**
   - Verify SSO integration
   - Check network policies
   - Review RBAC permissions
   - Audit API endpoints

## Success Metrics

- [ ] Image built and pushed to Harbor
- [ ] Pod running with 1/1 READY
- [ ] Health check returning 200 OK
- [ ] Frontend accessible via HTTPS
- [ ] LiteLLM connectivity verified
- [ ] Qdrant collections created
- [ ] Test simulation completed successfully
- [ ] Report generated correctly
- [ ] Langfuse traces visible (if enabled)
- [ ] Resource usage within limits (<8Gi memory, <4 CPU)

## Timeline

- **Image Build**: 5-10 minutes (in progress)
- **Image Push**: 2-3 minutes
- **Pulumi Deploy**: 3-5 minutes
- **Pod Start**: 1-2 minutes
- **Total**: ~15-20 minutes from start to accessible service

## Next Actions After Deployment

1. Create sample simulations for each use case
2. Document API integration patterns
3. Set up automated testing
4. Configure backup for project data
5. Plan multiarch build via GitHub Actions
