---
name: schieber-build
description: Orchestrator for Schieber card-game development. Coordinates `schieber-backend`, `schieber-frontend`, `schieber-qa`, `schieber-reviewer` agents. Trigger for any Schieber build/implement/fix/test work — "implement next task", "finish Schieber", "continue the frontend", "add websocket endpoint", "fix the trump phase", "run QA on Schieber", "review the game session", and all rerun / refine / iterate / update / modify variants of the above. Also trigger on "Schieber" + test/smoke/integration. Do NOT trigger for pure questions answered from the codebase (rule lookups, protocol lookups) — answer those directly.
---

# Schieber Build Orchestrator

Coordinates the 4-agent team (`schieber-backend`, `schieber-frontend`, `schieber-qa`, `schieber-reviewer`) through a batch of plan tasks from `docs/superpowers/plans/2026-04-13-schieber-html5-frontend.md`.

**Execution mode: hybrid.** Backend + frontend run as an **agent team** in the build phase (parallel with inter-agent messaging). QA and reviewer run as **single subagents** after build.

## Phase 0: Context Check

Before dispatching anything:

1. Check if `_workspace/` exists under project root.
2. Check the current state of the 15 plan tasks (grep the plan file for `- [x]` vs `- [ ]`, or read commit log).
3. Decide mode:
   - **Initial run** — no `_workspace/`, no work items queued yet → start fresh.
   - **Continuation** — `_workspace/` present, next plan task(s) ready → read latest `_workspace/*.md` artifacts for context, continue from the next uncompleted task.
   - **Partial re-run** — user asks to redo a specific task/module → move `_workspace/` → `_workspace_prev/`, rerun only the affected agent(s).
   - **New batch** — user gives a fresh scope outside the plan → treat as initial run, create plan addendum if needed.

Report mode chosen to the user in one sentence before starting.

## Phase 1: Scope

Determine the batch of plan tasks for this run. Default batch size: **2–4 tasks** (keeps QA scope manageable).

1. Read current plan progress.
2. Pick next batch.
3. Split tasks by agent:
   - Backend-only tasks (7, 8, 9 for example): to `schieber-backend`.
   - Frontend-only tasks (13, 14): to `schieber-frontend`.
   - Mixed tasks (10, 15): split — decide which file goes where.

## Phase 2: Team Build (Agent Team)

**Execution mode:** agent team. Use `TeamCreate` with `schieber-backend` and `schieber-frontend`, then `TaskCreate` with tasks for each.

```
TeamCreate({
  team_name: "schieber-build",
  members: ["schieber-backend", "schieber-frontend"]
})
```

Spawn both Agents with `model: "opus"` and `run_in_background: true`. Backend writes protocol-touching code; if it needs to extend the protocol, it updates the `schieber-protocol` skill AND sends a `PROTOCOL_DELTA` message to frontend. Frontend consumes the current skill state; if it has a question, it sends `PROTOCOL_Q` to backend.

Monitor for completion. When both agents report done, proceed.

**Artifacts produced:**
- `_workspace/{N}_backend_note.md` — backend summary: files changed, tests added, protocol deltas.
- `_workspace/{N}_frontend_note.md` — frontend summary: files changed, handlers, UX notes.

`N` = batch index (0-padded two digits).

## Phase 3: QA (Subagent)

**Execution mode:** single subagent. After Phase 2 team completes, teardown team (`TeamDelete`) and spawn `schieber-qa` via `Agent` tool with `model: "opus"`.

Pass QA the batch scope and pointers to backend/frontend notes. QA writes `_workspace/{N}_qa_report.md` and returns verdict: GREEN / YELLOW / RED.

- **RED**: blocker defects. Return to Phase 2 — spawn a new team with scoped fix instructions drawn from the QA report. Loop until GREEN or YELLOW.
- **YELLOW**: non-blocker defects. Proceed to Phase 4 but surface defects for the user's decision.
- **GREEN**: proceed to Phase 4.

