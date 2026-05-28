---
bump: patch
type: fix
---

Emit the `db.system.name` and `db.query.text` semantic-convention attributes
instead of `appsignal.sql_body` when `set_sql_body` is used in collector
mode. This fixes SQL query sanitization when using the experimental collector
mode. 
