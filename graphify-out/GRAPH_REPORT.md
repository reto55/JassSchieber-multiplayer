# Graph Report - .  (2026-05-06)

## Corpus Check
- 64 files · ~181,101 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 574 nodes · 1273 edges · 90 communities detected
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 194 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Frontend WebSocket client|Frontend WebSocket client]]
- [[_COMMUNITY_GameSession state machine|GameSession state machine]]
- [[_COMMUNITY_server.py|server.py]]
- [[_COMMUNITY_jquery-1.6.min.js|jquery-1.6.min.js]]
- [[_COMMUNITY_database_manager.py|database_manager.py]]
- [[_COMMUNITY_Cards_refactored.py|Cards_refactored.py]]
- [[_COMMUNITY_room.py|room.py]]
- [[_COMMUNITY_db_utils.py|db_utils.py]]
- [[_COMMUNITY_insert.py|insert.py]]
- [[_COMMUNITY_db_adapter.py|db_adapter.py]]
- [[_COMMUNITY_Auth base.html Jinja layout|Auth base.html Jinja layout]]
- [[_COMMUNITY_email.py|email.py]]
- [[_COMMUNITY_game_session.py|game_session.py]]
- [[_COMMUNITY_models.py|models.py]]
- [[_COMMUNITY_lobby.js|lobby.js]]
- [[_COMMUNITY_ai_strategies.py|ai_strategies.py]]
- [[_COMMUNITY_Cards_refactored.py|Cards_refactored.py]]
- [[_COMMUNITY_ai_strategies.py|ai_strategies.py]]
- [[_COMMUNITY_card_utils.py|card_utils.py]]
- [[_COMMUNITY_schieber_json.py|schieber_json.py]]
- [[_COMMUNITY_home.js|home.js]]
- [[_COMMUNITY_guest.py|guest.py]]
- [[_COMMUNITY_game.html|game.html]]
- [[_COMMUNITY_game_utils.py|game_utils.py]]
- [[_COMMUNITY_db.py|db.py]]
- [[_COMMUNITY_Card Class Hierarchy (core)|Card Class Hierarchy (core)]]
- [[_COMMUNITY_deps.py|deps.py]]
- [[_COMMUNITY_admin.html|admin.html]]
- [[_COMMUNITY_html5jass.matchjass.js|html5jass.matchjass.js]]
- [[_COMMUNITY_lobby.html|lobby.html]]
- [[_COMMUNITY_CLAUDE|CLAUDE.md]]
- [[_COMMUNITY_users.py|users.py]]
- [[_COMMUNITY_database_manager.py|database_manager.py]]
- [[_COMMUNITY_html5games.matchgame.js|html5games.matchgame.js]]
- [[_COMMUNITY_example.py|example.py]]
- [[_COMMUNITY_Cards_refactored.py|Cards_refactored.py]]
- [[_COMMUNITY_settings.py|settings.py]]
- [[_COMMUNITY_schieber.py|schieber.py]]
- [[_COMMUNITY_Frontend WebSocket client|Frontend WebSocket client]]
- [[_COMMUNITY_schemas.py|schemas.py]]
- [[_COMMUNITY_CLAUDE|CLAUDE.md]]
- [[_COMMUNITY_DatabaseManager OOP class|DatabaseManager OOP class]]
- [[_COMMUNITY_ai_strategies.py|ai_strategies.py]]
- [[_COMMUNITY_lockout.py|lockout.py]]
- [[_COMMUNITY_tombstone.py|tombstone.py]]
- [[_COMMUNITY_game.js|game.js]]
- [[_COMMUNITY_html5games.pingpong.js|html5games.pingpong.js]]
- [[_COMMUNITY_CLAUDE|CLAUDE.md]]
- [[_COMMUNITY_IMPORTS_README|IMPORTS_README.md]]
- [[_COMMUNITY_Shared csrfHeaders JS constant|Shared csrfHeaders JS constant]]
- [[_COMMUNITY_Sub-project B — User accounts|Sub-project B — User accounts]]
- [[_COMMUNITY_manager.py|manager.py]]
- [[_COMMUNITY_Cards_refactored.py|Cards_refactored.py]]
- [[_COMMUNITY_ratelimit.py|ratelimit.py]]
- [[_COMMUNITY_._compute_ai_action()|._compute_ai_action()]]
- [[_COMMUNITY_Cards_refactored.py|Cards_refactored.py]]
- [[_COMMUNITY_jquery-1.6.min.js|jquery-1.6.min.js]]
- [[_COMMUNITY_Cards_refactored.py|Cards_refactored.py]]
- [[_COMMUNITY_SmtpMailBackend|SmtpMailBackend]]
- [[_COMMUNITY_connect()|connect()]]
- [[_COMMUNITY_Sechs|Sechs]]
- [[_COMMUNITY_Ass|Ass]]
- [[_COMMUNITY_Koenig|Koenig]]
- [[_COMMUNITY_Banner|Banner]]
- [[_COMMUNITY_Acht|Acht]]
- [[_COMMUNITY_ConsoleMailBackend|ConsoleMailBackend]]
- [[_COMMUNITY_db_migration.py|db_migration.py]]
- [[_COMMUNITY_detect_stock()|detect_stock()]]
- [[_COMMUNITY_bZ()|bZ()]]
- [[_COMMUNITY_bj()|bj()]]
- [[_COMMUNITY_bootAuth()|bootAuth()]]
- [[_COMMUNITY_Dev test dependencies (pytest, pytest-as|Dev test dependencies (pytest, pytest-as]]
- [[_COMMUNITY_GET authme endpoint|GET /auth/me endpoint]]
- [[_COMMUNITY_db_adapter compatibility layer|db_adapter compatibility layer]]
- [[_COMMUNITY_DeclarativeBase|DeclarativeBase]]
- [[_COMMUNITY_K()|K()]]
- [[_COMMUNITY_cf()|cf()]]
- [[_COMMUNITY__rate_limit_handler()|_rate_limit_handler()]]
- [[_COMMUNITY_bh()|bh()]]
- [[_COMMUNITY_bf()|bf()]]
- [[_COMMUNITY_onWeisRequest()|onWeisRequest()]]
- [[_COMMUNITY_onTrumpRequest()|onTrumpRequest()]]
- [[_COMMUNITY_teamOf()|teamOf()]]
- [[_COMMUNITY_computeLayout()|computeLayout()]]
- [[_COMMUNITY_E()|E()]]
- [[_COMMUNITY_H()|H()]]
- [[_COMMUNITY_lobby_page()|lobby_page()]]
- [[_COMMUNITY__start_reaper()|_start_reaper()]]
- [[_COMMUNITY_Protocol|Protocol]]
- [[_COMMUNITY_home_page()|home_page()]]

## God Nodes (most connected - your core abstractions)
1. `GameSession` - 38 edges
2. `DatabaseManager` - 29 edges
3. `appendLog()` - 24 edges
4. `principal_id()` - 19 edges
5. `Card` - 18 edges
6. `_get_principal()` - 15 edges
7. `HardStrategy` - 13 edges
8. `get_room()` - 12 edges
9. `leave_endpoint()` - 12 edges
10. `get_db_manager()` - 12 edges

## Surprising Connections (you probably didn't know these)
- `DatabaseManager` --references--> `DatabaseManager context-manager pattern`  [INFERRED]
  /mnt/archive/Dokumente/JassSchieber-multiplayer/ausbau/database_manager.py → ausbau/DB_README.md
- `farbe_lang()` --references--> `farbe_lang() longest-suit selection`  [INFERRED]
  /mnt/archive/Dokumente/JassSchieber-multiplayer/utils/card_utils.py → CLAUDE.md
- `Schieben mechanic (push trump to partner)` --semantically_similar_to--> `Sub-project C — AI difficulty`  [INFERRED] [semantically similar]
  schieber.txt → CLAUDE.md
- `db_adapter compatibility layer` --semantically_similar_to--> `imports_new.py compatibility shim`  [INFERRED] [semantically similar]
  ausbau/DB_README.md → IMPORTS_README.md
- `Trump selection modal` --implements--> `Game modes (Eicheln/Rosen/Schellen/Schilten/Oben/Unten)`  [INFERRED]
  ausbau/html5/game.html → CLAUDE.md

## Hyperedges (group relationships)
- **Auth signup/login/reset flow templates** — signup_form, login_signin_form, forgot_password_form, reset_password_form, verify_done_page, account_identity_panel [INFERRED 0.90]
- **Multiplayer room UI flow (home -> lobby -> game)** — home_create_room_action, home_join_room_form, lobby_seats_section, lobby_actions, game_table, game_js_schieber [INFERRED 0.85]
- **Three Schieber sub-projects (multiplayer, accounts, AI difficulty)** — claudemd_subproject_a_multiplayer, claudemd_subproject_b_accounts, claudemd_subproject_c_ai_difficulty [EXTRACTED 1.00]

## Communities

### Community 0 - "Frontend WebSocket client"
Cohesion: 0.23
Nodes (28): appendLog(), applyGameStartLikePayload(), dispatch(), onCardPlayed(), onError(), onGameEnd(), onGameStart(), onHostChanged() (+20 more)

### Community 1 - "GameSession state machine"
Cohesion: 0.29
Nodes (2): GameSession, list

### Community 2 - "server.py"
Cohesion: 0.38
Nodes (19): get_room(), principal_id(), ai_difficulty_endpoint(), create_room_endpoint(), _get_principal(), get_room_endpoint(), join_endpoint(), leave_endpoint() (+11 more)

### Community 3 - "jquery-1.6.min.js"
Cohesion: 0.18
Nodes (19): a(), bB(), bg(), bi(), bl(), bX(), bY(), cg() (+11 more)

### Community 4 - "database_manager.py"
Cohesion: 0.29
Nodes (4): DatabaseManager, demonstrate_basic_operations(), demonstrate_transaction(), migrate_database()

### Community 5 - "Cards_refactored.py"
Cohesion: 0.32
Nodes (12): calculate_wiis(), determine_longest_suit(), determine_trumpf(), determine_trumpf_after_schieben(), Neun, Ober, Sieben, sort_hand_desc() (+4 more)

### Community 6 - "room.py"
Cohesion: 0.32
Nodes (10): _close_room(), create_room(), find_rooms_for_principal(), make_code(), reap_rooms_once(), reaper_loop(), remove_room(), Seat (+2 more)

### Community 7 - "db_utils.py"
Cohesion: 0.28
Nodes (11): create_connection(), create_game(), create_play(), create_schieber(), create_spieler(), create_stich(), create_wwys(), create_wys() (+3 more)

### Community 8 - "insert.py"
Cohesion: 0.33
Nodes (10): create_connection(), create_game(), create_play(), create_schieber(), create_spieler(), create_stich(), create_wwys(), create_wys() (+2 more)

### Community 9 - "db_adapter.py"
Cohesion: 0.44
Nodes (10): create_connection(), create_game(), create_play(), create_schieber(), create_spieler(), create_stich(), create_wwys(), create_wys() (+2 more)

### Community 10 - "Auth base.html Jinja layout"
Cohesion: 0.29
Nodes (10): Auth base.html Jinja layout, POST /auth/forgot endpoint, Forgot password form, Auth strip on home, POST /auth/login endpoint, Sign-in form, POST /auth/reset endpoint, Password reset form (+2 more)

### Community 11 - "email.py"
Cohesion: 0.33
Nodes (7): Mail, MailBackend, mask_email(), render_change_email_confirm(), render_change_email_notice(), render_reset(), render_verification()

### Community 12 - "game_session.py"
Cohesion: 0.42
Nodes (8): ai_select_card(), card_to_code(), describe_weis(), determine_trick_winner(), find_card_in_hand(), get_valid_cards(), hand_to_codes(), trick_points()

### Community 13 - "models.py"
Cohesion: 0.44
Nodes (9): AccessToken, AdminAudit, Base, EmailToken, LockoutAttempt, _new_uuid(), _now_utc(), Tombstone (+1 more)

### Community 14 - "lobby.js"
Cohesion: 0.49
Nodes (8): api(), fetchWho(), handleWsMessage(), openWs(), refresh(), refreshMembership(), render(), withErrors()

### Community 15 - "ai_strategies.py"
Cohesion: 0.39
Nodes (5): EasyStrategy, make_strategy(), MediumStrategy, _split_code(), ValueError

### Community 16 - "Cards_refactored.py"
Cohesion: 0.31
Nodes (3): Hand, _move_cards(), Players

### Community 17 - "ai_strategies.py"
Cohesion: 0.39
Nodes (1): HardStrategy

### Community 18 - "card_utils.py"
Cohesion: 0.44
Nodes (7): add_card(), move_cards(), pop_card(), rsort_trumpf(), sort_oben(), sort_trumpf(), sort_unten()

### Community 19 - "schieber_json.py"
Cohesion: 0.36
Nodes (4): JSONObject, Point, serialize_instance(), unserialize_object()

### Community 20 - "home.js"
Cohesion: 0.57
Nodes (6): api(), bootAuth(), escapeHtml(), handleCreateRoom(), handleJoinRoom(), showError()

### Community 21 - "guest.py"
Cohesion: 0.61
Nodes (6): display_name(), Guest, GuestCookieError, issue_guest_cookie(), read_guest_cookie(), _serializer()

### Community 22 - "game.html"
Cohesion: 0.32
Nodes (8): schieber.js game client script, Game-over modal, Table area with trump badge and trick slots, Trump selection modal, Weis announcement modal, Schieber Jass rules (German description), Schieben mechanic (push trump to partner), Weisen card combinations

### Community 23 - "game_utils.py"
Cohesion: 0.46
Nodes (6): calculate_points(), check_game_end(), format_game_duration(), game_duration(), get_next_player(), get_winner()

### Community 24 - "db.py"
Cohesion: 0.43
Nodes (6): init_db(), make_engine(), make_session_factory(), _auth_init_db(), _build_auth_app(), _ensure_auth_initialised()

### Community 25 - "Card Class Hierarchy (core)"
Cohesion: 0.25
Nodes (1): Card

### Community 26 - "deps.py"
Cohesion: 0.43
Nodes (4): build_app(), make_current_principal_dep(), make_current_user_dep(), make_require_admin_dep()

### Community 27 - "admin.html"
Cohesion: 0.38
Nodes (5): GET /admin/audit endpoint, make_admin_router(), Admin user actions (ban/unban/promote/demote/force-verify), GET /admin/users endpoint, Admin users table

### Community 28 - "html5jass.matchjass.js"
Cohesion: 0.52
Nodes (5): checkPattern(), isMatchPattern(), removeTookCards(), selectCard(), shuffle()

### Community 29 - "lobby.html"
Cohesion: 0.38
Nodes (7): Create Room action, Join room form, home.js client script, Lobby action buttons (join/leave/spectate/start), lobby.js client script, Seats list UI, Target score controls (1000/2500)

### Community 30 - "CLAUDE.md"
Cohesion: 0.33
Nodes (7): Card subclass hierarchy (Ass/Koenig/Ober/Under/Banner/Neun/Acht/Sieben/Sechs), Game modes (Eicheln/Rosen/Schellen/Schilten/Oben/Unten), GameState singleton removed (rationale), Schieber agent harness, Schieber project overview, CARD_ATTRIBUTES static table, Uvicorn server start command

### Community 31 - "users.py"
Cohesion: 0.67
Nodes (5): make_auth_backend(), make_fastapi_users(), make_manager_dep(), make_token_db_dep(), make_user_db_dep()

### Community 32 - "database_manager.py"
Cohesion: 0.33
Nodes (1): demonstrate_context_manager()

### Community 33 - "html5games.matchgame.js"
Cohesion: 0.52
Nodes (5): checkPattern(), isMatchPattern(), removeTookCards(), selectCard(), shuffle()

### Community 34 - "example.py"
Cohesion: 0.57
Nodes (4): demo_card_utils(), demo_database_utils(), demo_game_utils(), main()

### Community 35 - "Cards_refactored.py"
Cohesion: 0.33
Nodes (1): Play

### Community 36 - "settings.py"
Cohesion: 0.53
Nodes (4): BaseSettings, load_settings(), secure_cookie(), Settings

### Community 37 - "schieber.py"
Cohesion: 0.67
Nodes (4): alter_table(), create_connection(), create_table(), main()

### Community 38 - "Frontend WebSocket client"
Cohesion: 0.33
Nodes (6): playCard(), send(), sendAnnounceWeis(), sendChooseTrump(), sendPlayCard(), sendSchieben()

### Community 39 - "schemas.py"
Cohesion: 0.53
Nodes (4): UserCreate, UserRead, UserUpdate, validate_email_address()

### Community 40 - "CLAUDE.md"
Cohesion: 0.33
Nodes (5): farbe_lang(), determine_trick_winner trick-winner logic, farbe_lang() longest-suit selection, Multiplayer room/seat model, Human hand area

### Community 41 - "DatabaseManager OOP class"
Cohesion: 0.47
Nodes (6): SQLite schema (schieber/game/play/spieler/stich/wys/wwys), Team layout (compo/compn/compe/comps; SN vs OW), create_play / create_game / create_stich / create_wys snippet, DatabaseManager context-manager pattern, DatabaseManager OOP class, AI bar (4 player slots + score panel)

### Community 42 - "ai_strategies.py"
Cohesion: 0.33
Nodes (1): AIStrategy

### Community 43 - "lockout.py"
Cohesion: 0.6
Nodes (3): clear_email_streak(), is_locked_out(), record_attempt()

### Community 44 - "tombstone.py"
Cohesion: 0.6
Nodes (2): hash_email(), hash_username()

### Community 45 - "game.js"
Cohesion: 0.6
Nodes (3): isMatchPattern(), removeTookCards(), selectCard()

### Community 46 - "html5games.pingpong.js"
Cohesion: 0.8
Nodes (3): gameloop(), moveBall(), movePaddless()

### Community 47 - "CLAUDE.md"
Cohesion: 0.5
Nodes (5): Sub-project A — Networked multiplayer, Sub-project C — AI difficulty, Game variants trumpf_bock/match_bonus/stoeck, Variant selection list, Session resume handoff notes

### Community 48 - "IMPORTS_README.md"
Cohesion: 0.4
Nodes (5): card_utils module, db_utils module, Explicit imports replacing wildcards, game_utils module, Modular utils package structure

### Community 49 - "Shared csrfHeaders JS constant"
Cohesion: 0.67
Nodes (3): Change email form, Change password form, Shared csrfHeaders JS constant

### Community 50 - "Sub-project B — User accounts"
Cohesion: 0.5
Nodes (4): Delete account form, Export data link, Sub-project B — User accounts, Email verified confirmation page

### Community 51 - "manager.py"
Cohesion: 0.5
Nodes (1): UserManager

### Community 52 - "Cards_refactored.py"
Cohesion: 0.67
Nodes (1): Suit

### Community 53 - "ratelimit.py"
Cohesion: 0.67
Nodes (1): make_limiter()

### Community 54 - "._compute_ai_action()"
Cohesion: 0.67
Nodes (1): index()

### Community 55 - "Cards_refactored.py"
Cohesion: 0.67
Nodes (2): _add_card(), _pop_card()

### Community 57 - "jquery-1.6.min.js"
Cohesion: 0.67
Nodes (3): b_(), N(), W()

### Community 58 - "Cards_refactored.py"
Cohesion: 0.67
Nodes (2): create_card(), Deck

### Community 59 - "SmtpMailBackend"
Cohesion: 1.0
Nodes (1): SmtpMailBackend

### Community 60 - "connect()"
Cohesion: 1.0
Nodes (2): connect(), wsUrl()

### Community 61 - "Sechs"
Cohesion: 1.0
Nodes (1): Sechs

### Community 62 - "Ass"
Cohesion: 1.0
Nodes (1): Ass

### Community 63 - "Koenig"
Cohesion: 1.0
Nodes (1): Koenig

### Community 64 - "Banner"
Cohesion: 1.0
Nodes (1): Banner

### Community 65 - "Acht"
Cohesion: 1.0
Nodes (1): Acht

### Community 66 - "ConsoleMailBackend"
Cohesion: 1.0
Nodes (1): ConsoleMailBackend

### Community 67 - "db_migration.py"
Cohesion: 1.0
Nodes (1): db_migration tool

### Community 68 - "detect_stock()"
Cohesion: 1.0
Nodes (1): detect_stock()

### Community 69 - "bZ()"
Cohesion: 1.0
Nodes (2): bZ(), D()

### Community 70 - "bj()"
Cohesion: 1.0
Nodes (2): bj(), bk()

### Community 71 - "bootAuth()"
Cohesion: 1.0
Nodes (2): bootAuth(), escapeHtml()

### Community 72 - "Dev test dependencies (pytest, pytest-as"
Cohesion: 1.0
Nodes (2): Dev test dependencies (pytest, pytest-asyncio, httpx), HTML5 server runtime dependencies

### Community 73 - "GET /auth/me endpoint"
Cohesion: 1.0
Nodes (2): GET /auth/me endpoint, Account identity panel

### Community 74 - "db_adapter compatibility layer"
Cohesion: 1.0
Nodes (2): db_adapter compatibility layer, imports_new.py compatibility shim

### Community 77 - "DeclarativeBase"
Cohesion: 1.0
Nodes (1): DeclarativeBase

### Community 80 - "K()"
Cohesion: 1.0
Nodes (1): K()

### Community 85 - "cf()"
Cohesion: 1.0
Nodes (1): cf()

### Community 88 - "_rate_limit_handler()"
Cohesion: 1.0
Nodes (1): _rate_limit_handler()

### Community 89 - "bh()"
Cohesion: 1.0
Nodes (1): bh()

### Community 92 - "bf()"
Cohesion: 1.0
Nodes (1): bf()

### Community 93 - "onWeisRequest()"
Cohesion: 1.0
Nodes (1): onWeisRequest()

### Community 94 - "onTrumpRequest()"
Cohesion: 1.0
Nodes (1): onTrumpRequest()

### Community 95 - "teamOf()"
Cohesion: 1.0
Nodes (1): teamOf()

### Community 96 - "computeLayout()"
Cohesion: 1.0
Nodes (1): computeLayout()

### Community 97 - "E()"
Cohesion: 1.0
Nodes (1): E()

### Community 104 - "H()"
Cohesion: 1.0
Nodes (1): H()

### Community 105 - "lobby_page()"
Cohesion: 1.0
Nodes (1): lobby_page()

### Community 106 - "_start_reaper()"
Cohesion: 1.0
Nodes (1): _start_reaper()

### Community 110 - "Protocol"
Cohesion: 1.0
Nodes (1): Protocol

### Community 114 - "home_page()"
Cohesion: 1.0
Nodes (1): home_page()

## Knowledge Gaps
- **13 isolated node(s):** `Uvicorn server start command`, `Dev test dependencies (pytest, pytest-asyncio, httpx)`, `HTML5 server runtime dependencies`, `Explicit imports replacing wildcards`, `db_utils module` (+8 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `GameSession state machine`** (24 nodes): `GameSession`, `._await_seat_action()`, `.broadcast()`, `.broadcast_per_seat()`, `._commit_pending_swap()`, `._disconnect_seat()`, `._game_start_for()`, `._partner_of()`, `._play_trick()`, `._reclaim_seat()`, `._reconnect_timeout()`, `._record_seat_swap_request()`, `._room_resume_message_for()`, `._run_spiel()`, `._seat()`, `._seat_swap_timeout()`, `._seat_to_dict()`, `.send_to_seat()`, `.start_game()`, `._transfer_host()`, `._trump_phase()`, `._weis_phase()`, `list`, `.display_name()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ai_strategies.py`** (9 nodes): `HardStrategy`, `._card_value()`, `.__init__()`, `._is_guaranteed_winner()`, `.on_card_played()`, `.on_spiel_start()`, `.pick_card()`, `._strength()`, `._winner_so_far()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Card Class Hierarchy (core)`** (8 nodes): `Card`, `.__eq__()`, `.__gt__()`, `.__init__()`, `.__repr__()`, `.__str__()`, `.to_json()`, `.to_jsons()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `database_manager.py`** (7 nodes): `db_example.py`, `.fetch_one()`, `.get_last_game_id()`, `.get_player_by_id()`, `.get_spieler_id_by_name()`, `demonstrate_context_manager()`, `db_example.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Cards_refactored.py`** (7 nodes): `.__init__()`, `.__init__()`, `Play`, `.__init__()`, `._setup_game()`, `.__init__()`, `.__init__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ai_strategies.py`** (6 nodes): `AIStrategy`, `.__init__()`, `.on_card_played()`, `.on_spiel_start()`, `.pick_card()`, `.pick_trump()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `tombstone.py`** (5 nodes): `tombstone.py`, `.create()`, `tombstone.py`, `hash_email()`, `hash_username()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `manager.py`** (4 nodes): `UserManager`, `.parse_id()`, `.validate_password()`, `manager.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Cards_refactored.py`** (3 nodes): `Suit`, `.__init__()`, `.__repr__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ratelimit.py`** (3 nodes): `ratelimit.py`, `ratelimit.py`, `make_limiter()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `._compute_ai_action()`** (3 nodes): `.pick_trump()`, `._compute_ai_action()`, `index()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Cards_refactored.py`** (3 nodes): `_add_card()`, `._move_cards()`, `_pop_card()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Cards_refactored.py`** (3 nodes): `create_card()`, `Deck`, `.__init__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `SmtpMailBackend`** (2 nodes): `SmtpMailBackend`, `.send()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `connect()`** (2 nodes): `connect()`, `wsUrl()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Sechs`** (2 nodes): `Sechs`, `.__init__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Ass`** (2 nodes): `Ass`, `.__init__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Koenig`** (2 nodes): `Koenig`, `.__init__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Banner`** (2 nodes): `Banner`, `.__init__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Acht`** (2 nodes): `Acht`, `.__init__()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `ConsoleMailBackend`** (2 nodes): `ConsoleMailBackend`, `.send()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `db_migration.py`** (2 nodes): `db_migration.py`, `db_migration tool`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `detect_stock()`** (2 nodes): `detect_stock()`, `._apply_stoeck()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `bZ()`** (2 nodes): `bZ()`, `D()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `bj()`** (2 nodes): `bj()`, `bk()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `bootAuth()`** (2 nodes): `bootAuth()`, `escapeHtml()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dev test dependencies (pytest, pytest-as`** (2 nodes): `Dev test dependencies (pytest, pytest-asyncio, httpx)`, `HTML5 server runtime dependencies`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `GET /auth/me endpoint`** (2 nodes): `GET /auth/me endpoint`, `Account identity panel`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `db_adapter compatibility layer`** (2 nodes): `db_adapter compatibility layer`, `imports_new.py compatibility shim`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `DeclarativeBase`** (1 nodes): `DeclarativeBase`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `K()`** (1 nodes): `K()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `cf()`** (1 nodes): `cf()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `_rate_limit_handler()`** (1 nodes): `_rate_limit_handler()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `bh()`** (1 nodes): `bh()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `bf()`** (1 nodes): `bf()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `onWeisRequest()`** (1 nodes): `onWeisRequest()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `onTrumpRequest()`** (1 nodes): `onTrumpRequest()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `teamOf()`** (1 nodes): `teamOf()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `computeLayout()`** (1 nodes): `computeLayout()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `E()`** (1 nodes): `E()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `H()`** (1 nodes): `H()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `lobby_page()`** (1 nodes): `lobby_page()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `_start_reaper()`** (1 nodes): `_start_reaper()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Protocol`** (1 nodes): `Protocol`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `home_page()`** (1 nodes): `home_page()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_build_auth_app()` connect `db.py` to `deps.py`, `server.py`, `ConsoleMailBackend`, `SmtpMailBackend`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **Why does `build_app()` connect `deps.py` to `Auth base.html Jinja layout`, `ratelimit.py`, `db.py`, `admin.html`, `users.py`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `DatabaseManager` connect `database_manager.py` to `database_manager.py`, `example.py`, `db_adapter.py`, `DatabaseManager OOP class`, `database_manager.py`, `database_manager.py`, `.__init__()`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `DatabaseManager` (e.g. with `migrate_database()` and `get_db_manager()`) actually correct?**
  _`DatabaseManager` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `principal_id()` (e.g. with `._seat_for_principal()` and `._spectator_for_principal()`) actually correct?**
  _`principal_id()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Uvicorn server start command`, `Dev test dependencies (pytest, pytest-asyncio, httpx)`, `HTML5 server runtime dependencies` to the rest of the system?**
  _13 weakly-connected nodes found - possible documentation gaps or missing edges._