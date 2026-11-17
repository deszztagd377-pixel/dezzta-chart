from pathlib import Path
import re


def test_frontend_dependency_audit_runs_diagnostics_before_final_enforcement():
    workflow_path = (
        Path(__file__).resolve().parents[2]
        / ".github"
        / "workflows"
        / "ci.yml"
    )
    workflow = workflow_path.read_text(encoding="utf-8")

    audit_match = re.search(
        r"(?ms)^      - name: Audit frontend dependencies\n(?P<body>.*?)(?=^      - name:|\Z)",
        workflow,
    )
    enforcement_match = re.search(
        r"(?ms)^      - name: Enforce frontend dependency audit result\n(?P<body>.*?)(?=^      - name:|\Z)",
        workflow,
    )

    assert audit_match is not None
    assert enforcement_match is not None
    assert "id: frontend_dependency_audit" in audit_match.group("body")
    assert "continue-on-error: true" in audit_match.group("body")
    assert "run: npm audit --audit-level=high" in audit_match.group("body")

    enforcement = enforcement_match.group("body")
    assert "if: always()" in enforcement
    assert "steps.frontend_dependency_audit.outcome" in enforcement
    assert "exit 1" in enforcement
    assert "npm audit" in workflow
    assert workflow.index("Enforce frontend dependency audit result") > workflow.index(
        "Upload container vulnerability reports"
    )
