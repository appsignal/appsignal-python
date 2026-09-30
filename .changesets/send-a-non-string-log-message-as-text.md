---
bump: minor
type: change
---

A log message that is not a string, such as the dictionary in `logger.info({"message": "Order placed", "order_id": 1234})`, is sent as text by the `logging` instrumentation. Pass the structured values in the `extra` argument to send a structured log line:

```python
logger.info("Order placed", extra={"order_id": 1234})
```

[The OpenTelemetry logs API](https://docs.appsignal.com/logging/integrations/python#sending-logs-with-opentelemetry) sends a structured log line from a dictionary body.
