---
bump: patch
type: fix
---

Ensure that data sent for check-ins, to an external collector, or via the agent always honors the `http_proxy` configuration option and the `APPSIGNAL_HTTP_PROXY` environment variable first, falling back to the `HTTP_PROXY` and `HTTPS_PROXY` environment variables if the configuration option is unset, and always ignores the `NO_PROXY` environment variable.
