---
bump: "minor"
type: "add"
---

_Heartbeats are currently only available to beta testers. If you are interested in trying it out, [send an email to support@appsignal.com](mailto:support@appsignal.com?subject=Heartbeat%20beta)!_

---

Add heartbeats support. You can use the `heartbeat` function to send heartbeats directly from your code, to track the execution of certain processes:

```python
from appsignal import heartbeat

def send_invoices():
  # ... your code here ...
  heartbeat("send_invoices")
```

It is also possible to pass a defined function as an argument to the `heartbeat`
function:

```python
def send_invoices():
  # ... your code here ...

heartbeat("send_invoices", send_invoices)
```

If an exception is raised within the function, the finish event will not be
reported to AppSignal, triggering a notification about the missing heartbeat.
The exception will be raised outside of the heartbeat function.
