'use strict';

// ─── Multiplayer game UI (Task 23) ────────────────────────────────────────────
//
// schieber.js drives game.html for the multi-WS protocol (`/ws/{code}`).
// Connection model: one WebSocket per browser, scoped to a room code read
// from the URL query (`?code=ABCDEF`). The first message we expect after
// connect is `room_resume` (the seat reclaim path used by /ws/{code}); a
// fresh `game_start` follows whenever the bg game-loop deals a new spiel.
//
// Per the schieber-protocol skill, every server→client message we handle is
// listed in the `handlers` map below. Out-of-list types are logged to the
// game log panel (defensive) and ignored. Client→server messages are emitted
// only via `send(...)` helpers — never inline.

// ─── URL / connection ─────────────────────────────────────────────────────────

const params = new URLSearchParams(window.location.search);
const ROOM_CODE = params.get('code');

const SUIT_EMOJI = {
  Eicheln: '🌳', Rosen: '🌹', Schellen: '🔔', Schilten: '🛡',
  Oben: '⬆', Unten: '⬇',
};

const POSITION_LABELS = {
  comps: 'Süd', compn: 'Nord', compo: 'Ost', compe: 'West',
};

// Standard CW order from any seat's POV: me → folger → partner → prev.
// Mirror of `Cards_refactored.py`'s `folger`:
//   comps → compo → compn → compe → comps
const FOLGER = {
  comps: 'compo', compo: 'compn', compn: 'compe', compe: 'comps',
};

function teamOf(position) {
  return (position === 'comps' || position === 'compn') ? 'sn' : 'ow';
}

// Compute the visual layout slot ('bottom' | 'right' | 'top' | 'left') for
// every position relative to the local seat. With `bottom` always being
// the local seat, `right` = folger[bottom], `top` = folger[right] (=
// partner), `left` = folger[top]. Spectators view from `comps` for now.
function computeLayout(myPos) {
  return { bottom: 'comps', right: 'compo', top: 'compn', left: 'compe' };
}

// ─── Game state ───────────────────────────────────────────────────────────────

const state = {
  myPosition: null,            // null = spectator
  layout: computeLayout('comps'),
  hand: [],                    // local seat's hand (codes)
  scores: { sn: 0, ow: 0 },
  targetScore: 1000,
  // Per-seat metadata keyed by position.
  seats: {
    comps: {
      display_name: 'Süd', is_partner: false, card_count: 0,
      paused: false, ai: false
    },
    compn: {
      display_name: 'Nord', is_partner: false, card_count: 0,
      paused: false, ai: false
    },
    compo: {
      display_name: 'Ost', is_partner: false, card_count: 0,
      paused: false, ai: false
    },
    compe: {
      display_name: 'West', is_partner: false, card_count: 0,
      paused: false, ai: false
    },
  },
  trick: { comps: null, compn: null, compo: null, compe: null },
  validCards: [],
  operator: null,
};

// ─── WebSocket ────────────────────────────────────────────────────────────────

let ws = null;

// Reconnect / shutdown bookkeeping.
//   intentionalClose — user navigated away or a fatal close was handled;
//                       suppresses auto-reconnect.
//   reconnectAttempt — exponential-backoff counter; reset on a clean onopen.
//   fatalReason      — set from an in-band {type:"error", reason:...} message
//                      (the FATAL set the server sends right before close 1008).
const FATAL_REASONS = new Set(['room_not_found', 'no_seat_slot', 'no_auth']);
const RECONNECT_MAX_ATTEMPTS = 6;
let intentionalClose = false;
let reconnectAttempt = 0;
let fatalReason = null;
let reconnectTimer = null;

function wsUrl() {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
  return `${proto}://${window.location.host}/ws/${ROOM_CODE}`;
}

// WHY fatal-vs-transient: Apache's mod_proxy_wstunnel does not reliably forward
// the WS close *reason* string to the browser, so we cannot trust
// CloseEvent.reason. The server therefore sends an in-band
// {type:"error", reason:<R>} just before close(1008). We treat a connection as
// fatal (redirect, no reconnect) when that reason is in FATAL_REASONS or the
// close code is 1008; everything else (1006/1001/1011/server restart) is
// transient and auto-reconnects with backoff.
function handleFatalError(reason, message) {
  fatalReason = reason;
  intentionalClose = true;
  appendLog(message || 'Verbindung abgelehnt.', 'error');
  if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null; }
}

function fatalRedirect(reason) {
  if (reason === 'no_seat_slot') {
    window.location.href = '/lobby?code=' + encodeURIComponent(ROOM_CODE || '');
  } else {
    // room_not_found / no_auth / anything else fatal → home.
    window.location.href = '/home';
  }
}

