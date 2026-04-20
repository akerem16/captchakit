"""Prometheus adapter for :class:`captchakit.metrics.MetricsSink`.

Requires the ``[metrics]`` extra::

    pip install "captchakit[metrics]"

Example::

    from prometheus_client import CollectorRegistry
    from captchakit.metrics_prometheus import PrometheusMetrics

    registry = CollectorRegistry()
    metrics = PrometheusMetrics(registry=registry)
    manager = CaptchaManager(..., metrics=metrics)
"""

from __future__ import annotations

from dataclasses import dataclass

try:
    from prometheus_client import REGISTRY, CollectorRegistry, Counter
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError(
        "PrometheusMetrics requires the `prometheus_client` package. "
        'Install with `pip install "captchakit[metrics]"`.'
    ) from exc


@dataclass
class PrometheusMetrics:
    """Exposes lifecycle events as Prometheus counters.

    Four counters are registered:

    - ``captchakit_issued_total``
    - ``captchakit_verified_total{result="success"|"fail"}``
    - ``captchakit_expired_total``
    - ``captchakit_too_many_attempts_total``

    Pass ``namespace`` to prefix metric names (useful when multiple
    captcha flows share a registry).
    """

    registry: CollectorRegistry | None = None
    namespace: str = "captchakit"

    def __post_init__(self) -> None:
        reg = self.registry if self.registry is not None else REGISTRY
        self._issued = Counter(
            f"{self.namespace}_issued_total",
            "Total captcha challenges issued.",
            registry=reg,
        )
        self._verified = Counter(
            f"{self.namespace}_verified_total",
            "Total captcha verification attempts.",
            ["result"],
            registry=reg,
        )
        self._expired = Counter(
            f"{self.namespace}_expired_total",
            "Total captcha challenges that reached TTL.",
            registry=reg,
        )
        self._too_many = Counter(
            f"{self.namespace}_too_many_attempts_total",
            "Total captcha challenges that exhausted max_attempts.",
            registry=reg,
        )

    def on_issue(self) -> None:
        self._issued.inc()

    def on_verify_success(self) -> None:
        self._verified.labels(result="success").inc()

    def on_verify_fail(self) -> None:
        self._verified.labels(result="fail").inc()

    def on_expired(self) -> None:
        self._expired.inc()

    def on_too_many_attempts(self) -> None:
        self._too_many.inc()


__all__ = ["PrometheusMetrics"]
