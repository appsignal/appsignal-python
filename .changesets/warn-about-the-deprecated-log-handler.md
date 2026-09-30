---
bump: patch
type: add
---

AppSignal warns when your application attaches the OpenTelemetry log handler from `opentelemetry.sdk._logs`, which is deprecated and is removed in a future release of the OpenTelemetry SDK. Its replacement is in `opentelemetry.instrumentation.logging.handler`.
