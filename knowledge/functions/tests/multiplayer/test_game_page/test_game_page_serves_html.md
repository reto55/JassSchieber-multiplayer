---
type: Python Function
title: test_game_page_serves_html
resource: tests/multiplayer/test_game_page.py#L24-L32
generated:
  by: okf-rs/0.3.0
---

# Signature

`async def test_game_page_serves_html(client): # `/` redirects to `/home` when no ?code= is present; the game page # itself is served at `/?code=…` (or any path with the code param).`