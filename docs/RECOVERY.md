# Blue Note Automator — Recovery & State Document

> Generated: 2026-04-30T05:30:00Z
> Purpose: If the agent disconnects or runs out of tokens, this file contains
> everything needed to resume from scratch.

## 1. Server

- **IP:** 207.246.90.230
- **SSH:** ssh -i ~/.ssh/id_ed25519 root@207.246.90.230
- **OS:** Arch Linux x86_64, 3.8GB RAM, 75GB disk + 11GB swap

### Dev Tools
- Go 1.26.2, Python 3.14.4, Node v25.9.0, git 2.54, Kilo CLI v7.2.31

### Git Auth
- Credential helper in ~/.git-credentials
- Remote: https://github.com/owen-nash/blue-note-automator

## 2. Gas Town

- **Root:** /opt/gastown
- **CLI:** gt v1.0.1, bd v1.0.3, dolt v1.86.6
- **PATH:** /root/go/bin:/usr/local/bin:/root/go/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/bin

### Agents
| Name | Model | Purpose |
|------|-------|---------|
| kilo (default) | moonshotai/kimi-k2.6 | Mayor orchestration |
| kilo-flash | deepseek/deepseek-v4-flash | Affordable coding |

### Rigs: blue_note_automator, budget_platform, poetry_factory

## 3. Git History (origin/main)
aaa0bc5 docs: update RECOVERY.md
785d823 fix: merge sync_taste naming conflict, enrich_taste_profile per-artist, cron calls it
2f9cd7b docs: add RECOVERY.md with full state capture
4e339fe feat(bna-bgw): wire Mem0 search into discover (limit=5) and herald (limit=10)
2b36ce9 fix(bna-fl8): unify user_id plumbing across bot and Modal via TASTE_USER_ID
02d1b5d feat(bna-lre): add sync_taste() ingestion pipeline
29a0683 Merge pull request #1 from owen-nash/polecat/chrome/bna-93b (cron)
cfcc575 feat: add 6hr Modal cron for taste profile sync
00e3863 chore: update .gitignore
4415b2b Initial commit

## 4. Beads — All Closed
- bna-93b: cron task, merged by PR #1
- bna-lre: sync_taste pipeline, now enrich_taste_profile()
- bna-fl8: user_id plumbing fixed
- bna-bgw: Mem0 search wired into discover/herald

## 5. Resume Quickstart