function scheduleReconnect() {
  if (reconnectAttempt >= RECONNECT_MAX_ATTEMPTS) {
    appendLog('Verbindung verloren — bitte Seite neu laden.', 'error');
    return;
  }
  const delay = Math.min(1000 * Math.pow(2, reconnectAttempt), 10000);
  reconnectAttempt += 1;
  appendLog(
    `Verbindung getrennt — neuer Versuch in ${Math.round(delay / 1000)}s ` +
    `(${reconnectAttempt}/${RECONNECT_MAX_ATTEMPTS})…`,
    'error'
  );
  reconnectTimer = setTimeout(() => { reconnectTimer = null; connect(); }, delay);
}

function connect() {
  if (!ROOM_CODE) {
    appendLog('Kein Raumcode in URL — Weiterleitung zur Startseite…', 'error');
    window.location.href = '/home';
    return;
  }
  ws = new WebSocket(wsUrl());
  ws.onopen = () => {
    reconnectAttempt = 0;
    appendLog(`Verbunden mit Raum ${ROOM_CODE}.`);
  };
  ws.onmessage = (e) => {
    let msg = null;
    try { msg = JSON.parse(e.data); } catch (_) {
      appendLog('Ungültige Server-Nachricht.', 'error');
      return;
    }
    dispatch(msg);
  };
  ws.onclose = (event) => {
    if (intentionalClose || fatalReason || (event && event.code === 1008)) {
      // Fatal close (or user-initiated): show message + redirect, never reconnect.
      const reason = fatalReason || 'room_not_found';
      if (!intentionalClose || fatalReason) {
        // A 1008 without an in-band reason still redirects (default: home).
        fatalRedirect(reason);
      }
      return;
    }
    // Transient/abnormal drop → auto-reconnect with backoff.
    scheduleReconnect();
  };
  ws.onerror = () => appendLog('Verbindungsfehler.', 'error');
}

// Navigating away should not trigger reconnect noise.
window.addEventListener('beforeunload', () => { intentionalClose = true; });

function send(msg) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
  }
}

// Client → server senders (one helper per message type).
function sendChooseTrump(operator) {
  send({ type: 'choose_trump', operator });
}
function sendSchieben() {
  send({ type: 'schieben' });
}
function sendAnnounceWeis(announce, weisNames) {
  const payload = { type: 'announce_weis', announce };
  if (announce && weisNames) payload.weis = weisNames;
  send(payload);
}
function sendPlayCard(code) {
  send({ type: 'play_card', card: code });
}
function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const text = (input.value || '').trim();
  if (!text) return;
  send({ type: 'chat', text });
  input.value = '';
}

// ─── Dispatch ─────────────────────────────────────────────────────────────────

const handlers = {
  game_start: onGameStart,
  room_resume: onRoomResume,
  trump_request: onTrumpRequest,
  trump_pending: onTrumpPending,
  trump_chosen: onTrumpChosen,
  weis_request: onWeisRequest,
  weis_resolution: onWeisResolution,
  play_request: onPlayRequest,
  play_pending: onPlayPending,
  card_played: onCardPlayed,
  trick_end: onTrickEnd,
  spiel_end: onSpielEnd,
  game_end: onGameEnd,
  seat_paused: onSeatPaused,
  seat_reclaimed: onSeatReclaimed,
  seat_ai_takeover: onSeatAiTakeover,
  seat_changed: onSeatChanged,
  seat_kicked: onSeatKicked,
  host_changed: onHostChanged,
  seat_swap_request: onSeatSwapRequest,
  seat_swap_committed: onSeatSwapCommitted,
  seat_swap_expired: onSeatSwapExpired,
  error: onError,
  chat_message: onChatMessage,
};

function dispatch(msg) {
  if (!msg || typeof msg !== 'object' || typeof msg.type !== 'string') {
    appendLog('Server-Nachricht ohne type — ignoriert.', 'error');
    return;
  }
  const fn = handlers[msg.type];
  if (fn) {
    try { fn(msg); }
    catch (err) { appendLog(`Render-Fehler: ${err.message}`, 'error'); }
  } else {
    // Unknown message: surface defensively but don't crash.
    appendLog(`Unbekannte Nachricht: ${msg.type}`, 'error');
  }
}

// ─── Auth strip ───────────────────────────────────────────────────────────────

