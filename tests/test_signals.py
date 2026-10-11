"""Tests for core/observe/signals.py. Mocked - no network calls to Raindrop.
Owner: Talal (T3). Reviewer: Shiv.
"""
import json
import logging

import pytest

from core.observe import signals


class FakeRaindrop:
    """Stands in for raindrop.analytics. init()/track_ai()/track_signal() match
    the real module's call signatures closely enough for signals.py's usage."""

    def __init__(self, fail: bool = False):
        self.fail = fail
        self.init_calls: list = []
        self.track_ai_calls: list = []
        self.track_signal_calls: list = []

    def init(self, key):
        self.init_calls.append(key)

    def track_ai(self, **kwargs):
        if self.fail:
            raise RuntimeError("boom")
        self.track_ai_calls.append(kwargs)
        return "fake-event-id"

    def track_signal(self, **kwargs):
        if self.fail:
            raise RuntimeError("boom")
        self.track_signal_calls.append(kwargs)


@pytest.fixture(autouse=True)
def reset_initialized(monkeypatch):
    # send() only calls raindrop.init() once per process; force it to run
    # again for every test regardless of what a previous test left behind.
    monkeypatch.setattr(signals, "_initialized", False)


def test_no_key_does_not_call_sdk_and_logs_warning(monkeypatch, caplog):
    monkeypatch.delenv("RAINDROP_WRITE_KEY", raising=False)
    fake = FakeRaindrop()
    monkeypatch.setattr(signals, "raindrop", fake)

    with caplog.at_level(logging.WARNING):
        signals.send("attempt_logged", {"session_id": "s1"})

    assert fake.track_ai_calls == []
    assert fake.track_signal_calls == []
    assert any("RAINDROP_WRITE_KEY" in r.message for r in caplog.records)


def test_sdk_failure_does_not_raise_and_logs_warning(monkeypatch, caplog):
    monkeypatch.setenv("RAINDROP_WRITE_KEY", "test-key")
    fake = FakeRaindrop(fail=True)
    monkeypatch.setattr(signals, "raindrop", fake)

    with caplog.at_level(logging.WARNING):
        signals.send("attempt_logged", {"session_id": "s1"})  # must not raise

    assert any("attempt_logged" in r.message for r in caplog.records)


def test_nested_payload_is_flattened(monkeypatch):
    monkeypatch.setenv("RAINDROP_WRITE_KEY", "test-key")
    fake = FakeRaindrop()
    monkeypatch.setattr(signals, "raindrop", fake)

    payload = {
        "session_id": "s1",
        "audit": {"sr": 1.2, "pass_total": True},
        "tags": ["a", "b"],
        "note": None,
    }
    signals.send("audit_pass", payload)

    sent = fake.track_ai_calls[0]["properties"]
    assert sent["audit.sr"] == 1.2
    assert sent["audit.pass_total"] is True
    assert sent["tags"] == json.dumps(["a", "b"], default=str)
    assert "note" not in sent
    assert fake.track_signal_calls[0]["properties"] == sent


def test_secret_keys_are_dropped(monkeypatch):
    monkeypatch.setenv("RAINDROP_WRITE_KEY", "test-key")
    fake = FakeRaindrop()
    monkeypatch.setattr(signals, "raindrop", fake)

    payload = {
        "session_id": "s1",
        "mongodb_uri": "mongodb+srv://user:pass@host",
        "api_key": "sk-abc123",
        "password": "hunter2",
        "auth": {"token": "xyz"},
    }
    signals.send("blocked_query", payload)

    sent = fake.track_ai_calls[0]["properties"]
    assert sent == {"session_id": "s1"}


def test_unknown_kind_raises_value_error():
    with pytest.raises(ValueError):
        signals.send("not_a_real_kind", {})


def test_all_contracts_kinds_are_accepted(monkeypatch):
    monkeypatch.setenv("RAINDROP_WRITE_KEY", "test-key")
    fake = FakeRaindrop()
    monkeypatch.setattr(signals, "raindrop", fake)

    for kind in signals.KINDS:
        signals.send(kind, {"session_id": "s1"})

    sent_events = {call["event"] for call in fake.track_ai_calls}
    assert sent_events == signals.KINDS
