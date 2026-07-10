import {
  Bell,
  Calendar,
  Mail,
  Package,
  Phone,
  Search,
  type LucideIcon,
} from "lucide-react";
import { PROJECT } from "@/config/site";

/* ── capabilities panel ─────────────────────────────────────────── */

const CAPABILITIES: { icon: LucideIcon; title: string; text: string }[] = [
  {
    icon: Mail,
    title: "Poczta",
    text: "Segreguje skrzynkę, odpisuje na rutynowe, eskaluje ważne.",
  },
  {
    icon: Calendar,
    title: "Kalendarz",
    text: "Umawia terminy i negocjuje godziny z ludźmi w Twoim imieniu.",
  },
  {
    icon: Bell,
    title: "Czujki",
    text: "Pilnuje cen, terminów, serwerów i repo — odzywa się, gdy trzeba działać.",
  },
  {
    icon: Package,
    title: "Sprawy",
    text: "Rezerwacje, reklamacje, subskrypcje, śledzenie paczek — załatwione.",
  },
  {
    icon: Search,
    title: "Research",
    text: "Grzebie w źródłach i przynosi gotową syntezę zamiast 40 zakładek.",
  },
  {
    icon: Phone,
    title: "Telefon",
    text: "Dzwoni w Twoim imieniu — zawsze jawnie, jako Twój asystent. Wkrótce.",
  },
];

export function CapabilitiesPanel() {
  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {CAPABILITIES.map((c) => (
        <div key={c.title} className="rounded-2xl bg-fill p-6">
          <c.icon className="size-6 text-blue" strokeWidth={1.8} />
          <h3 className="mt-4 text-base font-semibold text-ink">{c.title}</h3>
          <p className="mt-1.5 text-sm leading-relaxed text-ink-2">{c.text}</p>
        </div>
      ))}
    </div>
  );
}

/* ── how it works panel ─────────────────────────────────────────── */

const FLOW = [
  "Zdarzenie",
  "Kolejka",
  "Agent",
  "Uprawnienia",
  "Wykonanie",
  "Audyt",
] as const;

const TRUST = [
  {
    title: "Szyfrowany sejf",
    text: "Tokeny OAuth i klucze API leżą w lokalnym, szyfrowanym SQLite. Nigdy nie wychodzą z Twojego sprzętu.",
  },
  {
    title: "Sandbox od pierwszego dnia",
    text: "Kod, który agent pisze sam, odpala się w izolacji — z limitami i bez dostępu do sejfu.",
  },
  {
    title: "Pełny audyt",
    text: "Każde działanie: timestamp, wejście, wyjście i powód. Zawsze wiesz, co i dlaczego zrobił.",
  },
] as const;

export function HowItWorksPanel() {
  return (
    <div>
      <div className="overflow-x-auto rounded-3xl bg-fill px-6 py-8">
        <div className="flex min-w-max items-center justify-center gap-2.5 text-sm font-medium sm:gap-3">
          {FLOW.map((step, i) => (
            <div key={step} className="flex items-center gap-2.5 sm:gap-3">
              <span
                className={`rounded-full px-4 py-2 ${
                  step === "Uprawnienia"
                    ? "bg-violet text-white"
                    : "bg-white text-ink shadow-sm"
                }`}
              >
                {step}
              </span>
              {i < FLOW.length - 1 && (
                <span className="text-hairline" aria-hidden="true">
                  →
                </span>
              )}
            </div>
          ))}
        </div>
        <p className="mt-5 text-center text-xs text-ink-2">
          Poziom „proponuje" kieruje akcję do skrzynki decyzji — wykonanie
          rusza dopiero po Twojej zgodzie.
        </p>
      </div>

      <div className="mt-5 grid gap-5 sm:grid-cols-3">
        {TRUST.map((t) => (
          <div key={t.title} className="rounded-2xl bg-fill p-6">
            <h3 className="text-base font-semibold text-ink">{t.title}</h3>
            <p className="mt-1.5 text-sm leading-relaxed text-ink-2">
              {t.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── roadmap panel ──────────────────────────────────────────────── */

const ROADMAP = [
  { stage: "01", name: "Landing page + wizja", status: "W TOKU" },
  { stage: "02", name: "Rdzeń: zdarzenia, uprawnienia, sejf, telegram", status: "DALEJ" },
  { stage: "03", name: "Web dashboard", status: "PLAN" },
  { stage: "04", name: "Kuźnia narzędzi", status: "PLAN" },
  { stage: "05", name: "Telefonia · Home Assistant", status: "PLAN" },
] as const;

export function RoadmapPanel() {
  return (
    <div className="grid items-center gap-10 lg:grid-cols-2">
      <div>
        <h3 className="text-2xl font-semibold tracking-tight text-balance sm:text-3xl">
          Buduje się publicznie.
        </h3>
        <p className="mt-4 max-w-md text-base leading-relaxed text-ink-2">
          Cały kod od pierwszego commita jest otwarty. Zajrzyj, zostaw
          gwiazdkę, obserwuj postępy — a niedługo uruchom u siebie.
        </p>
        <div className="mt-7">
          <a
            href={PROJECT.repoUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-block rounded-full bg-blue px-6 py-3 text-sm font-medium text-white transition-all hover:bg-blue-soft hover:shadow-[0_8px_24px_-8px_rgba(29,78,216,0.5)] active:scale-[0.98]"
          >
            ★ {PROJECT.repoSlug}
          </a>
        </div>
      </div>

      <ul className="space-y-2.5">
        {ROADMAP.map((r) => (
          <li
            key={r.stage}
            className="flex items-center gap-4 rounded-2xl bg-fill px-5 py-4 text-sm"
          >
            <span className="font-mono text-xs text-ink-2">{r.stage}</span>
            <span className="flex-1 font-medium text-ink">{r.name}</span>
            <span
              className={`rounded-full px-3 py-1 text-[10px] font-semibold tracking-wider ${
                r.status === "W TOKU"
                  ? "bg-violet/10 text-violet"
                  : r.status === "DALEJ"
                    ? "bg-blue/10 text-blue"
                    : "bg-fill-2 text-ink-2"
              }`}
            >
              {r.status}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* ── footer ─────────────────────────────────────────────────────── */

export function Footer() {
  return (
    <footer className="border-t border-hairline/60">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-8 text-xs text-ink-2 sm:px-6">
        <p>
          {PROJECT.name} · MIT · self-hosted z założenia
        </p>
        <a
          href={PROJECT.repoUrl}
          target="_blank"
          rel="noreferrer"
          className="transition-colors hover:text-ink"
        >
          github.com/{PROJECT.repoSlug}
        </a>
      </div>
    </footer>
  );
}
