---
bump: "patch"
type: "add"
---

Add distribution value custom metric helper. This can be used to add values to distributions in the same way as in our other integrations:

```python
# Import the AppSignal metric helper
from appsignal import add_distribution_value

# The first argument is a string, the second argument a number (int/float)
# add_distribution_value(metric_name, value)
add_distribution_value("memory_usage", 100)
add_distribution_value("memory_usage", 110)

# Will create a metric "memory_usage" with the mean field value 105
# Will create a metric "memory_usage" with the count field value 2
```
