from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from captchakit import (
    CaptchaManager,
    ChallengeExpired,
    ImageRenderer,
    MemoryStorage,
    MetricsSink,
    NoOpMetrics,
    TextChallengeFactory,
    TooManyAttempts,
)

from .conftest import FakeClock


@dataclass
class RecordingMetrics:
    events: list[str] = field(default_factory=list)

    def on_issue(self) -> None:
        self.events.append("issue")

    def on_verify_success(self) -> None:
        self.events.append("success")

    def on_verify_fail(self) -> None:
        self.events.append("fail")

    def on_expired(self) -> None:
        self.events.append("expired")

    def on_too_many_attempts(self) -> None:
        self.events.append("too_many")


def test_noop_is_a_metrics_sink() -> None:
    assert isinstance(NoOpMetrics(), MetricsSink)


async def test_happy_path_records_issue_and_success(clock: FakeClock) -> None:
    metrics = RecordingMetrics()
    mgr = CaptchaManager(
        factory=TextChallengeFactory(length=4),
        renderer=ImageRenderer(width=120, height=40, font_size=20),
        storage=MemoryStorage(clock=clock),
        ttl=30.0,
        clock=clock,
        metrics=metrics,
    )
    cid, _ = await mgr.issue()
    ch = await mgr.storage.get(cid)
    assert ch is not None
    await mgr.verify(cid, ch.solution)
    assert metrics.events == ["issue", "success"]


async def test_fail_and_too_many(clock: FakeClock) -> None:
    metrics = RecordingMetrics()
    mgr = CaptchaManager(
        factory=TextChallengeFactory(length=4),
        renderer=ImageRenderer(width=120, height=40, font_size=20),
        storage=MemoryStorage(clock=clock),
        ttl=30.0,
        max_attempts=2,
        clock=clock,
        metrics=metrics,
    )
    cid, _ = await mgr.issue()
    await mgr.verify(cid, "nope")
    with pytest.raises(TooManyAttempts):
        await mgr.verify(cid, "nope-again")
    assert metrics.events == ["issue", "fail", "fail", "too_many"]


async def test_expired_records(clock: FakeClock) -> None:
    metrics = RecordingMetrics()
    mgr = CaptchaManager(
        factory=TextChallengeFactory(length=4),
        renderer=ImageRenderer(width=120, height=40, font_size=20),
        storage=MemoryStorage(clock=clock),
        ttl=10.0,
        clock=clock,
        metrics=metrics,
    )
    cid, _ = await mgr.issue()
    clock.advance(11.0)
    with pytest.raises(ChallengeExpired):
        await mgr.verify(cid, "x")
    assert metrics.events == ["issue", "expired"]


def test_prometheus_adapter_counts() -> None:
    prometheus_client = pytest.importorskip("prometheus_client")
    from captchakit.metrics_prometheus import PrometheusMetrics  # noqa: PLC0415

    registry = prometheus_client.CollectorRegistry()
    m = PrometheusMetrics(registry=registry, namespace="test_ck")
    m.on_issue()
    m.on_issue()
    m.on_verify_success()
    m.on_verify_fail()
    m.on_expired()
    m.on_too_many_attempts()

    assert registry.get_sample_value("test_ck_issued_total") == 2.0
    assert registry.get_sample_value("test_ck_verified_total", {"result": "success"}) == 1.0
    assert registry.get_sample_value("test_ck_verified_total", {"result": "fail"}) == 1.0
    assert registry.get_sample_value("test_ck_expired_total") == 1.0
    assert registry.get_sample_value("test_ck_too_many_attempts_total") == 1.0
