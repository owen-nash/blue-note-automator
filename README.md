# 🎷 Blue Note Automator (2026 Edition)

**High-fidelity jazz discovery for the serious head.**

Blue Note Automator is a serverless music curation and library management system designed for a jazz practitioner's ear (specifically optimized for drummers). 

## 🚀 2026 Architecture
The project has been migrated from a monolithic VM setup to a state-of-the-art serverless stack:
- **Client (Gateway):** Persistent Discord bot hosted on **Fly.io**.
- **Intelligence Layer:** High-compute reasoning and verification functions hosted on **Modal.com**.
- **Models:** Dual-model pipeline via **OpenRouter**:
  - **Claude 4.6 Sonnet (Analyst):** Musical verification & ground truth.
  - **Claude 4.7 Opus (Writer):** Narrative drafting.
- **Memory:** **Mem0** (Managed) + **Voyage AI** embeddings stored in **Neon Postgres (pgvector)**.

---

## 🎺 Core Modules

### 1. The Analyst (Modal)
- **Tool-Use:** Uses MusicBrainz MCP and YouTube Music API to verify every discovery before sending.
- **Memory Integration:** Consults your "Musical Soul" via Mem0 to ensure recommendations mature with your taste.

### 2. The Writer (Modal)
- **Narrative:** Drafts engaging, musician-centric summaries of discoveries that highlight technical player details.

### 3. The Jazz News Herald (Modal)
- **Scouting:** RSS extraction with Playwright.
- **Curation:** Filters news based on practitioner relevance.

---

## 🤖 Discord Interface
- `/discover`: Triggers 5 fresh jazz discoveries verified against real databases.
- `/herald`: Curates the latest high-signal jazz dispatches.

---

## 🛠️ Setup

### Intelligence (Modal)
1. Deploy the Modal app:
   \`\`\`bash
   cd intelligence && modal deploy modal_app.py
   \`\`\`

### Bot (Fly.io)
1. Set up secrets:
   \`\`\`bash
   fly secrets set DISCORD_BOT_TOKEN=... LASTFM_API_KEY=...
   \`\`\`
2. Deploy the bot:
   \`\`\`bash
   cd bot && fly deploy
   \`\`\`
