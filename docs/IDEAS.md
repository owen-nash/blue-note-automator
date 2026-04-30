# Future Projects & Ideas: Blue Note Automator

## 🎺 Project: Jazz News Herald (The "Daily Brief")
**Status**: COMPLETED (April 2026)
- **Scouting**: RSS + local Playwright for deep extraction (Ethan Iverson, Nate Chinen, DownBeat, etc).
- **Curation**: Claude 3.7 Sonnet with hybrid taste profile & expert drummer focus.
- **Persistence**: SQLite with 30-day auto-pruning to avoid duplicates.
- **Delivery**: Daily 8 AM Discord loop + \`/herald\` slash command.

---

## 🎹 Feedback Loop (The "Love/Hate" Engine)
**Status**: Backlog
- Integrate "Love" button on Discord embeds to trigger Last.fm favorites.
- Integrate "Not For Me" button to update \`blacklist.json\`.

## 📂 Digital Liner Notes
**Status**: Backlog
- Automatically generate a \`personnel.md\` or \`notes.txt\` via Claude 3.7 whenever an album is successfully downloaded, placing it in the Navidrome directory.

## 🥁 [Proposed] Personnel Proximity Graph
- Track sidemen (drums, bass, piano) from saved/loved albums.
- Prioritize new discoveries based on the "Sideman Network" (e.g., "If you like Bill Stewart with Scofield, you might like this trio with Larry Goldings").

## 💬 [Proposed] Granular Discord Feedback
- Add a "Critique" button to Discord.
- Feed user reasons for rejection (e.g., "Too polished," "Need more avant-garde") back into the Claude 4.6 System Prompt.

## 🎧 [Proposed] Acoustic Semantic Search
- Use ChromaDB to compare the acoustic fingerprint (BPM, Energy, Timbre) of new discoveries against your top 100 library tracks.
