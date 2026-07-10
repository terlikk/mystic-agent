"use client";

import { useEffect, useRef, useState } from "react";
import { animate } from "animejs";
import { BentoCard, BentoGrid } from "@/components/ui/bento-grid";
import { CommandLine } from "@/components/site/terminal";
import { Reveal } from "@/components/site/reveal";
import { PROJECT } from "@/config/site";

/* ── permission control demo (iOS segmented control style) ─────── */

const LEVELS = [
  {
    key: "off",
    label: "Wyłączone",
    message: "Agent śpi — nie zrobi nic bez Twojej zgody.",
    dot: "bg-hairline",
  },
  {
    key: "propose",
    label: "Proponuje",
    message: "Mail od klienta: proponuję odpowiedź — Zatwierdź / Odrzuć.",
    dot: "bg-violet",
  },
  {
    key: "act_report",
    label: "Robi + raport",
    message: "Odpisałem na 3 rutynowe maile. Raport czeka w audycie.",
    dot: "bg-blue",
  },
  {
    key: "act_silent",
    label: "Robi cicho",
    message: "Zrobione. Szczegóły zawsze znajdziesz w audycie.",
    dot: "bg-blue",
  },
] as const;

function PermissionControlDemo() {
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
    <div className="flex h-full flex-col justify-center gap-4 px-6 pt-6 sm:px-7">
      <div
        role="radiogroup"
        aria-label="Poziom uprawnień umiejętności"
        className="flex rounded-full bg-fill-2 p-1"
      >
        {LEVELS.map((l, i) => (
          <button
            key={l.key}
            role="radio"
            aria-checked={level === i}
            onClick={() => select(i)}
            className={`flex-1 rounded-full px-1 py-2 text-[11px] font-medium transition-all duration-300 sm:text-xs ${
              level === i
                ? "bg-white text-ink shadow-sm"
                : "text-ink-2 hover:text-ink"
            }`}
          >
            {l.label}
          </button>
        ))}
      </div>

      <div className="rounded-2xl bg-white px-5 py-4 shadow-sm">
        <p ref={msgRef} className="flex items-center gap-3 text-sm text-ink">
          <span className={`size-2 shrink-0 rounded-full ${current.dot}`} />
          {current.message}
        </p>
      </div>
    </div>
  );
}

/* ── proactive event feed ───────────────────────────────────────── */

const EVENTS = [
  { t: "08:12", text: "Pilny mail od księgowej — eskaluję do Ciebie", dot: "bg-violet" },
  { t: "11:40", text: "Cena monitorowanej karty spadła 12% — alert", dot: "bg-blue" },
  { t: "14:05", text: "Serwer nie odpowiadał — restart i raport", dot: "bg-blue" },
  { t: "18:00", text: "Raport dnia wysłany na telegrama", dot: "bg-blue" },
  { t: "02:31", text: "Certyfikat TLS wygasa za 7 dni — proponuję odnowienie", dot: "bg-violet" },
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
    <div className="relative h-full overflow-hidden">
      <div
        className="pointer-events-none absolute inset-x-0 top-0 z-10 h-10 bg-gradient-to-b from-fill to-transparent"
        aria-hidden="true"
      />
      <ul
        ref={listRef}
        className="flex h-full flex-col justify-end gap-2 px-6 pt-6 sm:px-7"
      >
        {EVENTS.slice(0, visible).map((e) => (
        <li
          key={e.t}
          className="flex items-center gap-3 rounded-xl bg-white px-4 py-2.5 text-xs text-ink shadow-sm"
        >
          <span className={`size-1.5 shrink-0 rounded-full ${e.dot}`} />
          <span className="flex-1">{e.text}</span>
          <span className="shrink-0 text-[10px] text-ink-2">{e.t}</span>
        </li>
        ))}
      </ul>
    </div>
  );
}

/* ── tool forge pipeline ────────────────────────────────────────── */

const FORGE_STEPS = [
  { n: 1, text: "Pisze kod nowego narzędzia", state: "done" },
  { n: 2, text: "Testuje w sandboxie — bez dostępu do sejfu", state: "done" },
  { n: 3, text: "Pyta Cię o zgodę", state: "active" },
  { n: 4, text: "Rejestruje skill na stałe", state: "todo" },
] as const;

function ForgePipeline() {
  return (
    <ol className="flex h-full flex-col justify-center gap-3 px-6 pt-6 sm:px-7">
      {FORGE_STEPS.map((s) => (
        <li key={s.n} className="flex items-center gap-3 text-sm">
          <span
            className={`flex size-6 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold ${
              s.state === "done"
                ? "bg-blue text-white"
                : s.state === "active"
                  ? "pulse-soft bg-violet text-white"
                  : "bg-fill-2 text-ink-2"
            }`}
          >
            {s.state === "done" ? "✓" : s.n}
          </span>
          <span className={s.state === "todo" ? "text-ink-2" : "text-ink"}>
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
    <div className="flex h-full flex-col justify-center gap-3 px-6 pt-6 sm:px-7">
      <CommandLine command={PROJECT.installCmd} />
      <p className="text-xs text-ink-2">
        …a potem wszystko klikasz w dashboardzie. Zero YAML-a.
      </p>
    </div>
  );
}

/* ── section ────────────────────────────────────────────────────── */

export function Pillars() {
  return (
    <section id="filary" className="scroll-mt-14">
      <div className="mx-auto max-w-5xl px-4 py-20 sm:px-6 sm:py-28">
        <Reveal className="text-center">
          <h2 className="text-3xl font-semibold tracking-tight text-balance sm:text-5xl">
            Autonomia bez utraty kontroli.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-base text-ink-2 sm:text-lg">
            Cztery rzeczy, które odróżniają {PROJECT.name} od frameworków do
            składania samemu.
          </p>
        </Reveal>

        <Reveal delay={120} className="mt-12">
          <BentoGrid className="lg:grid-cols-3">
            <BentoCard
              name="Suwak uprawnień na każdej umiejętności"
              className="lg:col-span-2"
              eyebrow="Kontrola i zaufanie"
              description="Od pełnej ciszy po pełną autonomię — Ty decydujesz, ile agent może. Propozycje czekają w skrzynce decyzji, a każde działanie ląduje w audycie. Wypróbuj:"
              background={<PermissionControlDemo />}
            />
            <BentoCard
              name="Produkt, nie framework"
              className="lg:col-span-1"
              eyebrow="Instalacja"
              description="Jedna komenda w terminalu, reszta w przejrzystym dashboardzie."
              background={<InstallDemo />}
            />
            <BentoCard
              name="Sam zauważa, sam się odzywa"
              className="lg:col-span-1"
              eyebrow="Proaktywność"
              description="Agent żyje na strumieniu zdarzeń i reaguje, zanim zdążysz zapytać."
              background={<EventFeed />}
            />
            <BentoCard
              name="Kuźnia narzędzi"
              className="lg:col-span-2"
              eyebrow="Samorozbudowa"
              description="Gdy czegoś nie umie, pisze sobie nowe narzędzie: kod, test w sandboxie, Twoja zgoda, rejestracja. Skille to przetestowany kod — nie notatki."
              background={<ForgePipeline />}
            />
          </BentoGrid>
        </Reveal>
      </div>
    </section>
  );
}
