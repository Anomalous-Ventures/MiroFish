from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[2] / ".github/workflows/build-deploy.yml"


def test_gitops_promotion_is_digest_only_and_pr_gated():
    source = WORKFLOW.read_text()

    assert "cat > deployments/08-ai/llm/mirofish" not in source
    assert "git push origin HEAD:main" not in source
    assert "deployments/08-ai/llm/mirofish/deployment.yaml" in source
    assert "expected exactly one pinned MiroFish image" in source
    assert "Kustomize and static policy" in source
    assert 'gh pr merge "$pr_number"' in source
    assert "APPS_GITOPS_TOKEN" in source
    assert "permission-checks: read" in source
    assert "permission-contents: write" not in source
    assert 'GH_TOKEN="$CHECKS_TOKEN" gh api' in source
    assert "contents: read" in source
