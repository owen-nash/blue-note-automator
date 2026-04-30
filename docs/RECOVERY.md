# Blue Note Automator — Recovery & State Document

> Generated: 2026-04-30T21:30:00Z

## Server
- **IP:** 207.246.90.230 | **SSH:** ssh root@207.246.90.230 (password: TempPass123!)
- **OS:** Arch Linux, Go 1.26.2, Python 3.14.4, Node v25.9.0, Kilo v7.2.31

## Gas Town — `/opt/gastown`
- **CLI:** gt v1.0.1, bd v1.0.3, dolt v1.86.6
- **Default agent:** `kilo` (DeepSeek V4 Flash via KiloCode)
- **Worker agent:** `modal-worker` (Qwen3.6-35B-A3B on Modal L4, $0.96/hr)

### Agents
| Name | Model | Provider |
|------|-------|----------|
| `kilo` (default, Mayor) | DeepSeek V4 Flash | KiloCode |
| `kilo-flash` | DeepSeek V4 Flash | KiloCode |
| `modal-worker` | Qwen3.6-35B-A3B (MoE) | Modal L4 |

### Modal Deployments
| App | Model | GPU | Cost/hr | Endpoint |
|-----|-------|-----|---------|----------|
| gastown-qwen | Qwen2.5-Coder-7B (fallback) | T4 | $0.46 | `...-qwen-qwencoder-generate.modal.run` |
| gastown-worker | Qwen3.6-35B-A3B (workers) | L4 | $0.96 | `...-worker-workermodel-generate.modal.run` |

### Modal Proxy (systemd)
- Service: `modal-proxy.service` — auto-starts on boot
- Port: 8000 (127.0.0.1)
- Routes: Qwen/Worker endpoints by model name

### 25 Beads — All Closed
All brain fix, feedback, cron, playlist, Mem0, and Modal inference beads complete.

## Git — 18 commits on origin/main
Last commit: `3f00f32` — per-album messages fix
Worker model files: `gastown_qwen.py`, `gastown_worker.py`, `gastown_dscoder.py`

## Blue Note Automator — OpenRouter (unchanged)
- discover: Claude Sonnet 4.6 / Opus 4.7
- herald: Claude Sonnet 4.6
- sync_taste, crons: Same stack

## Resume
```bash
ssh root@207.246.90.230
export PATH="$HOME/go/bin:/usr/local/bin:/root/.fly/bin:$PATH"
source /etc/profile.d/kilocode.sh
cd /opt/gastown
gt mayor status
```
