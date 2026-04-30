# Blue Note Automator — Recovery & State Document

> Generated: 2026-04-30T05:30:00Z
> Purpose: If the agent disconnects or runs out of tokens, this file contains
> everything needed to resume from scratch.

## 1. Server

- **IP:** 207.246.90.230
- **SSH:** `ssh -i ~/.ssh/id_ed25519 root@207.246.90.230`
- **OS:** Arch Linux x86_64, 3.8GB RAM, 75GB disk + 11GB swap
- **Location:** Pontiac, MI / America/Detroit (UTC-4)

### Dev Tools
- Go 1.26.2, Python 3.14.4, Node v25.9.0, git 2.54
- Base-devel, tmux, htop, jq, neovim

### Git Auth
- Credential helper (ghp token) configured in ~/.git-credentials
- Remote: https://github.com/owen-nash/blue-note-automator

## 2. Gas Town

- **Root:** `/opt/gastown`
- **CLI:** gt v1.0.1, bd v1.0.3, dolt v1.86.6
- **PATH:** `$HOME/go/bin:/usr/local/bin:$PATH`
- **Config:** `/opt/gastown/settings/config.json`

### Agents
| Name | Model | Purpose |
|------|-------|---------|
| `kilo` (default) | `kilo/moonshotai/kimi-k2.6` | Mayor orchestration |
| `kilo-flash` | `kilo/deepseek/deepseek-v4-flash` | Affordable coding |

### Rigs
| Rig | Status |
|-----|--------|
| `blue_note_automator` | 🟢 Running (witness + refinery active) |
| `budget_platform` | 🟢 Running |
| `poetry_factory` | 🟢 Running |

### Daemon Patrols (3min heartbeat)
- **Deacon** — town patrol, auto-sligns mol-deacon-patrol
- **Refinery** — merge queue + git operations
- **Witness** — monitors polecats
- **Dolt backup** — every 15min

### Active Tmux Sessions
| Session | Role | Model |
|---------|------|-------|
| `hq-mayor` | Mayor (orchestrator) | `kilo/moonshotai/kimi-k2.6` |
| `hq-deacon` | Deacon (patrol) | `kilo/kilo-auto/balanced` |
| `bna-refinery` | Refinery (BNA rig) | `kilo/moonshotai/kimi-k2.6` |
| `bna-witness` | Witness (BNA rig) | `kilo/moonshotai/kimi-k2.6` |

## 3. Beads (Issue Tracker)

Beads live in `/opt/gastown/blue_note_automator/.beads/` (embedded Dolt).

### bna-93b — ✅ CLOSED
- **Title:** Add 6hr cron for taste profile sync  
- **Status:** Closed (completed by polecat chrome)  
- **Branch:** `polecat/chrome/bna-93b@mokzxypn`  
- **Commit:** `cfcc575` — `feat: add 6hr Modal cron for taste profile sync`  
- **MR created:** `Merge: bna-93b` (pending merge)

### bna-lre — ✅ COMPLETED
- **Title:** Build sync_taste ingestion pipeline  
- **Status:** Open (needs bead close)  
- **Commit:** `af9fab4` — `feat(bna-lre): add sync_taste() ingestion pipeline`  

### bna-fl8 — ✅ COMPLETED
- **Title:** Fix user_id plumbing  
- **Status:** Open (needs bead close)  
- **Commit:** `a8c4a32` — `fix(bna-fl8): unify user_id plumbing`  

### bna-lre — ✅ CLOSED
- **Title:** Build sync_taste ingestion pipeline
- **Status:** Closed
- **Commit:** 02d1b5d — 
- **Note:** Renamed to  in 785d823

### bna-fl8 — ✅ CLOSED
- **Title:** Fix user_id plumbing
- **Status:** Closed
- **Commit:** 2b36ce9 — 

### bna-bgw — ✅ CLOSED
- **Title:** Wire Mem0 search into discover_and_herald
- **Status:** Closed
- **Commit:** 4e339fe — 

### bna-93b — ✅ CLOSED
- **Title:** Add 6hr cron for taste profile sync
- **Status:** Closed, PR merged
- **Commit:** cfcc575 — 

### Fix commit — ✅ PUSHED
- **Commit:** 785d823 — 
### Pending Wisps (open molecules, can be force-closed)
- `bna-wisp-0qw` — stale (from rust polecat)  
- `bna-wisp-ee6` — stale (from rust polecat)  

## 4. Git History (crew/rex, pushed to origin/main)

```
16dd624 feat(bna-bgw): wire Mem0 search into discover (limit=5) and herald (limit=10)
a8c4a32 fix(bna-fl8): unify user_id plumbing across bot and Modal via TASTE_USER_ID
af9fab4 feat(bna-lre): add sync_taste() ingestion pipeline for Last.fm -> Mem0 taste sync
00e3863 chore: update .gitignore for Gas Town + secrets exclusion
4415b2b Initial commit: Consolidated 2026 Serverless Jazz Stack
```

Files changed in crew/rex:
- `intelligence/modal_app.py` — sync_taste() added, discover() uses m.search(), herald gets Mem0 context
- `bot/bot.py` — TASTE_USER_ID from env instead of Discord user ID
- `.env` — added TASTE_USER_ID
- `secrets.env` — added TASTE_USER_ID

## 5. Secrets (.env keys)
Located at `/opt/gastown/blue_note_automator/crew/rex/.env`:
- OPENROUTER_API_KEY ✓
- DISCORD_BOT_TOKEN ✓
- MEM0_API_KEY ✓
- VOYAGE_API_KEY ✓
- NEON_DB_URL ✓
- LASTFM_API_KEY / LASTFM_API_SECRET ✓
- LASTFM_USER ✓
- TASTE_USER_ID ✓
- GITHUB_TOKEN ✓
- KILOCODE_API_KEY ✓ (for Mayor)

Secrets also mirrored in `/opt/gastown/blue_note_automator/crew/rex/secrets.env`.

## 6. Resume Quickstart

```bash
# 1. SSH in
ssh -i ~/.ssh/id_ed25519 root@207.246.90.230

# 2. Load environment
export PATH="$HOME/go/bin:/usr/local/bin:$PATH"
source /etc/profile.d/kilocode.sh
cd /opt/gastown

# 3. Check Gas Town state
gt mayor status        # Should show running
gt convoy list          # Show active convoys
cd blue_note_automator && bd list  # Show all beads

# 4. Close completed beads
bd close bna-lre --force -m "Implemented and pushed"
bd close bna-fl8 --force -m "Implemented and pushed"
bd close bna-bgw --force -m "Implemented and pushed"

# 5. Start working on new beads
cd /opt/gastown/blue_note_automator/crew/rex
source .env
cat brain-fix-prompt.txt | kilo run --model kilo/deepseek/deepseek-v4-flash --auto
```

## 7. Known Issues
- Polcat session start keeps getting deferred for newly spawned polecats
- Workaround: manually create tmux session and launch Kilo CLI
- Dolt server on port 3307 (embedded beads DB may have lock contention)
