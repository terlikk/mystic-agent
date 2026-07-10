import { Reveal } from "@/components/site/reveal";
import { PROJECT } from "@/config/site";

/* ── capabilities ───────────────────────────────────────────────── */

const CAPABILITIES = [
  {
    tag: "MAIL",
    text: "Segreguje skrzynkę, odpisuje na rutynowe, eskaluje ważne.",
  },
  {
    tag: "KALENDARZ",
    text: "Umawia terminy i negocjuje godziny z ludźmi w Twoim imieniu.",
  },
  {
    tag: "CZUJKI",
    text: "Pilnuje cen, terminów dokumentów, serwerów i repo — odzywa się, gdy trzeba działać.",
  },
  {
    tag: "SPRAWY",
    text: "Rezerwacje, reklamacje, subskrypcje, śledzenie paczek — załatwione.",
  },
  {
    tag: "RESEARCH",
    text: "Grzebie w źródłach i przynosi gotową syntezę zamiast 40 zakładek.",
  },
  {
    tag: "TELEFON",
    text: "Dzwoni w Twoim imieniu — zawsze jawnie, jako Twój asystent. (wkrótce)",
  },
] as const;

export function Capabilities() {
  return (
    <section id="mozliwosci" className="hairline-top scroll-mt-14">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6 sm:py-28">
        <Reveal>
          <p className="font-mono text-xs tracking-wide text-cyan">
            {"// po nadaniu uprawnień"}
          </p>
          <h2 className="mt-3 max-w-2xl font-heading text-3xl font-bold tracking-tight text-balance sm:text-4xl">
            Co odda Ci z głowy
          </h2>
        </Reveal>

        <div className="mt-10 grid gap-x-10 gap-y-6 sm:grid-cols-2">
          {CAPABILITIES.map((c, i) => (
            <Reveal key={c.tag} delay={i * 60}>
              <div className="flex items-baseline gap-4 border-b border-line/60 pb-5">
                <span className="w-24 shrink-0 font-mono text-[11px] tracking-[0.15em] text-cyan">
                  {c.tag}
                </span>
                <p className="text-sm leading-relaxed text-foreground/85">
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
  "ZDARZENIE",
  "KOLEJKA",
  "AGENT",
  "UPRAWNIENIA",
  "WYKONANIE",
  "AUDYT",
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
    <section id="jak-dziala" className="hairline-top scroll-mt-14">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6 sm:py-28">
        <Reveal>
          <p className="font-mono text-xs tracking-wide text-cyan">
            {"// architektura"}
          </p>
          <h2 className="mt-3 max-w-2xl font-heading text-3xl font-bold tracking-tight text-balance sm:text-4xl">
            Od zdarzenia do audytu
          </h2>
        </Reveal>

        <Reveal delay={100} className="mt-10">
          <div className="overflow-x-auto rounded-lg border border-line bg-panel px-6 py-8">
            <div className="flex min-w-max items-center gap-3 font-mono text-xs sm:gap-4">
              {FLOW.map((step, i) => (
                <div key={step} className="flex items-center gap-3 sm:gap-4">
                  <span
                    className={`rounded-sm border px-3 py-2 tracking-wider ${
                      step === "UPRAWNIENIA"
                        ? "border-amber/50 text-amber"
                        : "border-cyan/30 text-cyan"
                    }`}
                  >
                    {step}
                  </span>
                  {i < FLOW.length - 1 && (
                    <span className="text-dim" aria-hidden="true">
                      →
                    </span>
                  )}
                </div>
              ))}
            </div>
            <p className="mt-4 min-w-max font-mono text-[11px] text-dim">
              {"                                          "}
              └─ poziom „proponuje” → skrzynka decyzji → Twoja zgoda
            </p>
          </div>
        </Reveal>

        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          {TRUST.map((t, i) => (
            <Reveal key={t.title} delay={i * 90}>
              <div className="h-full rounded-lg border border-line bg-panel p-5">
                <h3 className="font-mono text-sm font-medium text-foreground">
                  <span className="mr-2 text-cyan" aria-hidden="true">
                    ▪
                  </span>
                  {t.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-dim">{t.text}</p>
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
    <section className="hairline-top">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6 sm:py-28">
        <div className="grid items-start gap-12 lg:grid-cols-2">
          <Reveal>
            <p className="font-mono text-xs tracking-wide text-cyan">
              {"// status"}
            </p>
            <h2 className="mt-3 font-heading text-3xl font-bold tracking-tight text-balance sm:text-4xl">
              Buduje się publicznie
            </h2>
            <p className="mt-5 max-w-md text-base leading-relaxed text-dim">
              Cały kod od pierwszego commita jest otwarty. Zajrzyj, zostaw
              gwiazdkę, obserwuj postępy — a niedługo uruchom u siebie.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <a
                href={PROJECT.repoUrl}
                target="_blank"
                rel="noreferrer"
                className="rounded-md bg-cyan px-5 py-3 font-mono text-sm font-medium text-[#06222a] shadow-[0_0_24px_rgba(34,211,238,0.35)] transition-transform hover:scale-[1.03] active:scale-[0.98]"
              >
                ★ {PROJECT.repoSlug}
              </a>
            </div>
          </Reveal>

          <Reveal delay={120}>
            <div className="rounded-lg border border-line bg-panel font-mono text-xs">
              <div className="border-b border-line px-5 py-3 text-dim">
                roadmap.txt
              </div>
              <ul className="space-y-3 px-5 py-5">
                {ROADMAP.map((r) => (
                  <li key={r.stage} className="flex items-center gap-4">
                    <span className="text-dim">{r.stage}</span>
                    <span className="flex-1 text-foreground/85">{r.name}</span>
                    <span
                      className={
                        r.status === "W TOKU"
                          ? "pulse-amber text-amber"
                          : r.status === "DALEJ"
                            ? "text-cyan"
                            : "text-dim"
                      }
                    >
                      [{r.status}]
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

/* ── footer ─────────────────────────────────────────────────────── */

export function Footer() {
  return (
    <footer className="hairline-top">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-10 font-mono text-xs text-dim sm:px-6">
        <p>
          <span className="text-cyan" aria-hidden="true">
            ▚{" "}
          </span>
          {PROJECT.name} · MIT · self-hosted z założenia
        </p>
        <a
          href={PROJECT.repoUrl}
          target="_blank"
          rel="noreferrer"
          className="transition-colors hover:text-cyan"
        >
          github.com/{PROJECT.repoSlug} ↗
        </a>
      </div>
    </footer>
  );
}
