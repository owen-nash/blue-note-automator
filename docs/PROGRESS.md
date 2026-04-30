# Blue Note Automator - Development Progress Log

## Project State
- **Root Path**: \`/home/ownash/blue-note-automator\`
- **Media Path**: \`/opt/selfhosted/media/music\`
- **Knowledge Path**: (Pending discovery of SilverBullet data dir)

## Resolved Issues
- **Permission Bug**: Discovered that Navidrome requires \`root:root\` ownership and \`755\` permissions for library files.
- **Migration**: Successfully moved existing downloads from \`~/Music/Tiddl\` to the media folder and fixed permissions.
- **Config**: Updated \`tiddl.json\` to point directly to the media folder.

## Task Log
- [x] Initial Research & Planning
- [x] Environment Setup (Venv created)
- [x] Dependency Installation (Playwright, CrewAI, etc.)
- [x] Scout Module: Local Library Taste Analysis (Done)
- [x] Gatekeeper Module: Claude 3.7 Sonnet Integration (Done)
- [x] Archivist Module: Tiddl & Beets automation + Permission enforcement (Done)
- [x] Beets LLM Tagger: Interactive pexpect tagger with Llama 3.1 8B (Done)
- [x] Correspondent Module: Discord Reporting (Done)
- [x] Curator Module: Stylistic Analysis & RAG (Done)
- [x] Curator Module: Discord Playlist Breakdown (Done)
- [x] Curator Module: Daily Playlist Generation (Done)
- [x] Curator Module: Seed Playlists (Done)
- [x] Orchestration: Main execution loop (Done)
- [x] Scheduling: Weekly Automator + Daily Curator (Done)
- [x] CLI Helper: 'beet-tag' command (Done)
- [x] Migration to Fly.io & Modal (April 28, 2026)
- [x] Integration with OpenRouter & Mem0 (April 28, 2026)

## Session End (2026-04-26)
- **Status**: System stable.
- **Wider Context**: Integration with the new \`homelab_orch\` global CrewAI manager documented.
- **Model Strategy**: Transitioned to Deepseek v4 Pro (Manager) and Claude Sonnet 4.6 (Creative).
