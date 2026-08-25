---
bump: patch
type: change
---

On Heroku, report the name of the dyno as the hostname. Before, the hostname of the container that the dyno runs in was reported, so applications running on Heroku will see their data reported under a new host name.
