/**
 * Single source of truth for the project identity.
 * Renaming the project = editing this file only.
 */
export const PROJECT = {
  name: "MysticAgent",
  cli: "mystic-agent",
  version: "v0.1.0-dev",
  repoUrl: "https://github.com/terlikk/mystic-agent",
  repoSlug: "terlikk/mystic-agent",
  installCmd:
    "curl -fsSL https://raw.githubusercontent.com/terlikk/mystic-agent/main/install.sh | sh",
  tagline: "Twój Jarvis. Twój serwer. Twoje zasady.",
  description:
    "Open-source'owy agent AI, który mieszka na Twoim komputerze — ogarnia maile, kalendarz i codzienne sprawy, a o każdą ważną decyzję pyta Ciebie.",
} as const;

/** Pixel banner rendered in the hero terminal (and the CLI splash). */
export const ASCII_BANNER = [
  "███    ███ ██    ██ ███████ ████████ ██  ██████",
  "████  ████  ██  ██  ██         ██    ██ ██",
  "██ ████ ██   ████   ███████    ██    ██ ██",
  "██  ██  ██    ██         ██    ██    ██ ██",
  "██      ██    ██    ███████    ██    ██  ██████",
  "   █████   ██████  ███████ ███    ██ ████████",
  "  ██   ██ ██       ██      ████   ██    ██",
  "  ███████ ██   ███ █████   ██ ██  ██    ██",
  "  ██   ██ ██    ██ ██      ██  ██ ██    ██",
  "  ██   ██  ██████  ███████ ██   ████    ██",
] as const;
