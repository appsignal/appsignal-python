---
bump: patch
type: fix
---

Report a request or response header whose name is written with capital letters or underscores in the `request_headers` or `response_headers` configuration option, such as `Content-Type` or `content_type`. The collector matches these names against the ones it receives the headers under, which follow the OpenTelemetry semantic convention: the header's own name, lowercased, with its dashes kept. A name written any other way matched nothing, so the header was left out.

The `set_header` helper names a header the same way when a collector is in use.
