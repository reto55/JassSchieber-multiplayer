'use strict';

// ─── Home Page logic ─────────────────────────────────────────────────────────
//
// Drives the landing page where users can create a new room or join an existing one.

const $error = document.getElementById('error');
const $btnCreate = document.getElementById('btn-create');
const $formJoin = document.getElementById('form-join');
const $inputCode = document.getElementById('input-code');

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

function showError(msg) {
  if (!msg) {
    $error.hidden = true;
    $error.textContent = '';
  } else {
    $error.hidden = false;
    $error.textContent = msg;
  }
}

async function handleCreateRoom() {
  try {
    $btnCreate.disabled = true;
    showError(null);
    
    // Create a new room with default variant settings
    const room = await api('/rooms', { method: 'POST', body: {} });
    
    if (room && room.code) {
      window.location.href = `/lobby?code=${room.code}`;
    } else {
      throw new Error("Invalid response from server");
    }
  } catch (err) {
    showError(err.message);
    $btnCreate.disabled = false;
  }
}

function handleJoinRoom(e) {
  e.preventDefault();
  const code = $inputCode.value.trim().toUpperCase();
  
  if (!code) {
    showError('Please enter a valid room code.');
    return;
  }
  
  // Just redirect to the lobby with the code.
  // The lobby page will attempt to fetch room details and display errors if not found.
  window.location.href = `/lobby?code=${code}`;
}

// ─── Auth strip ───────────────────────────────────────────────────────────────

async function bootAuth() {
  try {
    const r = await fetch('/auth/whoami', { credentials: 'same-origin' });
    const me = await r.json();
    const el = document.getElementById('auth-info');
    if (!el) return;
    
    if (me.kind === 'user') {
      const verified = me.is_verified ? '✓' : '⚠';
      el.innerHTML = `${escapeHtml(me.display_name)} (${verified}) ` +
                     `<a href="/account">Account</a> · ` +
                     `<a href="#" id="logoutBtn">Logout</a>`;
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
                     `<a href="/login">Sign in</a> · ` +
                     `<a href="/signup">Sign up</a>`;
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

// ─── Initialization ───────────────────────────────────────────────────────────

$btnCreate.addEventListener('click', handleCreateRoom);
$formJoin.addEventListener('submit', handleJoinRoom);

bootAuth();
