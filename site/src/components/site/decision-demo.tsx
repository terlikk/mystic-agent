"use client";

import { useEffect, useRef, useState } from "react";
import { animate } from "animejs";

/**
 * The signature moment: the agent's core loop shown as a live terminal —
 * an event arrives, the agent proposes, you approve, it acts, it's logged.
 * This is the "autonomy on your terms" philosophy, in motion.
 */
type Line = {
  who: "event" | "agent" | "you" | "done" | "audit";
  text: string;
};

const SCRIPT: Line[] = [
  { who: "event", text: "nowy mail od: klient@firma.pl — „Prośba o wycenę”" },
  { who: "agent", text: "Proponuję: odpisać z ofertą i cennikiem." },
  { who: "you", text: "Zatwierdzasz ✓" },
  { who: "done", text: "wysłano odpowiedź do klient@firma.pl" },
  { who: "audit", text: "email_send · wykonano po zgodzie · zapisano w audycie" },
];

const STYLE: Record<Line["who"], { label: string; cls: string }> = {
  event: { label: "▸ zdarzenie", cls: "text-white/55" },
  agent: { label: "◆ agent", cls: "text-[#a78bfa]" },
  you: { label: "✓ Ty", cls: "text-[#22d3ee]" },
  done: { label: "→ zrobione", cls: "text-[#4ade80]" },
  audit: { label: "· audyt", cls: "text-white/45" },
};

export function DecisionDemo() {
  const ref = useRef<HTMLDivElement>(null);
  const [shown, setShown] = useState(0);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setShown(SCRIPT.length);
      return;
    }
    let i = 0;
    let alive = true;
    const tick = () => {
      if (!alive) return;
      i = i >= SCRIPT.length ? 1 : i + 1;
      setShown(i);
    };
    setShown(1);
    const id = setInterval(tick, 1500);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  useEffect(() => {
    const last = ref.current?.querySelector<HTMLElement>("[data-line]:last-child");
    if (!last) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    animate(last, {
      opacity: [0, 1],
      translateY: [6, 0],
      duration: 420,
      ease: "outQuad",
    });
  }, [shown]);

  return (
    <div className="overflow-hidden rounded-2xl border border-white/8 bg-term shadow-[0_24px_70px_-24px_rgba(0,0,0,0.7)]">
      <div className="flex items-center gap-2 border-b border-white/8 px-4 py-3">
        <span className="size-2.5 rounded-full bg-white/15" />
        <span className="size-2.5 rounded-full bg-white/15" />
        <span className="size-2.5 rounded-full bg-white/15" />
        <span className="ml-2 font-mono text-[11px] text-white/40">
          pętla agenta
        </span>
        <span className="ml-auto flex items-center gap-1.5 font-mono text-[10px] tracking-widest text-white/45 uppercase">
          <span
            className="size-1.5 rounded-full bg-[#22d3ee]"
            style={{ animation: "cursor-blink 1.4s steps(1) infinite" }}
          />
          na żywo
        </span>
      </div>
      <div ref={ref} className="min-h-[220px] space-y-2.5 px-5 py-5 font-mono text-[13px] leading-relaxed">
        {SCRIPT.slice(0, shown).map((l, i) => {
          const s = STYLE[l.who];
          return (
            <p key={i} data-line className="flex gap-3">
              <span className={`w-24 shrink-0 ${s.cls}`}>{s.label}</span>
              <span className="text-white/85">{l.text}</span>
            </p>
          );
        })}
      </div>
    </div>
  );
}
