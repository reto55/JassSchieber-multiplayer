// Schieber lobby page — Task 22.
// Renders room state, offers Join/Leave/Spectate/Start, opens WS once seated.

const params = new URLSearchParams(window.location.search);
const code = params.get('code');

const $code = document.getElementById('room-code');
const $seats = document.getElementById('seats');
const $variantList = document.getElementById('variant-list');
const $error = document.getElementById('error');
const $who = document.getElementById('who');
const $btnJoin = document.getElementById('btn-join');
const $btnLeave = document.getElementById('btn-leave');
const $btnSpectate = document.getElementById('btn-spectate');
const $btnStopSpectate = document.getElementById('btn-stop-spectate');
const $btnStart = document.getElementById('btn-start');
const $spectatorCount = document.getElementById('spectator-count');
const $stateValue = document.getElementById('state-value');
const $currentTargetScore = document.getElementById('current-target-score');
const $targetScoreControls = document.getElementById('target-score-controls');
const btnTargets = document.querySelectorAll('.btn-target');

let currentRoomState = null;
let myMembership = null; // {role: 'seat'|'spectator', position?: 'comps'|...}

async function api(path, opts = {}) {
  const headers = { 'X-Requested-With': 'schieber', ...(opts.headers || {}) };
  let body = opts.body;
  if (body && typeof body !== 'string') {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(body);
  }
  const res = await fetch(path, { ...opts, headers, body, credentials: 'include' });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  if (res.status === 204) return null;
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}

async function fetchWho() {
  try {
    const me = await api('/auth/whoami');
    $who.textContent = me.display_name || '(anonymous)';
  } catch (err) {
    $who.textContent = '(unknown)';
  }
}

async function refreshMembership() {
  try {
    const mine = await api('/rooms/mine');
    myMembership = (mine || []).find((r) => r.code === code) || null;
  } catch (err) {
    myMembership = null;
  }
}

function roomGone(err) {
  // `api()` prefixes the HTTP status, so a missing room surfaces as
  // "404: room not found". Match on either signal.
  const m = (err && err.message) || '';
  return m.startsWith('404') || m.toLowerCase().includes('room not found');
}

function showRoomGone() {
  $error.textContent = '';
  $error.innerHTML =
    'Dieser Raum existiert nicht mehr — er wurde evtl. beendet oder ist abgelaufen. ' +
    '<a href="/home">Zur Startseite</a>';
}

async function refresh() {
  $error.textContent = '';
  try {
    [currentRoomState] = await Promise.all([
      api(`/rooms/${code}`),
      refreshMembership(),
    ]);
    render();
  } catch (err) {
    if (roomGone(err)) {
      showRoomGone();
    } else {
      $error.textContent = err.message;
    }
  }
}

function render() {
  if (!currentRoomState) return;
  $code.textContent = currentRoomState.code;
  $stateValue.textContent = currentRoomState.state;

  // Derive host / lobby state up front so it is available when rendering
  // per-seat AI dropdowns (which need to know whether to enable themselves).
  const isLobby = currentRoomState.state === 'lobby';
  const seated = myMembership && myMembership.role === 'seat';
  const spectating = myMembership && myMembership.role === 'spectator';
  let amHost = false;
  if (seated) {
    const mySeatRow = currentRoomState.seats.find(
      (s) => s.position === myMembership.position
    );
    amHost = !!(mySeatRow && mySeatRow.is_host);
  }

  $seats.innerHTML = '';
  for (const s of currentRoomState.seats) {
    const li = document.createElement('li');
    const flags = [];
    if (s.is_host) flags.push('HOST');
    if (s.is_ai) flags.push('AI');
    if (!s.connected && !s.is_ai) flags.push('paused');
    const tag = flags.length ? ' [' + flags.join(' ') + ']' : '';
    li.textContent = `${s.position}: ${s.display_name}${tag}`;
    if (myMembership && myMembership.role === 'seat'
        && myMembership.position === s.position) {
      li.classList.add('me');
    }

    if (s.is_ai) {
      const sel = document.createElement('select');
      sel.className = 'ai-difficulty';
      sel.dataset.position = s.position;
      for (const lvl of ['easy', 'medium', 'hard']) {
        const opt = document.createElement('option');
        opt.value = lvl;
        opt.textContent = lvl;
        if (lvl === s.ai_difficulty) opt.selected = true;
        sel.appendChild(opt);
      }
      sel.disabled = !amHost || !isLobby;
      sel.addEventListener('change', async (ev) => {
        try {
          await api(`/rooms/${currentRoomState.code}/ai_difficulty`, {
            method: 'POST',
            body: { position: ev.target.dataset.position, level: ev.target.value },
          });
        } catch (err) {
          $error.textContent = err.message;
          await refresh();   // revert dropdown to server state
        }
      });
      li.appendChild(sel);
    }

    $seats.appendChild(li);
  }

  $variantList.innerHTML = '';
  for (const [k, v] of Object.entries(currentRoomState.variant || {})) {
    const li = document.createElement('li');
    li.textContent = `${k}: ${v ? 'on' : 'off'}`;
    $variantList.appendChild(li);
  }
  $spectatorCount.textContent = currentRoomState.spectator_count;

  $btnJoin.hidden = !isLobby || !!seated;
  $btnLeave.hidden = !seated;
  $btnSpectate.hidden = !!seated || !!spectating;
  $btnStopSpectate.hidden = !spectating;
  $btnStart.hidden = !(amHost && isLobby);

  $currentTargetScore.textContent = currentRoomState.end_game || 1000;
  $targetScoreControls.hidden = !(amHost && isLobby);
  
  btnTargets.forEach(btn => {
    btn.style.fontWeight = (parseInt(btn.dataset.score) === currentRoomState.end_game) ? 'bold' : 'normal';
  });
}

