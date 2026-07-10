"use client";

import { useEffect, useRef, useState } from "react";
import { animate } from "animejs";
import { BentoCard, BentoGrid } from "@/components/ui/bento-grid";
import { CommandLine } from "@/components/site/terminal";
import { Reveal } from "@/components/site/reveal";
import { PROJECT } from "@/config/site";

/* ── permission slider demo ─────────────────────────────────────── */

const LEVELS = [
  {
    key: "off",
    label: "Wyłączone",
    message: "agent śpi — nie zrobi nic bez Twojej zgody",
    tone: "text-dim",
    prefix: "·",
  },
  {
    key: "propose",
    label: "Proponuje",
    message: "mail od klienta → proponuję odpowiedź  [Zatwierdź] [Odrzuć]",
    tone: "text-amber",
    prefix: "?",
  },
  {
    key: "act_report",
    label: "Robi i raportuje",
    message: "odpisałem na 3 rutynowe maile — raport w audycie",
    tone: "text-ok",
    prefix: "✓",
  },
  {
    key: "act_silent",
    label: "Robi cicho",
    message: "zrobione. szczegóły zawsze w audycie.",
    tone: "text-ok",
    prefix: "✓",
  },
] as const;

function PermissionSliderDemo() {
  const [level, setLevel] = useState(1);
  const msgRef = useRef<HTMLParagraphElement>(null);

  const select = (i: number) => {
    setLevel(i);
    if (
      msgRef.current &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      animate(msgRef.current, {
        opacity: [0, 1],
        translateY: [6, 0],
        duration: 350,
        ease: "outQuad",
      });
    }
  };

  const current = LEVELS[level];

  return (
    <div className="flex h-full flex-col justify-center gap-4 px-5 pt-5">
      <div
        role="radiogroup"
        aria-label="Poziom uprawnień umiejętności"
        className="relative flex items-center justify-between"
      >
        {/* track */}
        <span
          className="absolute inset-x-2 top-1/2 h-px -translate-y-1/2 bg-line"
          aria-hidden="true"
        />
        <span
          className="absolute left-2 top-1/2 h-px -translate-y-1/2 bg-cyan transition-all duration-300"
          style={{ width: `calc(${(level / (LEVELS.length - 1)) * 100}% - 1rem)` }}
          aria-hidden="true"
        />
        {LEVELS.map((l, i) => (
          <button
            key={l.key}
            role="radio"
            aria-checked={level === i}
            aria-label={l.label}
            onClick={() => select(i)}
            className="relative z-10 flex flex-col items-center gap-2 px-1 py-2"
          >
            <span
              className={`size-3.5 rounded-full border-2 transition-all duration-300 ${
                level === i
                  ? "border-cyan bg-cyan shadow-[0_0_12px_rgba(34,211,238,0.6)]"
                  : i < level
                    ? "border-cyan/60 bg-panel"
                    : "border-line bg-panel"
              }`}
            />
            <span
              className={`font-mono text-[9px] tracking-wide uppercase transition-colors sm:text-[10px] ${
                level === i ? "text-cyan" : "text-dim"
              }`}
            >
              {l.label}
            </span>
          </button>
        ))}
      </div>

      <div className="rounded-md border border-line bg-background/60 px-4 py-3 font-mono text-xs">
        <p ref={msgRef} className={current.tone}>
          <span className="mr-2">{current.prefix}</span>
          {current.message}
        </p>
      </div>
    </div>
  );
}

/* ── proactive event feed ───────────────────────────────────────── */

const EVENTS = [
  { t: "08:12", text: "nowy mail od księgowej → wygląda pilnie, eskaluję", tone: "text-amber" },
  { t: "11:40", text: "cena monitorowanej karty spadła 12% → alert", tone: "text-cyan" },
  { t: "14:05", text: "deploy na serwerze padł → restart + raport", tone: "text-ok" },
  { t: "18:00", text: "cron: raport dnia → wysłany na telegrama", tone: "text-ok" },
  { t: "02:31", text: "certyfikat TLS wygasa za 7 dni → proponuję odnowienie", tone: "text-amber" },
] as const;

