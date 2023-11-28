---
bump: "patch"
type: "change"
---

Improve extraction of OpenTelemetry span details from the Requests library, by using the HTTP method, scheme, host and port as the event name. This improves grouping in the "Slow API requests" performance panel.
