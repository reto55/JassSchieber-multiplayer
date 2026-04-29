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

async function refresh() {
  $error.textContent = '';
  try {
    [currentRoomState] = await Promise.all([
      api(`/rooms/${code}`),
      refreshMembership(),
    ]);
    render();
  } catch (err) {
    $error.textContent = err.message;
  }
}

function render() {
  if (!currentRoomState) return;
  $code.textContent = currentRoomState.code;
  $stateValue.textContent = currentRoomState.state;

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
    $seats.appendChild(li);
  }

  $variantList.innerHTML = '';
  for (const [k, v] of Object.entries(currentRoomState.variant || {})) {
    const li = document.createElement('li');
    li.textContent = `${k}: ${v ? 'on' : 'off'}`;
    $variantList.appendChild(li);
  }
  $spectatorCount.textContent = currentRoomState.spectator_count;

  // Button gating: derive from membership + room state.
  const isLobby = currentRoomState.state === 'lobby';
  const seated = myMembership && myMembership.role === 'seat';
  const spectating = myMembership && myMembership.role === 'spectator';
  let isHost = false;
  if (seated) {
    const mySeat = currentRoomState.seats.find(
      (s) => s.position === myMembership.position
    );
    isHost = !!(mySeat && mySeat.is_host);
  }

  $btnJoin.hidden = !isLobby || !!seated;
  $btnLeave.hidden = !seated;
  $btnSpectate.hidden = !!seated || !!spectating;
  $btnStopSpectate.hidden = !spectating;
  $btnStart.hidden = !(isHost && isLobby);
}

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

function handleWsMessage(msg) {
  if (!msg || !msg.type) return;
  // Lobby-relevant lifecycle events: refresh state.
  const lobbyEvents = new Set([
    'seat_joined', 'seat_left', 'seat_kicked',
    'seat_disconnected', 'seat_reconnected',
    'host_changed', 'spectator_joined', 'spectator_left',
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
    $error.textContent = 'Missing ?code=ABCDEF in URL.';
    return;
  }
  await fetchWho();
  await refresh();
  // If already seated or spectating, open the WS proactively so updates flow in.
  if (myMembership) openWs();
})();
