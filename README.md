<div align="center">

```
███╗   ███╗██╗   ██╗███████╗████████╗██╗ ██████╗
████╗ ████║╚██╗ ██╔╝██╔════╝╚══██╔══╝██║██╔════╝
██╔████╔██║ ╚████╔╝ ███████╗   ██║   ██║██║
██║╚██╔╝██║  ╚██╔╝  ╚════██║   ██║   ██║██║
██║ ╚═╝ ██║   ██║   ███████║   ██║   ██║╚██████╗
╚═╝     ╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝ ╚═════╝
   █████╗  ██████╗ ███████╗███╗   ██╗████████╗
  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║
  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║
  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝
```

**Your open-source Jarvis. Self-hosted, autonomous, accountable.**

🚧 **Status: early development** — nothing to install yet, watch the repo.

</div>

---

## What is MysticAgent?

MysticAgent is a self-hosted AI agent that automates your life — email, calendar, errands, monitoring — while you stay in full control. It runs entirely on **your** machine: your data and keys never leave your hardware. No cloud, no telemetry, no accounts.

It is a **product, not a framework**: install with one command, then manage everything from a clean web dashboard.

### The four pillars

1. **Product, not framework** — one-command install, configured through a web dashboard, not YAML files.
2. **Control & trust** — every capability has a permission slider: `Off` / `Propose` / `Act & report` / `Act silently`. Proposed actions land in a decision inbox awaiting your approval. Every action is written to a full audit log.
3. **Proactivity** — the agent lives on an event stream (new email, cron tick, price drop). It notices and reacts on its own instead of waiting for commands.
4. **Tool forge** — when the agent lacks a capability, it writes a new tool (real code), tests it in a sandbox, asks for your approval, and registers it. Skills are executable, tested code — not LLM notes.

### What it will do for you (once you grant permission)

- Triage your inbox, answer routine email, escalate what matters
- Manage your calendar and negotiate meeting times with people
- Watch prices, document deadlines, servers, repos — and speak up when action is needed
- Handle errands: bookings, complaints, subscriptions, package tracking
- Research topics and deliver syntheses
- Make phone calls on your behalf (openly, as your assistant)
- Build itself new tools when it hits a wall

### Channels

Telegram bot (primary) + local web dashboard. Planned: telephony (Twilio), Home Assistant.

## Installation

> Coming soon:
>
> ```sh
> curl -fsSL https://raw.githubusercontent.com/terlikk/mystic-agent/main/install.sh | sh
> ```

## Architecture

```
mystic-agent/
├── site/       # project landing page (Next.js)
├── core/       # the agent: FastAPI service + event engine (Python)
├── dashboard/  # local web UI served by core
└── install.sh  # one-command installer
```

Credentials (OAuth tokens, API keys, bot tokens) live in a local encrypted vault (SQLite). Agent-written code always runs in a sandbox with no vault access.

## Roadmap

- [x] Landing page — [mystic-agent.vercel.app](https://mystic-agent.vercel.app)
- [x] Core: event bus, agent loop, permission system, vault, audit log, Telegram gateway
- [ ] Web dashboard: activity stream, decision inbox, skill cards, connections
- [ ] Tool forge MVP
- [ ] Telephony, Home Assistant

## Po polsku

MysticAgent to self-hosted agent AI — „otwarty Jarvis". Działa w całości na Twoim sprzęcie: żadnej chmury, telemetrii ani kont. Każda zdolność agenta ma suwak uprawnień (Wyłączone / Proponuje / Robi i raportuje / Robi cicho), akcje do zatwierdzenia trafiają do skrzynki decyzji, a wszystko ląduje w audycie. Agent żyje na strumieniu zdarzeń i sam się odzywa, gdy trzeba działać, a gdy czegoś nie umie — pisze sobie nowe narzędzie i pyta Cię o zgodę. Projekt jest we wczesnej fazie budowy 🚧.

## License

[MIT](LICENSE)
