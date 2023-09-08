---
bump: "patch"
type: "add"
---

Add helper for reporting gauge metrics to AppSignal using OpenTelemetry. Use these helpers to simplify sending gauge metrics as supported by AppSignal.

```python
from appsignal import set_gauge

# Report a gauge value
set_gauge("gauge_name", 10)

# Add tags to metrics
set_gauge("gauge_with_tags", 10, {"tag1": "value1"})
```

Consult our documentation for more information about AppSignal's [custom metrics](https://docs.appsignal.com/metrics/custom.html).
