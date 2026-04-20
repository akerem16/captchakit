# Metrics

`captchakit` emits one event per lifecycle transition so you can wire it
into any observability stack without patching the core.

## `MetricsSink` protocol

```python
class MetricsSink(Protocol):
    def on_issue(self) -> None: ...
    def on_verify_success(self) -> None: ...
    def on_verify_fail(self) -> None: ...
    def on_expired(self) -> None: ...
    def on_too_many_attempts(self) -> None: ...
```

All callbacks are synchronous and must not block. If you need to do I/O
(push to a remote aggregator, write to disk), buffer locally and flush
from a background task.

The default sink is `NoOpMetrics` — zero cost, no setup.

## Prometheus

```bash
pip install "captchakit[metrics]"
```

```python
from prometheus_client import CollectorRegistry, start_http_server
from captchakit import CaptchaManager, ImageRenderer, MemoryStorage, TextChallengeFactory
from captchakit.metrics_prometheus import PrometheusMetrics

registry = CollectorRegistry()
metrics = PrometheusMetrics(registry=registry)
start_http_server(9090, registry=registry)

manager = CaptchaManager(
    factory=TextChallengeFactory(),
    renderer=ImageRenderer(),
    storage=MemoryStorage(),
    metrics=metrics,
)
```

Exported series:

| Metric                                       | Type    |
| -------------------------------------------- | ------- |
| `captchakit_issued_total`                    | Counter |
| `captchakit_verified_total{result=success}`  | Counter |
| `captchakit_verified_total{result=fail}`     | Counter |
| `captchakit_expired_total`                   | Counter |
| `captchakit_too_many_attempts_total`         | Counter |

Pass `namespace="myapp"` to `PrometheusMetrics` to rename the prefix.

## Custom sinks

Implement the protocol with plain Python — no subclassing required.

```python
class StatsDMetrics:
    def __init__(self, client): self._c = client
    def on_issue(self): self._c.incr("captcha.issued")
    def on_verify_success(self): self._c.incr("captcha.verified.success")
    def on_verify_fail(self): self._c.incr("captcha.verified.fail")
    def on_expired(self): self._c.incr("captcha.expired")
    def on_too_many_attempts(self): self._c.incr("captcha.too_many")
```
