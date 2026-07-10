import {
  Bell,
  Calendar,
  Mail,
  Package,
  Phone,
  Search,
  type LucideIcon,
} from "lucide-react";
import { Reveal } from "@/components/site/reveal";
import { PROJECT } from "@/config/site";

/* ── capabilities ───────────────────────────────────────────────── */

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

export function Capabilities() {
  return (
    <section id="mozliwosci" className="scroll-mt-14 bg-fill">
      <div className="mx-auto max-w-5xl px-4 py-20 sm:px-6 sm:py-28">
        <Reveal className="text-center">
          <h2 className="text-3xl font-semibold tracking-tight text-balance sm:text-5xl">
            Co odda Ci z głowy.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-base text-ink-2 sm:text-lg">
            Po nadaniu uprawnień agent przejmuje codzienność — kawałek po
            kawałku.
          </p>
        </Reveal>

        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {CAPABILITIES.map((c, i) => (
            <Reveal key={c.title} delay={i * 60}>
              <div className="h-full rounded-2xl bg-white p-6 shadow-sm">
                <c.icon className="size-6 text-blue" strokeWidth={1.8} />
                <h3 className="mt-4 text-base font-semibold text-ink">
                  {c.title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-ink-2">
                  {c.text}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── how it works ───────────────────────────────────────────────── */

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

export function HowItWorks() {
  return (
    <section id="jak-dziala" className="scroll-mt-14">
      <div className="mx-auto max-w-5xl px-4 py-20 sm:px-6 sm:py-28">
        <Reveal className="text-center">
          <h2 className="text-3xl font-semibold tracking-tight text-balance sm:text-5xl">
            Od zdarzenia do audytu.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-base text-ink-2 sm:text-lg">
            Każde działanie agenta przechodzi przez tę samą, przewidywalną
            ścieżkę.
          </p>
        </Reveal>

        <Reveal delay={100} className="mt-12">
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
        </Reveal>

        <div className="mt-5 grid gap-5 sm:grid-cols-3">
          {TRUST.map((t, i) => (
            <Reveal key={t.title} delay={i * 90}>
              <div className="h-full rounded-2xl bg-fill p-6">
                <h3 className="text-base font-semibold text-ink">{t.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-ink-2">
                  {t.text}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ── roadmap + CTA ──────────────────────────────────────────────── */

const ROADMAP = [
  { stage: "01", name: "Landing page + wizja", status: "W TOKU" },
  { stage: "02", name: "Rdzeń: zdarzenia, uprawnienia, sejf, telegram", status: "DALEJ" },
  { stage: "03", name: "Web dashboard", status: "PLAN" },
  { stage: "04", name: "Kuźnia narzędzi", status: "PLAN" },
  { stage: "05", name: "Telefonia · Home Assistant", status: "PLAN" },
] as const;

export function Roadmap() {
  return (
    <section className="bg-fill">
      <div className="mx-auto max-w-5xl px-4 py-20 sm:px-6 sm:py-28">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <Reveal>
            <h2 className="text-3xl font-semibold tracking-tight text-balance sm:text-5xl">
              Buduje się publicznie.
            </h2>
            <p className="mt-5 max-w-md text-base leading-relaxed text-ink-2 sm:text-lg">
              Cały kod od pierwszego commita jest otwarty. Zajrzyj, zostaw
              gwiazdkę, obserwuj postępy — a niedługo uruchom u siebie.
            </p>
            <div className="mt-8">
              <a
                href={PROJECT.repoUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-block rounded-full bg-blue px-6 py-3 text-sm font-medium text-white transition-all hover:bg-blue-soft hover:shadow-[0_8px_24px_-8px_rgba(29,78,216,0.5)] active:scale-[0.98]"
              >
                ★ {PROJECT.repoSlug}
              </a>
            </div>
          </Reveal>

          <Reveal delay={120}>
            <ul className="space-y-2.5">
              {ROADMAP.map((r) => (
                <li
                  key={r.stage}
                  className="flex items-center gap-4 rounded-2xl bg-white px-5 py-4 text-sm shadow-sm"
                >
                  <span className="font-mono text-xs text-ink-2">
                    {r.stage}
                  </span>
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
          </Reveal>
        </div>
      </div>
    </section>
  );
}

/* ── footer ─────────────────────────────────────────────────────── */

export function Footer() {
  return (
    <footer className="border-t border-hairline/60">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 py-10 text-xs text-ink-2 sm:px-6">
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