async function bootAuth() {
  try {
    const r = await fetch('/auth/whoami', { credentials: 'same-origin' });
    const me = await r.json();
    const el = document.getElementById('auth-info');
    if (!el) return;
    const codeBadge = ROOM_CODE
      ? ` · Raum <a href="/lobby?code=${escapeHtml(ROOM_CODE)}" style="color:#9cf">${escapeHtml(ROOM_CODE)}</a>`
      : '';
    if (me.kind === 'user') {
      const verified = me.is_verified ? '✓' : '⚠';
      el.innerHTML = `${escapeHtml(me.display_name)} (${verified}) ` +
        `<a href="/account" style="color:#9cf">Account</a> · ` +
        `<a href="#" id="logoutBtn" style="color:#9cf">Logout</a>` +
        codeBadge;
      const btn = document.getElementById('logoutBtn');
      if (btn) {
        btn.addEventListener('click', async (e) => {
          e.preventDefault();
          await fetch('/auth/logout', {
            method: 'POST',
            headers: { 'X-Requested-With': 'schieber' },
          });
          location.reload();
        });
      }
    } else {
      el.innerHTML = `Playing as ${escapeHtml(me.display_name)} ` +
        `<a href="/login" style="color:#9cf">Sign in</a> · ` +
        `<a href="/signup" style="color:#9cf">Sign up</a>` +
        codeBadge;
    }
  } catch (err) {
    console.warn('auth boot failed', err);
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

bootAuth().then(connect);

// ─── Render ───────────────────────────────────────────────────────────────────

function renderScores() {
  document.getElementById('score-sn').textContent = state.scores.sn;
  document.getElementById('score-ow').textContent = state.scores.ow;
  document.getElementById('score-target').textContent = `Ziel: ${state.targetScore}`;
}

// Update the AI bar slots (the 3 non-local seats). The DOM still has
// fixed slot ids (player-compe / player-compn / player-compo) by historical
// happenstance; we now drive their content from `state.seats[layout.X]`.
function renderAIBar() {
  const allPositions = ['compe', 'compn', 'compo', 'comps'];
  for (const pos of allPositions) {
    const seat = state.seats[pos];
    const wrap = document.getElementById(`player-${pos}`);
    if (!wrap) continue;

    if (pos === state.myPosition) {
      wrap.style.display = 'none';
      continue;
    }
    wrap.style.display = '';
    wrap.classList.toggle('partner', !!seat.is_partner);
    wrap.classList.toggle('paused', !!seat.paused);
    wrap.classList.toggle('ai', !!seat.ai);

    // Avatar letter — first letter of position label (W/N/O for the German label).
    const avatar = wrap.querySelector('.ai-avatar');
    if (avatar) avatar.textContent = POSITION_LABELS[pos][0];

    const nameEl = wrap.querySelector('.ai-name');
    if (nameEl) {
      const partnerStar = seat.is_partner ? ' ★' : '';
      const pausedTag = seat.paused ? ' (pausiert)' : '';
      const aiTag = seat.ai ? ' (KI)' : '';
      nameEl.textContent = `${seat.display_name}${partnerStar}${pausedTag}${aiTag}`;
      nameEl.title = `${POSITION_LABELS[pos]} · ${pos}`;
    }

    const cardsEl = wrap.querySelector('.ai-cards');
    if (cardsEl) {
      cardsEl.innerHTML = '';
      const count = seat.card_count ?? 0;
      for (let i = 0; i < count; i++) {
        const d = document.createElement('div');
        d.className = 'ai-card-back';
        cardsEl.appendChild(d);
      }
    }
  }
  renderScores();
}

function renderHand() {
  const container = document.getElementById('hand-cards');
  container.innerHTML = '';
  state.hand.forEach((code) => {
    const card = document.createElement('div');
    card.className = 'card';
    const face = document.createElement('div');
    face.className = `face back card${code}`;
    card.appendChild(face);

    if (state.validCards.length > 0) {
      if (state.validCards.includes(code)) {
        card.classList.add('valid');
        card.addEventListener('click', () => playCard(code));
      } else {
        card.classList.add('invalid');
      }
    }
    container.appendChild(card);
  });
  // Update hand label to show seat label.
  const lbl = document.getElementById('hand-label');
  if (lbl) {
    if (state.myPosition) {
      lbl.textContent = `Deine Hand (${POSITION_LABELS[state.myPosition]})`;
    } else {
      lbl.textContent = 'Zuschauer-Modus (keine Karten)';
    }
  }
}

// Render the trick area. The DOM has 4 fixed slot ids
// (trick-comps / trick-compn / trick-compo / trick-compe). We re-label them
// to match the local seat's POV and inject the played card if any.
function renderTrickArea() {
  // Map historic slot id ↔ layout role.
  const slotMap = [
    { domId: 'trick-comps', layoutKey: 'bottom' },
    { domId: 'trick-compn', layoutKey: 'top' },
    { domId: 'trick-compo', layoutKey: 'right' },
    { domId: 'trick-compe', layoutKey: 'left' },
  ];
  for (const slot of slotMap) {
    const pos = state.layout[slot.layoutKey];
    const slotEl = document.getElementById(slot.domId);
    if (!slotEl) continue;
    // Update label.
    const labelEl = slotEl.querySelector('.trick-label');
    if (labelEl) {
      const isMe = (pos === state.myPosition);
      labelEl.textContent = isMe ? 'Du' : POSITION_LABELS[pos];
      labelEl.title = pos;
    }
    // Replace card.
    const existing = slotEl.querySelector('.card');
    if (existing) existing.remove();
    const code = state.trick[pos];
    if (code) {
      const card = document.createElement('div');
      card.className = 'card';
      const face = document.createElement('div');
      face.className = `face back card${code}`;
      card.appendChild(face);
      slotEl.appendChild(card);
    }
  }
}

function appendLog(text, cls = '') {
  const entries = document.getElementById('log-entries');
  if (!entries) return;
  const div = document.createElement('div');
  div.className = `log-entry${cls ? ' ' + cls : ''}`;
  div.textContent = text;
  entries.appendChild(div);
  entries.scrollTop = entries.scrollHeight;
  while (entries.children.length > 80) entries.removeChild(entries.firstChild);
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function applyGameStartLikePayload(msg) {
  // Common bootstrap path for both `game_start` and `room_resume`.
  // Updates: myPosition, layout, hand, scores, target, seat metadata,
  // operator (room_resume only), trick (cleared), validCards (cleared).
  state.myPosition = msg.your_position || null;
  state.layout = computeLayout(state.myPosition || 'comps');
  state.hand = Array.isArray(msg.your_hand) ? msg.your_hand.slice() : [];
  state.scores = msg.scores || { sn: 0, ow: 0 };
  if (typeof msg.target === 'number') state.targetScore = msg.target;
  state.trick = { comps: null, compn: null, compo: null, compe: null };
  state.validCards = [];

  // Seed seat metadata. Reset all seats first to clean values.
  for (const pos of Object.keys(state.seats)) {
    state.seats[pos].is_partner = false;
    state.seats[pos].card_count = 0;
    state.seats[pos].paused = false;
    state.seats[pos].ai = false;
    // Default display_name = label (overwritten below for known seats).
    state.seats[pos].display_name = POSITION_LABELS[pos];
  }

  if (state.myPosition && state.seats[state.myPosition]) {
    state.seats[state.myPosition].card_count = state.hand.length || 9;
    state.seats[state.myPosition].display_name = POSITION_LABELS[state.myPosition];
  }

  if (Array.isArray(msg.players)) {
    for (const p of msg.players) {
      if (!p || !state.seats[p.position]) continue;
      state.seats[p.position].display_name = p.display_name || POSITION_LABELS[p.position];
      state.seats[p.position].is_partner = !!p.is_partner;
      if (typeof p.card_count === 'number') {
        state.seats[p.position].card_count = p.card_count;
      } else {
        state.seats[p.position].card_count = 9;
      }
    }
  }

  // Operator / trump only known after a Spiel has started (room_resume).
  state.operator = msg.operator || null;
  const badge = document.getElementById('trump-badge');
  if (state.operator) {
    badge.classList.remove('hidden');
    document.getElementById('trump-value').textContent =
      `${SUIT_EMOJI[state.operator] ?? ''} ${state.operator}`;
  } else {
    badge.classList.add('hidden');
  }
}

// ─── Message handlers ─────────────────────────────────────────────────────────

function onGameStart(msg) {
  applyGameStartLikePayload(msg);
  document.getElementById('active-player').textContent =
    msg.first_player ? `Führt: ${POSITION_LABELS[msg.first_player] || msg.first_player}` : '';
  appendLog('--- Neues Spiel ---');
  if (msg.first_player) appendLog(`${POSITION_LABELS[msg.first_player] || msg.first_player} führt.`);
  renderAIBar();
  renderHand();
  renderTrickArea();
}

function onRoomResume(msg) {
  // Reconnect / first-load path. Replays missed_tricks if any, then
  // shows the current in-flight trick.
  applyGameStartLikePayload(msg);
  document.getElementById('active-player').textContent =
    msg.current_seat_turn
      ? `Am Zug: ${POSITION_LABELS[msg.current_seat_turn] || msg.current_seat_turn}`
      : '';
  appendLog(`--- Wiederhergestellt (Phase: ${msg.phase || '?'}) ---`);

  // Show recent trick history briefly.
  if (Array.isArray(msg.missed_tricks)) {
    for (const t of msg.missed_tricks) {
      const winner = t.winner_position
        ? (POSITION_LABELS[t.winner_position] || t.winner_position)
        : '?';
      const points = (typeof t.points === 'number') ? ` (${t.points} Pkt)` : '';
      appendLog(`Vergangener Stich: ${winner}${points}.`);
    }
  }

  // In-flight trick: paint cards already on the table.
  if (Array.isArray(msg.trick_so_far)) {
    for (const entry of msg.trick_so_far) {
      if (entry && entry.position && entry.card) {
        state.trick[entry.position] = entry.card;
        // Decrement card count for visible plays from non-local seats.
        if (entry.position !== state.myPosition && state.seats[entry.position]) {
          state.seats[entry.position].card_count = Math.max(
            0, (state.seats[entry.position].card_count ?? 9) - 1
          );
        }
      }
    }
  }

  renderAIBar();
  renderHand();
  renderTrickArea();
}

function onTrumpRequest(msg) {
  const modal = document.getElementById('trump-modal');
  const grid = document.getElementById('trump-options');
  const schiebenBtn = document.getElementById('schieben-btn');
  grid.innerHTML = '';

  ['Eicheln', 'Rosen', 'Schellen', 'Schilten', 'Oben', 'Unten'].forEach((mode) => {
    const btn = document.createElement('button');
    btn.className = 'suit-btn';
    btn.textContent = `${SUIT_EMOJI[mode] ?? ''} ${mode}`;
    btn.onclick = () => {
      sendChooseTrump(mode);
      modal.classList.add('hidden');
    };
    grid.appendChild(btn);
  });

  const allowed = !!msg.schieben_allowed;
  schiebenBtn.classList.toggle('hidden', !allowed);
  schiebenBtn.onclick = () => {
    sendSchieben();
    modal.classList.add('hidden');
  };

  // Position the box either at the player's last dragged spot (remembered
  // across rounds) or at the default top-right aside, so the hand is never
  // covered.
  positionTrumpModalOnShow();
  modal.classList.remove('hidden');
}

// ─── Trump modal drag (Pointer Events) ──────────────────────────────────────
//
// The trump modal's overlay does not dim the table (see game.css). The
// .modal-box is `position: fixed` and JS sets its left/top on every show.
// Default position is top-right aside so cards are never covered. The whole
// box is a drag surface (except the suit buttons, which stay clickable).
// After a drag, the position is remembered for subsequent reopens this
// session (next round / Schieben pass-back).

const TRUMP_BOX_EST_WIDTH = 340;   // matches .modal-box max-width in game.css
const TRUMP_BOX_EST_HEIGHT = 220;  // rough; only used to clamp default pos
let trumpBoxLastPos = null;        // {left, top} once dragged; null = default

function trumpBoxRect(box) {
  // While hidden the box has zero size — fall back to CSS estimates so the
  // pre-show clamp produces a sensible default.
  return {
    w: box.offsetWidth || TRUMP_BOX_EST_WIDTH,
    h: box.offsetHeight || TRUMP_BOX_EST_HEIGHT,
  };
}

function clampTrumpBoxPos(left, top, box) {
  const { w, h } = trumpBoxRect(box);
  const maxLeft = Math.max(0, window.innerWidth - w);
  const maxTop = Math.max(0, window.innerHeight - h);
  return {
    left: Math.max(0, Math.min(left, maxLeft)),
    top: Math.max(0, Math.min(top, maxTop)),
  };
}

function defaultTrumpBoxPosition(box) {
  // Top-right of viewport, well above the hand area.
  return clampTrumpBoxPos(
    window.innerWidth - TRUMP_BOX_EST_WIDTH - 20,
    60,
    box,
  );
}

function positionTrumpModalOnShow() {
  const box = document.querySelector('#trump-modal .modal-box');
  if (!box) return;
  const pos = trumpBoxLastPos
    ? clampTrumpBoxPos(trumpBoxLastPos.left, trumpBoxLastPos.top, box)
    : defaultTrumpBoxPosition(box);
  box.style.left = `${pos.left}px`;
  box.style.top = `${pos.top}px`;
  box.classList.remove('dragging');
}

function initTrumpDrag() {
  const box = document.querySelector('#trump-modal .modal-box');
  if (!box) return;

  let dragging = false;
  let pointerId = null;
  let offsetX = 0;
  let offsetY = 0;

  box.addEventListener('pointerdown', (e) => {
    if (e.button !== undefined && e.button !== 0) return;
    // Clicks on buttons inside the box are NOT drags — let them through.
    if (e.target.closest('button')) return;
    const rect = box.getBoundingClientRect();
    offsetX = e.clientX - rect.left;
    offsetY = e.clientY - rect.top;
    dragging = true;
    pointerId = e.pointerId;
    box.classList.add('dragging');
    try { box.setPointerCapture(pointerId); } catch (_) { /* ignore */ }
    e.preventDefault();
  });

  box.addEventListener('pointermove', (e) => {
    if (!dragging || e.pointerId !== pointerId) return;
    const pos = clampTrumpBoxPos(e.clientX - offsetX, e.clientY - offsetY, box);
    box.style.left = `${pos.left}px`;
    box.style.top = `${pos.top}px`;
    e.preventDefault();
  });

  function endDrag(e) {
    if (!dragging || (pointerId !== null && e.pointerId !== pointerId)) return;
    dragging = false;
    box.classList.remove('dragging');
    try { box.releasePointerCapture(pointerId); } catch (_) { /* ignore */ }
    pointerId = null;
    // Remember the dragged position so the next trump_request reopens here.
    trumpBoxLastPos = {
      left: parseFloat(box.style.left) || 0,
      top: parseFloat(box.style.top) || 0,
    };
  }

  box.addEventListener('pointerup', endDrag);
  box.addEventListener('pointercancel', endDrag);
}

initTrumpDrag();

function onTrumpPending(msg) {
  const who = msg.by_position
    ? (POSITION_LABELS[msg.by_position] || msg.by_position)
    : '?';
  document.getElementById('active-player').textContent = `Trumpfwahl: ${who}`;
  appendLog(`Trumpfwahl bei ${who}…`);
}

function onTrumpChosen(msg) {
  state.operator = msg.operator;
  const badge = document.getElementById('trump-badge');
  badge.classList.remove('hidden');
  document.getElementById('trump-value').textContent =
    `${SUIT_EMOJI[msg.operator] ?? ''} ${msg.operator}`;
  const who = msg.by_position
    ? (POSITION_LABELS[msg.by_position] || msg.by_position)
    : '?';
  appendLog(`Trumpf: ${msg.operator} (${who})`);
  document.getElementById('active-player').textContent = '';
}

function onWeisRequest(msg) {
  const modal = document.getElementById('weis-modal');
  const list = document.getElementById('weis-list');
  list.innerHTML = '';
  const yourWeis = Array.isArray(msg.your_weis) ? msg.your_weis : [];
  let totalPts = 0;

  yourWeis.forEach((w) => {
    totalPts += (w.points || 0);
    const div = document.createElement('div');
    div.className = 'weis-item';
    div.innerHTML =
      `<span class="weis-name">${escapeHtml(w.name || '')}</span>` +
      `<span class="weis-suit">${escapeHtml(w.suit || '')}</span>` +
      `<span class="weis-pts">${w.points || 0} Pkt</span>`;
    list.appendChild(div);
  });

  const announceBtn = document.getElementById('weis-announce-btn');
  if (yourWeis.length === 0) {
    // No eligible weis — only "Schweigen" is available.
    announceBtn.classList.add('hidden');
  } else {
    announceBtn.classList.remove('hidden');
    announceBtn.textContent = `✓ Ansagen (${totalPts} Pkt)`;
    announceBtn.onclick = () => {
      sendAnnounceWeis(true, yourWeis.map((w) => w.name));
      modal.classList.add('hidden');
    };
  }
  document.getElementById('weis-pass-btn').onclick = () => {
    sendAnnounceWeis(false);
    modal.classList.add('hidden');
  };

  modal.classList.remove('hidden');
}

function onWeisResolution(msg) {
  // No score field on this message — the running totals come via
  // spiel_end. We log the outcome and any per-position weis.
  const team = msg.winning_team;
  if (team === 'sn') appendLog('Weis: Team Süd-Nord gewinnt.');
  else if (team === 'ow') appendLog('Weis: Team Ost-West gewinnt.');
  else if (team === 'tie') appendLog('Weis: Unentschieden.');

  const wbp = msg.weis_by_position || {};
  const positions = Object.keys(wbp);
  if (positions.length === 0) {
    appendLog('Kein Weis angesagt.');
  } else {
    for (const pos of positions) {
      const arr = wbp[pos] || [];
      const names = arr.map((w) => `${w.name}${w.suit ? `:${w.suit}` : ''}`).join(', ');
      const pts = arr.reduce((acc, w) => acc + (w.points || 0), 0);
      appendLog(`${POSITION_LABELS[pos] || pos}: ${names} (${pts} Pkt)`);
    }
  }
}

function onPlayRequest(msg) {
  // Local seat's turn. Paint trick_so_far in case the prompt arrived
  // ahead of card_played (server orders card_played after, but a
  // reconnect path may bypass the broadcast).
  if (Array.isArray(msg.trick_so_far)) {
    // Reset and apply (the cumulative shape lets us simply replay).
    state.trick = { comps: null, compn: null, compo: null, compe: null };
    for (const entry of msg.trick_so_far) {
      if (entry && entry.position && entry.card) {
        state.trick[entry.position] = entry.card;
      }
    }
  }
  state.validCards = Array.isArray(msg.valid_cards) ? msg.valid_cards : [];
  renderTrickArea();
  renderHand();
  document.getElementById('active-player').textContent = 'Am Zug: Du';
  appendLog('Dein Zug.');
}

function onPlayPending(msg) {
  if (Array.isArray(msg.trick_so_far)) {
    state.trick = { comps: null, compn: null, compo: null, compe: null };
    for (const entry of msg.trick_so_far) {
      if (entry && entry.position && entry.card) {
        state.trick[entry.position] = entry.card;
      }
    }
  }
  const who = msg.by_position
    ? (POSITION_LABELS[msg.by_position] || msg.by_position)
    : '?';
  document.getElementById('active-player').textContent = `Am Zug: ${who}`;
  renderTrickArea();
}

function onCardPlayed(msg) {
  const pos = msg.by_position;
  if (!pos || !state.seats[pos]) return;
  state.trick[pos] = msg.card;

  if (pos === state.myPosition) {
    state.hand = state.hand.filter((c) => c !== msg.card);
    state.validCards = [];
    state.seats[pos].card_count = state.hand.length;
  } else if (state.seats[pos]) {
    state.seats[pos].card_count = Math.max(
      0, (state.seats[pos].card_count ?? 9) - 1
    );
  }

  renderTrickArea();
  renderAIBar();
  renderHand();
  appendLog(`${POSITION_LABELS[pos] || pos} spielt ${msg.card}.`);
  document.getElementById('active-player').textContent = '';
}

function onTrickEnd(msg) {
  const pos = msg.winner_position;
  const team = msg.winner_team;
  const points = (typeof msg.points === 'number') ? msg.points : null;

  // Update running totals — server doesn't send them on trick_end (totals
  // come on spiel_end), but we can accumulate locally.
  if (team === 'sn' && points !== null) state.scores.sn += points;
  if (team === 'ow' && points !== null) state.scores.ow += points;
  renderScores();

  const who = pos ? (POSITION_LABELS[pos] || pos) : '?';
  if (points !== null) appendLog(`Stich an ${who} (${points} Pkt).`);
  else appendLog(`Stich an ${who}.`);

  // Clear the trick area after a beat for animation.
  setTimeout(() => {
    state.trick = { comps: null, compn: null, compo: null, compe: null };
    renderTrickArea();
  }, 1200);
}

function onSpielEnd(msg) {
  // Authoritative running totals after weis + match bonus.
  if (msg.scores) {
    state.scores = { sn: msg.scores.sn ?? 0, ow: msg.scores.ow ?? 0 };
    renderScores();
  }
  appendLog(`=== Spielende: SN ${state.scores.sn} / OW ${state.scores.ow} ===`);
  if (msg.weis_added) {
    const w = msg.weis_added;
    const sn = w.sn || 0, ow = w.ow || 0;
    if (sn || ow) appendLog(`Weis: SN +${sn}, OW +${ow}`);
  }
  if (msg.match) appendLog('🎯 Match! +100');
  if (msg.stoeck_team) {
    let lbl;
    if (msg.stoeck_team === 'sn') lbl = 'Süd-Nord';
    else if (msg.stoeck_team === 'ow') lbl = 'Ost-West';
    else if (msg.stoeck_team === 'both') lbl = 'beide Teams';
    else lbl = msg.stoeck_team;
    appendLog(`Stöck: Team ${lbl}`);
  }
}

function onGameEnd(msg) {
  if (msg.scores) {
    state.scores = { sn: msg.scores.sn ?? 0, ow: msg.scores.ow ?? 0 };
    renderScores();
  }
  const t = msg.winner_team;
  const lbl = t === 'sn' ? 'Team Süd-Nord'
    : t === 'ow' ? 'Team Ost-West'
      : t === 'tie' ? 'Unentschieden' : (t || '?');
  appendLog(`🏆 Spiel vorbei! ${lbl}.`);
  appendLog(`Endstand: SN ${state.scores.sn} / OW ${state.scores.ow}.`);

  const modal = document.getElementById('game-over-modal');
  const msgEl = document.getElementById('game-over-message');
  if (modal && msgEl) {
    msgEl.innerHTML = `<strong>${lbl} gewinnt!</strong><br><br>Endstand: SN ${state.scores.sn} / OW ${state.scores.ow}.`;
    modal.classList.remove('hidden');
  }
}

function onSeatPaused(msg) {
  const pos = msg.position;
  if (!pos || !state.seats[pos]) return;
  state.seats[pos].paused = true;
  if (msg.display_name) state.seats[pos].display_name = msg.display_name;
  renderAIBar();
  const deadline = msg.reconnect_deadline_secs;
  const name = msg.display_name || POSITION_LABELS[pos] || pos;
  appendLog(
    `${name} pausiert${deadline ? ` (max. ${deadline}s)` : ''}…`,
    'error'
  );
}

function onSeatReclaimed(msg) {
  const pos = msg.position;
  if (!pos || !state.seats[pos]) return;
  state.seats[pos].paused = false;
  state.seats[pos].ai = false;
  if (msg.display_name) state.seats[pos].display_name = msg.display_name;
  renderAIBar();
  const name = msg.display_name || POSITION_LABELS[pos] || pos;
  appendLog(`${name} wieder verbunden.`);
}

function onSeatAiTakeover(msg) {
  const pos = msg.position;
  if (!pos || !state.seats[pos]) return;
  state.seats[pos].paused = false;
  state.seats[pos].ai = true;
  state.seats[pos].display_name = `KI (${POSITION_LABELS[pos] || pos})`;
  renderAIBar();
  appendLog(`${POSITION_LABELS[pos] || pos}: KI übernimmt.`);
}

function onSeatChanged(msg) {
  // {seat: {...}, reason: "join"|"leave"|"disconnect"|"kick"|"ai_takeover"}
  const seat = msg.seat;
  if (!seat || !state.seats[seat.position]) return;
  const pos = seat.position;
  state.seats[pos].display_name = seat.display_name || POSITION_LABELS[pos];
  state.seats[pos].ai = !!seat.is_ai;
  state.seats[pos].paused = !seat.is_ai && seat.connected === false;
  renderAIBar();
  if (msg.reason) {
    appendLog(`Sitz ${POSITION_LABELS[pos] || pos}: ${msg.reason}.`);
  }
}

function onSeatKicked(msg) {
  const pos = msg.position;
  if (!pos) return;
  appendLog(`${POSITION_LABELS[pos] || pos} wurde entfernt.`, 'error');
}

function onHostChanged(msg) {
  const newHost = msg.new_host_position;
  const newName = msg.new_host_display_name || (POSITION_LABELS[newHost] || newHost);
  appendLog(`Neuer Host: ${newName}.`);
}

function onSeatSwapRequest(msg) {
  const from = msg.from_display_name || POSITION_LABELS[msg.from_position] || msg.from_position;
  appendLog(`Platztausch-Anfrage von ${from}.`);
  // Auto-accept UI is out of scope for Task 23; surface in log only.
}

function onSeatSwapCommitted(msg) {
  appendLog('Sitze getauscht. Spiel wird mit neuer Aufstellung fortgesetzt.');
  // The next room_resume / game_start will refresh layout & hand.
}

function onSeatSwapExpired(msg) {
  appendLog('Platztausch-Anfrage abgelaufen.');
}

function onError(msg) {
  // FATAL errors carry a `reason` (room_not_found / no_seat_slot / no_auth) and
  // arrive just before the server closes with 1008. Ordinary in-game validation
  // errors have NO `reason` field — those just shake the hand.
  if (msg && FATAL_REASONS.has(msg.reason)) {
    handleFatalError(msg.reason, msg.message);
    return;
  }
  appendLog(`Fehler: ${msg.message || '(unbekannt)'}`, 'error');
  // Visual shake of hand cards if we mis-played.
  const handEl = document.getElementById('hand-cards');
  if (handEl) {
    handEl.classList.remove('shake');
    void handEl.offsetWidth;  // reflow → restart animation
    handEl.classList.add('shake');
  }
}

// ─── Chat ─────────────────────────────────────────────────────────────────────

function onChatMessage(msg) {
  const box = document.getElementById('chat-messages');
  if (!box) return;
  const div = document.createElement('div');
  div.className = 'chat-entry';
  div.innerHTML = `<span class="chat-sender">${escapeHtml(msg.from_name)}:</span> ${escapeHtml(msg.text)}`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

const $chatSend = document.getElementById('chat-send');
const $chatInput = document.getElementById('chat-input');
if ($chatSend) $chatSend.addEventListener('click', sendChatMessage);
if ($chatInput) $chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); sendChatMessage(); }
});