## Phase 4: Review (Subagent)

**Execution mode:** single subagent. Spawn `schieber-reviewer` via `Agent` tool with `model: "opus"`. Pass the batch scope, QA report, and diff range.

Reviewer writes `_workspace/{N}_review.md` and returns APPROVE or REQUEST_CHANGES.

- **REQUEST_CHANGES** with BLOCKER findings: return to Phase 2 scoped fix.
- **REQUEST_CHANGES** with only MAJOR / MINOR / NIT: surface to user, ask whether to address now or defer.
- **APPROVE**: proceed to Phase 5.

## Phase 5: Commit & Plan Update

1. Create git commit per plan convention (see plan file — each task has its own commit message).
2. Tick the `- [x]` boxes in the plan file for completed tasks.
3. Report to user: tasks completed, defects open, next batch recommended.

## Phase 6: Feedback

Ask user: "Anything about the flow, agent behavior, or protocol to adjust?" If yes, update the relevant agent/skill file and record the change in CLAUDE.md's harness changelog.

## Data Flow

- **Shared contract:** `schieber-protocol` skill (WebSocket), `schieber-game-rules` skill (game logic). All agents read these.
- **Inter-agent messaging (Phase 2):** `SendMessage` for `PROTOCOL_DELTA` / `PROTOCOL_Q` / "ready for QA".
- **Task tracking (Phase 2):** `TaskCreate` per plan task, dependencies between backend and frontend where protocol overlaps.
- **Artifacts:** `_workspace/` under project root. Naming: `{NN}_{agent}_{kind}.md`. Examples: `03_backend_note.md`, `03_qa_report.md`, `03_review.md`.
- **Reviewer independence:** reviewer only sees workspace artifacts and the git diff, never the live agents.

## Error Handling

| Situation | Action |
|-----------|--------|
| Agent test suite fails | Agent re-attempts once; second failure — report to orchestrator, pause, ask user. |
| Protocol skill ambiguous | Backend proposes amendment in its note, orchestrator confirms with user before adopting. |
| QA flags a skill gap | Update the skill file in a separate step; note the update in CLAUDE.md changelog. |
| Smoke test needs running server | Backend spawns `uvicorn` in background; QA connects. If port 8765 busy, use 8766. |
| `_workspace/` collision with prior partial run | Move to `_workspace_prev/` before new run, do not delete. |
| Two teammates disagree on field semantics | Orchestrator reads the skill, issues a ruling, records as note in `_workspace/{N}_ruling.md`. |

## Test Scenarios

### Happy path
User: "continue Schieber — do tasks 7 and 8".
→ Phase 0 reads `_workspace/` (continuation), Phase 1 picks tasks 7 (Weis) and 8 (trick loop), both backend.
→ Phase 2 spawns backend agent only (no frontend work needed for 7/8). Team of 1 is fine — actually degenerate to subagent direct call.
→ Phase 3 QA. Phase 4 review. Phase 5 commits. User notified.

### Protocol change path
User: "add a `can_undo` field to `your_turn`".
→ Phase 0 new batch.
→ Phase 1 scope = backend (server-side) + frontend (handler) + protocol skill update.
→ Phase 2 team. Backend updates skill FIRST, sends `PROTOCOL_DELTA` to frontend. Frontend updates handler.
→ Phase 3 QA verifies both sides read same field.
→ Phase 4 review. Commit.

### Failure path
QA reports BLOCKER: backend sends `trick_end.winner` as internal key but frontend reads display name.
→ Orchestrator returns to Phase 2 with scoped fix: "backend: align `trick_end.winner` with protocol skill (display name)". Re-run QA. Loop until GREEN.

## Team Size

For Schieber this harness: 2 active build members (backend + frontend) plus 2 sequential subagents (QA, reviewer). Do not exceed 3 build members — the domain does not split finer.
