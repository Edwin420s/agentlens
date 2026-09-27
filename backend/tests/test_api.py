import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_health():
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["status"] == "ok"


def test_app_routes():
    route_paths = [r.path for r in app.routes]
    expected_routes = [
        "/health",
        "/api/v1/investigations",
        "/api/v1/investigations/{investigation_id}",
        "/api/v1/investigations/{investigation_id}/evaluation",
        "/api/v1/datasets/import",
        "/api/v1/datasets",
        "/api/v1/investigations/{investigation_id}/sessions",
        "/api/v1/sessions/{session_id}",
        "/api/v1/investigations/{investigation_id}/failures",
        "/api/v1/failures/{failure_id}",
        "/api/v1/investigations/{investigation_id}/groups",
        "/api/v1/groups/{group_id}",
        "/api/v1/investigations/{investigation_id}/dashboard",
        "/api/v1/investigations/{investigation_id}/assistant",
        "/api/v1/investigations/{investigation_id}/export",
    ]
    for r in expected_routes:
        assert r in route_paths, f"Missing route: {r}"


def test_endpoints_end_to_end():
    with TestClient(app) as client:
        # 0. Import dataset
        demo_path = Path(__file__).parent.parent / "data" / "demo_dataset.json"
        payload = json.loads(demo_path.read_text(encoding="utf-8"))
        import_resp = client.post("/api/v1/datasets/import", json=payload)
        assert import_resp.status_code == 200
        assert import_resp.json()["success"] is True
        inv_id = import_resp.json()["data"]["investigation_id"]

        # 1. List investigations
        inv_resp = client.get("/api/v1/investigations")
        assert inv_resp.status_code == 200
        inv_data = inv_resp.json()
        assert inv_data["success"] is True
        assert len(inv_data["data"]) > 0

        # 2. Get investigation
        single_inv = client.get(f"/api/v1/investigations/{inv_id}")
        assert single_inv.status_code == 200
        assert single_inv.json()["data"]["investigation_id"] == inv_id

        # 3. Dashboard
        dash = client.get(f"/api/v1/investigations/{inv_id}/dashboard")
        assert dash.status_code == 200
        dash_data = dash.json()["data"]
        assert dash_data["investigation_id"] == inv_id
        assert dash_data["summary"]["total_sessions"] > 0

        # 4. Sessions
        sessions_resp = client.get(f"/api/v1/investigations/{inv_id}/sessions")
        assert sessions_resp.status_code == 200
        sessions = sessions_resp.json()["data"]
        assert len(sessions) > 0
        first_session_id = sessions[0]["session_id"]

        # 5. Session Detail
        sess_detail = client.get(f"/api/v1/sessions/{first_session_id}")
        assert sess_detail.status_code == 200
        assert sess_detail.json()["data"]["session"]["session_id"] == first_session_id

        # 6. Failures
        failures_resp = client.get(f"/api/v1/investigations/{inv_id}/failures")
        assert failures_resp.status_code == 200
        failures = failures_resp.json()["data"]
        assert len(failures) > 0
        first_fail_id = failures[0]["failure_id"]

        # 7. Failure Detail
        fail_detail = client.get(f"/api/v1/failures/{first_fail_id}")
        assert fail_detail.status_code == 200
        assert fail_detail.json()["data"]["failure"]["failure_id"] == first_fail_id

        # 8. Groups
        groups_resp = client.get(f"/api/v1/investigations/{inv_id}/groups")
        assert groups_resp.status_code == 200
        groups = groups_resp.json()["data"]
        assert len(groups) > 0
        first_group_id = groups[0]["group_id"]

        # 9. Group Detail
        group_detail = client.get(f"/api/v1/groups/{first_group_id}")
        assert group_detail.status_code == 200
        assert group_detail.json()["data"]["group"]["group_id"] == first_group_id
        assert len(group_detail.json()["data"]["failures"]) > 0

        # 9b. Failure-groups alias
        fg_resp = client.get(f"/api/v1/investigations/{inv_id}/failure-groups")
        assert fg_resp.status_code == 200
        fg_detail = client.get(f"/api/v1/failure-groups/{first_group_id}")
        assert fg_detail.status_code == 200
        assert fg_detail.json()["data"]["group"]["group_id"] == first_group_id

        # 10. Assistant
        assist_resp = client.post(
            f"/api/v1/investigations/{inv_id}/assistant",
            json={"question": "What are the common failures?"},
        )
        assert assist_resp.status_code == 200
        assert assist_resp.json()["success"] is True

        # 11. Export
        export_resp = client.get(f"/api/v1/investigations/{inv_id}/export?format=json")
        assert export_resp.status_code == 200
        assert export_resp.json()["data"]["format"] == "json"

        export_csv = client.get(f"/api/v1/investigations/{inv_id}/export?format=csv")
        assert export_csv.status_code == 200
        assert export_csv.json()["data"]["format"] == "csv"

        # 12. Evaluation
        eval_resp = client.get(f"/api/v1/investigations/{inv_id}/evaluation")
        assert eval_resp.status_code == 200
        eval_data = eval_resp.json()["data"]
        assert "confusion" in eval_data
        assert eval_data["sessions_evaluated"] > 0

        # 13. Datasets listing
        ds_resp = client.get("/api/v1/datasets")
        assert ds_resp.status_code == 200
        assert len(ds_resp.json()["data"]) > 0
