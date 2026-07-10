"use client";

import { useEffect, useRef } from "react";
import { createTimeline, stagger } from "animejs";
import { ASCII_BANNER, PROJECT } from "@/config/site";

const BOOT_CMD = `${PROJECT.cli} start`;

/* Per-line blue→violet gradient. Solid colors per line instead of
   background-clip:text, which Chromium drops on animated descendants. */
function bannerColor(i: number, total: number) {
  const t = total <= 1 ? 0 : i / (total - 1);
  const from = [0x25, 0x63, 0xeb]; // #2563eb
  const to = [0x7c, 0x3a, 0xed]; // #7c3aed
  const c = from.map((f, k) => Math.round(f + (to[k] - f) * t));
  return `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
}

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
      className="overflow-hidden rounded-2xl bg-term font-mono text-[13px] leading-relaxed shadow-[0_24px_70px_-20px_rgba(29,29,31,0.45)]"
      aria-label={`Podgląd terminala: agent ${PROJECT.name} startuje i wyświetla status`}
    >
      {/* macOS window chrome */}
      <div className="flex items-center gap-2 border-b border-white/8 bg-white/4 px-4 py-3">
        <span className="size-3 rounded-full bg-[#ff5f57]" />
        <span className="size-3 rounded-full bg-[#febc2e]" />
        <span className="size-3 rounded-full bg-[#28c840]" />
        <span className="ml-3 text-xs text-white/40">
          {PROJECT.cli} — sesja lokalna
        </span>
        <span className="ml-auto flex items-center gap-1.5 text-[10px] tracking-widest text-white/50 uppercase">
          <span className="pulse-soft size-1.5 rounded-full bg-violet" />
          w budowie
        </span>
      </div>

      <div className="space-y-3 px-4 py-4 sm:px-6 sm:py-5">
        <p className="text-white/90">
          <span className="text-[#7aa5ff]">$ </span>
          <span ref={cmdRef} aria-hidden="true" />
          <span className="cursor-blink text-[#a78bfa]">▊</span>
        </p>

        <pre
          className="overflow-x-auto font-bold"
          style={{ fontSize: "clamp(7px, 2vw, 11px)", lineHeight: 1.3 }}
        >
          {ASCII_BANNER.map((line, i) => (
            <span
              key={i}
              data-banner
              className="block"
              style={{ color: bannerColor(i, ASCII_BANNER.length) }}
            >
              {line}
            </span>
          ))}
        </pre>

        <div className="space-y-1 pt-1">
          {NEOFETCH_ROWS.map(([k, v]) => (
            <p key={k} data-row className="will-change-transform">
              <span className="inline-block w-[7.5rem] text-[#7aa5ff]">
                {k}
              </span>
              <span className="text-white/80">{v}</span>
            </p>
          ))}
          <p data-row className="will-change-transform">
            <span className="inline-block w-[7.5rem] text-[#7aa5ff]">
              LICENSE
            </span>
            <span className="text-white/80">MIT · open source</span>
          </p>
        </div>

        <p data-status className="text-[#a78bfa]">
          ● {PROJECT.version} — projekt w budowie, obserwuj repo
        </p>

        <p data-prompt className="text-white/40">
          <span className="text-[#7aa5ff]">$ </span>czekam na zdarzenia…
        </p>
      </div>
    </div>
  );
}

/** Small dark command chip used elsewhere on the page. */
export function CommandLine({ command }: { command: string }) {
  return (
    <code className="block overflow-x-auto rounded-xl bg-term px-4 py-3 font-mono text-xs break-all text-white/85">
      <span className="text-[#7aa5ff]">$ </span>
      {command}
    </code>
  );
}
