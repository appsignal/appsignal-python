---
bump: "patch"
type: "add"
---

Add helper for reporting counter metrics to AppSignal using OpenTelemetry. Use these helpers to simplify sending counter metrics as supported by AppSignal.

```python
from appsignal import increment_counter

# Report a counter increasing
increment_counter("counter_name", 1)
# Report a counter decreasing
increment_counter("counter_name", -1)

# Add tags to counter
increment_counter("counter_with_tags", 1, {"tag1": "value1"})
```

Consult our documentation for more information about AppSignal's [custom metrics](https://docs.appsignal.com/metrics/custom.html).
