'use strict';

// ─── Constants ───────────────────────────────────────────────────────────────
const WS_URL = `ws://${location.host}/ws`;

const SUIT_EMOJI = {
  Eicheln: '🌳', Rosen: '🌹', Schellen: '🔔', Schilten: '🛡',
  Oben: '⬆', Unten: '⬇',
};

// Server uses 'player_key' strings like 'comps'; position label → key map
const LABEL_TO_KEY = { Süd: 'comps', Nord: 'compn', Ost: 'compo', West: 'compe' };

// ─── Game state ───────────────────────────────────────────────────────────────
const state = {
  hand: [],               // card codes for human's 9 cards
  scores: { sn: 0, ow: 0 },
  targetScore: 1000,
  cardCounts: { compe: 0, compn: 0, compo: 0 },
  trick: { comps: null, compn: null, compo: null, compe: null },
  validCards: [],
  operator: null,
};

// ─── WebSocket ────────────────────────────────────────────────────────────────
let ws = null;

function connect() {
  ws = new WebSocket(WS_URL);
  ws.onopen = () => appendLog('Verbunden — Karten werden verteilt…');
  ws.onmessage = (e) => dispatch(JSON.parse(e.data));
  ws.onclose = () => appendLog('Verbindung getrennt.');
  ws.onerror = () => appendLog('Verbindungsfehler.', 'error');
}

function send(msg) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
  }
}

function dispatch(msg) {
  const handlers = {
    game_start:    onGameStart,
    trump_request: onTrumpRequest,
    trump_chosen:  onTrumpChosen,
    weis_request:  onWeisRequest,
    weis_result:   onWeisResult,
    your_turn:     onYourTurn,
    card_played:   onCardPlayed,
    trick_end:     onTrickEnd,
    round_end:     onRoundEnd,
    game_end:      onGameEnd,
    error:         (m) => appendLog(`Fehler: ${m.message}`, 'error'),
  };
  const fn = handlers[msg.type];
  if (fn) fn(msg);
}

connect();
