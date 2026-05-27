---
bump: patch
type: fix
integrations: all
---

Emit the `appsignal.action_name` attribute instead of `appsignal.root_name`
when `set_root_name` is used in collector mode. The collector only reads the
action name from `appsignal.action_name`, so root names set this way were
previously ignored, falling back to the OpenTelemetry span name.
