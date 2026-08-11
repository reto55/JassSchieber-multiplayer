---
type: JavaScript Function
title: refresh
resource: ausbau/html5/js/lobby.js#L75-L90
generated:
  by: okf-rs/0.3.0
relationships:
  calls:
  - functions/ausbau/html5/js/lobby/refreshMembership
  - functions/ausbau/html5/js/lobby/render
  - functions/ausbau/html5/js/lobby/roomGone
  - functions/ausbau/html5/js/lobby/showRoomGone
  called_by:
  - functions/ausbau/html5/js/lobby/render
  - functions/ausbau/html5/js/lobby/handleWsMessage
  - functions/frontend/auth/manager/UserManager/on_after_register
---

# Signature

`async function refresh()`

# Calls

- [refreshMembership](../../../../../functions/ausbau/html5/js/lobby/refreshMembership.md)
- [render](../../../../../functions/ausbau/html5/js/lobby/render.md)
- [roomGone](../../../../../functions/ausbau/html5/js/lobby/roomGone.md)
- [showRoomGone](../../../../../functions/ausbau/html5/js/lobby/showRoomGone.md)

# Called by

- [render](../../../../../functions/ausbau/html5/js/lobby/render.md)
- [handleWsMessage](../../../../../functions/ausbau/html5/js/lobby/handleWsMessage.md)
- [on_after_register](../../../../../functions/frontend/auth/manager/UserManager/on_after_register.md)