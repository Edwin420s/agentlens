import pytest
from app.services.failure_grouper import _pick_severity


def test_pick_severity():
    failures = [{"severity": "medium"}, {"severity": "critical"}, {"severity": "low"}]
    assert _pick_severity(failures).value == "critical"
