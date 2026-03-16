# MiroFish Deployment Note - Image Push Issue

## Current Status

**Image Built**: ✅ Successfully built locally
- Image: `harbor.spooty.io/library/mirofish:latest`
- Size: 8.99 GB
- ID: dc95d21c6003

**Push to Harbor**: ❌ Timing out (HTTP 499)
- Error: "Client Closed Request"
- Cause: Large image size (9GB) exceeding upload timeout
- Harbor Status: Healthy and accessible

## Solution: Use GitHub Actions for Multiarch Build

**Recommended approach**: Push code to GitHub, let CI/CD build and push

### Steps:

1. **Create GitHub Repository** (if not exists)
```bash
# Option A: Fork upstream and add as remote
cd /home/pestilence/repos/personal/mirofish
git remote add personal git@github.com:YOUR_USERNAME/mirofish.git

# Option B: Create new repo and push
gh repo create mirofish --private
git remote add personal git@github.com:YOUR_USERNAME/mirofish.git
```

2. **Push Integration Branch**
```bash
git push personal feat/infrastructure-integration
```

3. **Merge to Main (triggers GitHub Actions)**
```bash
git checkout main
git merge feat/infrastructure-integration
git push personal main

# GitHub Actions will:
# - Build multiarch (linux/amd64, linux/arm64)
# - Push to harbor.spooty.io/library/mirofish:latest
# - Takes ~15-20 min but handles large images properly
```

4. **Monitor GitHub Actions**
```bash
gh run list
gh run watch
```

5. **Deploy After Actions Complete**
```bash
cd /home/pestilence/repos/personal/stax-stack-08-ai
pulumi config set enable_mirofish true  # Already done
pulumi up --yes
```

## Alternative: Manual Image Transfer

If you prefer not to use GitHub Actions:

```bash
# Save image to tarball
podman save harbor.spooty.io/library/mirofish:latest | gzip > mirofish.tar.gz

# Transfer to a cluster node
scp mirofish.tar.gz node01:/tmp/

# Load on node
ssh node01 "gunzip < /tmp/mirofish.tar.gz | podman load"

# Tag and push from node (better network to Harbor)
ssh node01 "podman push harbor.spooty.io/library/mirofish:latest"
```

## Current Pulumi Configuration

✅ **Already Configured**:
```yaml
stax-ai:enable_mirofish: "true"
```

**Deployment Ready**: Once image is in Harbor, run:
```bash
cd /home/pestilence/repos/personal/stax-stack-08-ai
pulumi up --yes
```

## Why GitHub Actions is Better

1. **Multiarch Support**: Builds for both AMD64 and ARM64
2. **Optimized for Large Images**: CI infrastructure handles large uploads
3. **Automated**: Repeatable, documented process
4. **Caching**: Layer caching speeds up future builds
5. **No Local Resource Consumption**: Offloads build to GitHub

## Next Steps

**Choose one:**

**Option A**: GitHub Actions (Recommended)
- Create/use personal GitHub fork
- Push `feat/infrastructure-integration` branch
- Merge to main
- Wait for Actions to complete (~15-20 min)
- Deploy via Pulumi

**Option B**: Manual Transfer
- Save image locally
- Transfer to cluster node
- Push from node to Harbor
- Deploy via Pulumi

**Option C**: Deploy Without MiroFish (for now)
- Comment out or set `enable_mirofish: false`
- Deploy other AI stack services
- Add MiroFish later after image upload resolves

## Status Summary

- ✅ Code integration complete (3 repos)
- ✅ Docker image built locally
- ❌ Image push to Harbor (timeout)
- ✅ Pulumi configuration ready
- ⏸️ Deployment blocked on image availability

**Recommendation**: Use GitHub Actions for proper multiarch build and automated push.