function EventFeed() {
  const [visible, setVisible] = useState(3);
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setVisible(EVENTS.length);
      return;
    }
    const id = setInterval(() => {
      setVisible((v) => (v >= EVENTS.length ? 3 : v + 1));
    }, 2600);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const last = listRef.current?.lastElementChild as HTMLElement | null;
    if (!last) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    animate(last, {
      opacity: [0, 1],
      translateY: [8, 0],
      duration: 400,
      ease: "outQuad",
    });
  }, [visible]);

  return (
    <ul
      ref={listRef}
      className="flex h-full flex-col justify-end gap-2 px-5 pt-5 font-mono text-[11px] leading-relaxed"
    >
      {EVENTS.slice(0, visible).map((e) => (
        <li key={e.t} className="flex gap-3">
          <span className="shrink-0 text-dim">{e.t}</span>
          <span className={e.tone}>{e.text}</span>
        </li>
      ))}
    </ul>
  );
}

/* ── tool forge pipeline ────────────────────────────────────────── */

const FORGE_STEPS = [
  { n: "01", text: "pisze kod nowego narzędzia", state: "done" },
  { n: "02", text: "testuje w sandboxie — bez dostępu do sejfu", state: "done" },
  { n: "03", text: "pyta Cię o zgodę (telegram / dashboard)", state: "active" },
  { n: "04", text: "rejestruje skill na stałe", state: "todo" },
] as const;

function ForgePipeline() {
  return (
    <ol className="flex h-full flex-col justify-center gap-2.5 px-5 pt-5 font-mono text-[11px]">
      {FORGE_STEPS.map((s) => (
        <li key={s.n} className="flex items-center gap-3">
          <span
            className={
              s.state === "done"
                ? "text-ok"
                : s.state === "active"
                  ? "pulse-amber text-amber"
                  : "text-dim"
            }
          >
            {s.state === "done" ? "✓" : s.state === "active" ? "▸" : "○"}
          </span>
          <span className="text-dim">{s.n}</span>
          <span
            className={
              s.state === "todo" ? "text-dim" : "text-foreground/85"
            }
          >
            {s.text}
          </span>
        </li>
      ))}
    </ol>
  );
}

/* ── install demo ───────────────────────────────────────────────── */

function InstallDemo() {
  return (
    <div className="flex h-full flex-col justify-center gap-3 px-5 pt-5">
      <CommandLine command={PROJECT.installCmd} />
      <p className="font-mono text-[11px] text-dim">
        …a potem wszystko klikasz w dashboardzie. zero YAML-a.
      </p>
    </div>
  );
}

/* ── section ────────────────────────────────────────────────────── */

export function Pillars() {
  return (
    <section id="filary" className="hairline-top scroll-mt-14">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6 sm:py-28">
        <Reveal>
          <p className="font-mono text-xs tracking-wide text-cyan">
            {"// czym się różni"}
          </p>
          <h2 className="mt-3 max-w-2xl font-heading text-3xl font-bold tracking-tight text-balance sm:text-4xl">
            Autonomia bez utraty kontroli
          </h2>
        </Reveal>

        <Reveal delay={120} className="mt-10">
          <BentoGrid className="lg:grid-cols-3">
            <BentoCard
              name="Suwak uprawnień na każdej umiejętności"
              className="lg:col-span-2"
              eyebrow="kontrola i zaufanie"
              description="Od pełnej ciszy po pełną autonomię — Ty decydujesz, ile agent może. Propozycje czekają w skrzynce decyzji, a każde działanie ląduje w audycie. Przesuń sam:"
              background={<PermissionSliderDemo />}
            />
            <BentoCard
              name="Produkt, nie framework"
              className="lg:col-span-1"
              eyebrow="instalacja"
              description="Jedna komenda w terminalu, reszta w ładnym web dashboardzie. Bez plików konfiguracyjnych."
              background={<InstallDemo />}
            />
            <BentoCard
              name="Sam zauważa, sam się odzywa"
              className="lg:col-span-1"
              eyebrow="proaktywność"
              description="Agent żyje na strumieniu zdarzeń — mail, cron, spadek ceny — i reaguje, zanim zdążysz zapytać."
              background={<EventFeed />}
            />
            <BentoCard
              name="Kuźnia narzędzi"
              className="lg:col-span-2"
              eyebrow="samorozbudowa"
              description="Gdy czegoś nie umie, pisze sobie nowe narzędzie: kod, test w sandboxie, Twoja zgoda, rejestracja. Skille to wykonywalny, przetestowany kod — nie notatki."
              background={<ForgePipeline />}
            />
          </BentoGrid>
        </Reveal>
      </div>
    </section>
  );
}