btnTargets.forEach(btn => {
  btn.addEventListener('click', () => withErrors(async () => {
    await api(`/rooms/${code}/target_score`, {
      method: 'POST',
      body: { target: parseInt(btn.dataset.score) }
    });
    await refresh();
  }));
});

async function withErrors(fn) {
  $error.textContent = '';
  try { await fn(); } catch (err) { $error.textContent = err.message; }
}

$btnJoin.addEventListener('click', () => withErrors(async () => {
  await api(`/rooms/${code}/join`, { method: 'POST', body: {} });
  await refresh();
  openWs();
}));

$btnLeave.addEventListener('click', () => withErrors(async () => {
  await api(`/rooms/${code}/leave`, { method: 'POST', body: {} });
  if (ws) { try { ws.close(); } catch (_) {} ws = null; }
  await refresh();
}));

$btnSpectate.addEventListener('click', () => withErrors(async () => {
  await api(`/rooms/${code}/spectate`, { method: 'POST' });
  await refresh();
  openWs();
}));

$btnStopSpectate.addEventListener('click', () => withErrors(async () => {
  await api(`/rooms/${code}/leave-spectator`, { method: 'POST' });
  if (ws) { try { ws.close(); } catch (_) {} ws = null; }
  await refresh();
}));

$btnStart.addEventListener('click', () => withErrors(async () => {
  await api(`/rooms/${code}/start`, { method: 'POST' });
  await refresh();
}));

let ws = null;
function openWs() {
  if (ws) return;
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${window.location.host}/ws/${code}`);
  ws.addEventListener('message', (ev) => {
    let msg = null;
    try { msg = JSON.parse(ev.data); } catch (_) { return; }
    handleWsMessage(msg);
  });
  ws.addEventListener('close', () => { ws = null; });
  ws.addEventListener('error', () => { /* surfaced via close */ });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function appendChatMessage(fromName, text) {
  const box = document.getElementById('chat-messages');
  if (!box) return;
  const div = document.createElement('div');
  div.className = 'chat-entry';
  div.innerHTML = `<span class="chat-sender">${escapeHtml(fromName)}:</span> ${escapeHtml(text)}`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function sendChatMessage() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  const input = document.getElementById('chat-input');
  const text = (input.value || '').trim();
  if (!text) return;
  ws.send(JSON.stringify({ type: 'chat', text }));
  input.value = '';
}

const $chatSend = document.getElementById('chat-send');
const $chatInput = document.getElementById('chat-input');
if ($chatSend) $chatSend.addEventListener('click', sendChatMessage);
if ($chatInput) $chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') { e.preventDefault(); sendChatMessage(); }
});

function handleWsMessage(msg) {
  if (!msg || !msg.type) return;
  if (msg.type === 'chat_message') {
    appendChatMessage(msg.from_name || '?', msg.text || '');
    return;
  }
  // Lobby-relevant lifecycle events: refresh state.
  // These are the ACTUAL event names the server emits (per the
  // schieber-protocol skill).  An earlier draft listened on
  // `seat_joined` / `seat_left` / etc., but the backend never emitted
  // those — leaving the lobby stale until a manual reload.
  const lobbyEvents = new Set([
    'seat_changed',
    'seat_paused',
    'seat_reclaimed',
    'seat_ai_takeover',
    'seat_kicked',
    'host_changed',
    'spectator_count_changed',
    'target_score_changed',
  ]);
  if (lobbyEvents.has(msg.type)) {
    refresh();
    return;
  }
  if (msg.type === 'game_start' || msg.type === 'round_start') {
    // Hand off to the game UI. Task 23 makes this in-place; for now redirect.
    window.location.href = `/?code=${code}`;
  }
}

(async () => {
  if (!code) {
    window.location.href = '/home';
    return;
  }
  await fetchWho();
  await refresh();
  // If already seated or spectating, open the WS proactively so updates flow in.
  if (myMembership) openWs();
})();
