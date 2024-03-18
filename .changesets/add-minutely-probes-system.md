---
bump: "minor"
type: "add"
---

Add a minutely probes system. This can be used, alongside our metric helpers, to report metrics to AppSignal once per minute.

```python
from appsignal import probes, set_gauge

def new_carts(previous_carts=None):
    current_carts = Cart.objects.all().count()

    if previous_carts is not None:
      set_gauge("new_carts", current_carts - previous_carts)

    return current_carts

probes.register("new_carts", new_carts)
```

The minutely probes system starts by default, but no probes are automatically registered. You can use the `enable_minutely_probes` configuration option to disable it.
