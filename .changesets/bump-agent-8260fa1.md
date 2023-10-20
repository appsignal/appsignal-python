---
bump: "patch"
type: "change"
---

Bump agent to 8260fa1

- Add `appsignal.sql_body` magic span attribute for OpenTelemetry spans. When this attribute is detected, we store the value as the span/event body. This span is sanitized beforehand so it doesn't contain any sensitive data and helps to group events in our backend. When used in combination with the `appsignal.body` attribute, the new `appsignal.sql_body` attribute is leading.

  More information on [AppSignal OpenTelemetry span attributes](https://docs.appsignal.com/opentelemetry/custom-instrumentation/attributes.html) can be found in our docs.
