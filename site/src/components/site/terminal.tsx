"use client";

import { useEffect, useRef } from "react";
import { animate, createTimeline, stagger } from "animejs";
import { ASCII_BANNER, PROJECT } from "@/config/site";

const BOOT_CMD = `${PROJECT.cli} start`;

const NEOFETCH_ROWS: [string, string][] = [
  ["DESIGNATION", `${PROJECT.name} ${PROJECT.version}`],
  ["RUNTIME", "twój sprzęt · localhost:7700"],
  ["CHANNELS", "telegram · web dashboard"],
  ["SKILLS", "maile · kalendarz · czujki · research"],
  ["PRIVACY", "0 chmury · 0 telemetrii · 0 kont"],
];

/**
 * The hero centerpiece: a live terminal that boots the agent —
 * types the start command, reveals the pixel banner line by line,
 * then prints a neofetch-style status table.
 */
export function Terminal() {
  const rootRef = useRef<HTMLDivElement>(null);
  const cmdRef = useRef<HTMLSpanElement>(null);
  const started = useRef(false);

  useEffect(() => {
    if (started.current || !rootRef.current) return;
    started.current = true;

    const root = rootRef.current;
    const reduced = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    const bannerLines = root.querySelectorAll<HTMLElement>("[data-banner]");
    const tableRows = root.querySelectorAll<HTMLElement>("[data-row]");
    const statusLine = root.querySelector<HTMLElement>("[data-status]");
    const promptLine = root.querySelector<HTMLElement>("[data-prompt]");
    const all = [...bannerLines, ...tableRows, statusLine, promptLine].filter(
      Boolean
    ) as HTMLElement[];

    if (reduced) {
      if (cmdRef.current) cmdRef.current.textContent = BOOT_CMD;
      all.forEach((el) => (el.style.opacity = "1"));
      return;
    }

    all.forEach((el) => (el.style.opacity = "0"));

    const typing = { n: 0 };
    const tl = createTimeline({ defaults: { ease: "linear" } });

    tl.add(typing, {
      n: BOOT_CMD.length,
      duration: BOOT_CMD.length * 55,
      delay: 500,
      onUpdate: () => {
        if (cmdRef.current) {
          cmdRef.current.textContent = BOOT_CMD.slice(0, Math.round(typing.n));
        }
      },
    })
      .add(
        bannerLines,
        {
          opacity: [0, 1],
          translateY: [4, 0],
          duration: 220,
          delay: stagger(65),
          ease: "outQuad",
        },
        "+=280"
      )
      .add(
        tableRows,
        {
          opacity: [0, 1],
          translateX: [-6, 0],
          duration: 260,
          delay: stagger(90),
          ease: "outQuad",
        },
        "+=120"
      );

    if (statusLine) {
      tl.add(statusLine, { opacity: [0, 1], duration: 300 }, "+=200");
    }
    if (promptLine) {
      tl.add(promptLine, { opacity: [0, 1], duration: 200 }, "+=150");
    }

    return () => {
      tl.pause();
    };
  }, []);

  return (
    <div
      ref={rootRef}
      className="glow-box overflow-hidden rounded-lg border border-line bg-panel font-mono text-[13px] leading-relaxed"
      aria-label={`Podgląd terminala: agent ${PROJECT.name} startuje i wyświetla status`}
    >
      {/* window chrome */}
      <div className="flex items-center gap-2 border-b border-line bg-panel-2 px-4 py-2.5">
        <span className="size-2.5 rounded-full bg-[#2a3548]" />
        <span className="size-2.5 rounded-full bg-[#2a3548]" />
        <span className="size-2.5 rounded-full bg-[#2a3548]" />
        <span className="ml-3 text-xs text-dim">
          {PROJECT.cli} — sesja lokalna
        </span>
        <span className="ml-auto flex items-center gap-1.5 text-[10px] tracking-widest text-amber uppercase">
          <span className="pulse-amber size-1.5 rounded-full bg-amber" />
          w budowie
        </span>
      </div>

      <div className="space-y-3 px-4 py-4 sm:px-5">
        <p className="text-foreground">
          <span className="text-cyan">$ </span>
          <span ref={cmdRef} aria-hidden="true" />
          <span className="cursor-blink text-cyan">▊</span>
        </p>

        <pre
          className="glow-cyan overflow-x-auto text-cyan"
          style={{ fontSize: "clamp(6px, 1.7vw, 10px)", lineHeight: 1.25 }}
        >
          {ASCII_BANNER.map((line, i) => (
            <span key={i} data-banner className="block will-change-transform">
              {line}
            </span>
          ))}
        </pre>

        <div className="space-y-1 pt-1">
          {NEOFETCH_ROWS.map(([k, v]) => (
            <p key={k} data-row className="will-change-transform">
              <span className="inline-block w-[7.5rem] text-cyan">{k}</span>
              <span className="text-foreground/90">{v}</span>
            </p>
          ))}
          <p data-row className="will-change-transform">
            <span className="inline-block w-[7.5rem] text-cyan">LICENSE</span>
            <span className="text-foreground/90">MIT · open source</span>
          </p>
        </div>

        <p data-status className="text-amber">
          ⚠ {PROJECT.version} — projekt w budowie, obserwuj repo
        </p>

        <p data-prompt className="text-dim">
          <span className="text-cyan">$ </span>czekam na zdarzenia…
        </p>
      </div>
    </div>
  );
}

/** Small typed-command line used elsewhere on the page. */
export function CommandLine({ command }: { command: string }) {
  return (
    <code className="block overflow-x-auto rounded-md border border-line bg-panel px-4 py-3 font-mono text-xs text-foreground/90">
      <span className="text-cyan">$ </span>
      {command}
    </code>
  );
}
