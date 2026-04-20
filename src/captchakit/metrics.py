"""Metrics hooks.

A pluggable :class:`MetricsSink` receives one call per lifecycle event
(issue, verify success/fail, expiration, too-many-attempts) so callers
can wire captchakit into Prometheus, StatsD, OpenTelemetry, or anything
else.

The default :class:`NoOpMetrics` is a zero-cost stub; the
:class:`PrometheusMetrics` adapter lives in
:mod:`captchakit.metrics_prometheus` and requires the ``[metrics]``
extra.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class MetricsSink(Protocol):
    """Receives captchakit lifecycle events.

    Every callback is synchronous and must not block: it runs on the
    event loop thread. If you need to do I/O (push to a remote aggregator,
    write to disk), buffer locally and flush from a background task.
    """

    def on_issue(self) -> None: ...

    def on_verify_success(self) -> None: ...

    def on_verify_fail(self) -> None: ...

    def on_expired(self) -> None: ...

    def on_too_many_attempts(self) -> None: ...


class NoOpMetrics:
    """Default sink — all methods are no-ops."""

    __slots__ = ()

    def on_issue(self) -> None:
        return None

    def on_verify_success(self) -> None:
        return None

    def on_verify_fail(self) -> None:
        return None

    def on_expired(self) -> None:
        return None

    def on_too_many_attempts(self) -> None:
        return None


__all__ = ["MetricsSink", "NoOpMetrics"]
