---
bump: patch
type: fix
---

Update the OpenTelemetry span name directly when `set_name` is used in
collector mode, instead of setting the `appsignal.name` attribute. The
collector uses the span name as-is, so names set this way were previously
ignored.
