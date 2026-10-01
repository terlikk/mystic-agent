<div align="center">

# Mystic Agent

**A personal AI assistant you host yourself.**

Proactive tools, configurable permissions and a local dashboard.

[Project website](https://mystic-agent.vercel.app) · [Getting started](#getting-started) · [Data flow](#where-your-data-goes) · [Security notes](SECURITY.md)

`Python 3.11+` · `FastAPI` · `Telegram` · `MIT`

</div>

---

## Overview

Mystic Agent runs its Python service, dashboard and local storage on your machine. It connects an AI model to tools for everyday tasks, with per-capability permissions and a decision inbox.

**Early access:** the package currently declares version `0.3.0`. Interfaces, integrations and data formats are still evolving. Self-hosted describes the application runtime and storage; model calls and connected services can use external providers.

## Capabilities in the repository

| Area | Implementation and requirements |
| :--- | :--- |
| Conversation | Telegram gateway and a local web dashboard |
| Models | Anthropic and OpenAI API adapters; provider credentials and network access required |
| Everyday tools | Notes, contacts, tasks, reminders, local calendar entries, file/PDF reading and web tools |
| Email | Email tools requiring mailbox configuration |
| Browser | Optional Playwright integration; browser dependencies required |
| Packages | InPost tracking integration; some other carriers return tracking links |
| Voice & images | Optional local transcription, an OpenAI transcription fallback, and provider-based image descriptions |
| Automation | Event-driven processing and scheduled work |
| Tool forge | Generates skill files, runs subprocess checks and requests approval before registration |
| Telephony | Twilio ConversationRelay integration is present; needs Twilio credentials, a number and a configured public relay |

A tool being present in the code does not mean every workflow has been verified against a live service. Google OAuth for Gmail/Calendar and Home Assistant remain planned integrations. The built-in calendar stores local entries; it is not Google Calendar synchronization.

## Permission model

Each capability can be configured independently:

| Level | Behavior |
| :--- | :--- |
| `off` | Tool use disabled |
| `propose` | Action waits in the decision inbox |
| `act_report` | Action runs and is reported afterward |
| `act_silent` | Action runs with details recorded in the audit log |

Defaults vary by capability. For example, email sending, shell and phone calls default to proposals, while some local and read-only tools run automatically. **Not every action requires approval**; review the levels you enable.

## Getting started

The supplied installer targets **macOS/Linux** and requires Python 3.11+, Git, `curl` and Python virtual-environment support. You also need credentials for the selected model provider. Telegram and other integrations need their own configuration.

Download and inspect the installer, then run it:

```sh
curl -fLo install.sh https://raw.githubusercontent.com/terlikk/mystic-agent/main/install.sh
# Read install.sh before running it.
sh install.sh
mystic-agent start
```

The installer creates a virtual environment under `~/.mystic-agent/venv` and links the CLI into `~/.local/bin`. Ensure that directory is on your `PATH`, or use `~/.local/bin/mystic-agent start`.

On first start, the CLI runs a configuration wizard. The default dashboard address is **http://127.0.0.1:7700**. Use `mystic-agent setup` to revisit configuration.

Optional dependencies are declared in [`core/pyproject.toml`](core/pyproject.toml): `browser` adds Playwright and `voice` adds faster-whisper. Install extras into the same virtual environment as the application; browser automation also needs Playwright browser binaries.

## Where your data goes

- **Local:** application state, the dashboard and the encrypted credential vault are stored on your machine.
- **Model providers:** prompts, relevant context, tool results and submitted images can be sent to the configured Anthropic or OpenAI API.
- **Connected services:** Telegram, email, web requests, tracking and Twilio communicate with their respective services. Their credentials are used for those connections.
- **Voice:** faster-whisper can transcribe locally when installed; the fallback sends audio to OpenAI when an OpenAI key is available. Local model assets may need downloading.

This is not a fully offline assistant, and local storage is not a promise that all data stays on the device. External providers may require accounts and incur usage charges.

## Runtime boundaries

The skill runner uses a separate Python process, a temporary working directory, a minimal environment, a timeout and resource limits where available. It does **not** establish a container, filesystem jail or network isolation. A separate process running as the same user is not a hard barrier against access to that user’s files. Review generated skills before approving them.

Keep the local dashboard bound to loopback unless you have deliberately configured appropriate access controls. Telephony uses a separate relay; configuring it is a separate step from starting the dashboard. See [`SECURITY.md`](SECURITY.md) for the project’s security design and reporting guidance.

## Repository map

| Path | Purpose |
| :--- | :--- |
| `core/mystic_agent/` | Python service, providers, tools and event processing |
| `core/mystic_agent/dashboard/` | Local dashboard served by the application |
| `core/tests/` | Core tests |
| `site/` | Next.js project website |
| `install.sh` | Virtual-environment installer and CLI setup |

## Po polsku

Mystic Agent to asystent AI uruchamiany na własnym komputerze. Ma lokalny panel, narzędzia i konfigurowalne uprawnienia. Korzysta jednak z zewnętrznych modeli oraz wybranych integracji — część danych opuszcza urządzenie. To projekt we wczesnej fazie rozwoju; telefonia jest już obecna w kodzie, ale wymaga osobnej konfiguracji.

## License

[MIT](LICENSE).