// ─── Card play action ─────────────────────────────────────────────────────────

function playCard(code) {
  if (!state.validCards.includes(code)) return;
  state.validCards = [];
  renderHand();
  sendPlayCard(code);
}

// ─── Game Over Actions ────────────────────────────────────────────────────────
const btnNewGame = document.getElementById('btn-new-game');
if (btnNewGame) {
  btnNewGame.addEventListener('click', async () => {
    try {
      const res = await fetch('/rooms', {
        method: 'POST',
        body: JSON.stringify({}),
        headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'schieber' },
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to create room');
      const room = await res.json();
      window.location.href = `/lobby?code=${room.code}`;
    } catch (e) {
      appendLog("Fehler beim Erstellen eines neuen Spiels: " + e.message, 'error');
    }
  });
}

const btnHome = document.getElementById('btn-home');
if (btnHome) {
  btnHome.addEventListener('click', () => {
    window.location.href = '/home';
  });
}

const btnQuit = document.getElementById('btn-quit');
if (btnQuit) {
  btnQuit.addEventListener('click', async () => {
    try {
      if (ROOM_CODE) {
        await fetch(`/rooms/${ROOM_CODE}/leave`, {
          method: 'POST',
          body: JSON.stringify({}),
          headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'schieber' },
          credentials: 'include'
        });
      }
    } catch (e) {
      console.warn('Failed to leave room', e);
    }
    window.location.href = '/home';
  });
}
