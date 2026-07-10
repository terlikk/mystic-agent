"use client";

import { useEffect, useRef } from "react";
import { createTimeline, stagger } from "animejs";
import { ASCII_BANNER, PROJECT } from "@/config/site";

const BOOT_CMD = `${PROJECT.cli} start`;

/* ── pixel art rendered as SVG rects ──────────────────────────────
   Webfont subsets don't ship the █ block glyphs and system fallbacks
   have different metrics (that made the text banner look crooked),
   so all pixel art is drawn on an SVG grid instead. Each shape gets
   a darker offset copy underneath — the chunky retro drop shadow. */

type Runs = [number, number][][];

function toRuns(lines: readonly string[], ch: string): Runs {
  return lines.map((line) => {
    const runs: [number, number][] = [];
    let start = -1;
    for (let x = 0; x <= line.length; x++) {
      if (line[x] === ch) {
        if (start < 0) start = x;
      } else if (start >= 0) {
        runs.push([start, x - start]);
        start = -1;
      }
    }
    return runs;
  });
}

const SHADOW = 0.55;

function PixelArt({
  runs,
  width,
  gradId,
  rowShift,
  className,
  label,
}: {
  runs: Runs;
  width: number;
  gradId: string;
  rowShift?: (y: number) => number;
  className?: string;
  label?: string;
}) {
  const shift = rowShift ?? ((y: number) => y);
  const height = shift(runs.length - 1) + 1;
  const rects = runs.flatMap((row, y) =>
    row.map(([x, len]) => ({ x, y: shift(y), len }))
  );
  return (
    <svg
      viewBox={`0 0 ${width + SHADOW} ${height + SHADOW}`}
      className={className}
      role={label ? "img" : "presentation"}
      aria-label={label}
      aria-hidden={label ? undefined : true}
      shapeRendering="crispEdges"
    >
      <defs>
        <linearGradient
          id={gradId}
          gradientUnits="userSpaceOnUse"
          x1="0"
          y1="0"
          x2="0"
          y2={height}
        >
          <stop offset="0" stopColor="#2563eb" />
          <stop offset="1" stopColor="#7c3aed" />
        </linearGradient>
        <linearGradient
          id={`${gradId}-sh`}
          gradientUnits="userSpaceOnUse"
          x1="0"
          y1="0"
          x2="0"
          y2={height}
        >
          <stop offset="0" stopColor="#1e3a8a" />
          <stop offset="1" stopColor="#4c1d95" />
        </linearGradient>
      </defs>
      {/* shadow layer first, then the lit layer on top */}
      {rects.map((r, i) => (
        <rect
          key={`s${i}`}
          x={r.x + SHADOW}
          y={r.y + SHADOW}
          width={r.len}
          height={1.03}
          fill={`url(#${gradId}-sh)`}
        />
      ))}
      {rects.map((r, i) => (
        <rect
          key={i}
          x={r.x}
          y={r.y}
          width={r.len}
          height={1.03}
          fill={`url(#${gradId})`}
        />
      ))}
    </svg>
  );
}

const BANNER_W = Math.max(...ASCII_BANNER.map((l) => l.length));
const BANNER_RUNS = toRuns(ASCII_BANNER, "█");
/* rows 0-4 = MYSTIC, rows 5-9 = AGENT; small gap between the words */
const WORD_BREAK = 5;
const WORD_GAP = 0.7;
const bannerShift = (y: number) => (y >= WORD_BREAK ? y + WORD_GAP : y);

/* the mark: a pixel crystal — mystic, cuttable into a favicon later */
const GEM = [
  "  #########  ",
  " ########### ",
  "#############",
  "#############",
  " ########### ",
  "  #########  ",
  "   #######   ",
  "    #####    ",
  "     ###     ",
  "      #      ",
] as const;
const GEM_RUNS = toRuns(GEM, "#");

const NEOFETCH_ROWS: [string, string][] = [
  ["DESIGNATION", `${PROJECT.name} ${PROJECT.version}`],
  ["RUNTIME", "twój sprzęt · localhost:7700"],
  ["CHANNELS", "telegram · web dashboard"],
  ["SKILLS", "maile · kalendarz · czujki · research"],
  ["PRIVACY", "0 chmury · 0 telemetrii · 0 kont"],
  ["LICENSE", "MIT · open source"],
];

/**
 * The hero centerpiece: a live terminal that boots the agent —
 * types the start command, stamps the pixel banner, then prints
 * a neofetch-style status table with the crystal mark.
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

    const banner = root.querySelector<HTMLElement>("[data-banner]");
    const tableRows = root.querySelectorAll<HTMLElement>("[data-row]");
    const statusLine = root.querySelector<HTMLElement>("[data-status]");
    const promptLine = root.querySelector<HTMLElement>("[data-prompt]");
    const all = [banner, ...tableRows, statusLine, promptLine].filter(
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
    });

    if (banner) {
      tl.add(
        banner,
        {
          opacity: [0, 1],
          scale: [0.96, 1],
          duration: 450,
          ease: "outBack",
        },
        "+=280"
      );
    }

    tl.add(
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
        <span className="ml-3 truncate text-xs text-white/40">
          {PROJECT.cli} — sesja lokalna
        </span>
        <span className="ml-auto flex shrink-0 items-center gap-1.5 text-[10px] tracking-widest whitespace-nowrap text-white/50 uppercase">
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

        <div data-banner className="origin-left py-1">
          <PixelArt
            runs={BANNER_RUNS}
            width={BANNER_W}
            gradId="banner-grad"
            rowShift={bannerShift}
            className="w-full max-w-[420px]"
            label={PROJECT.name}
          />
        </div>

        <div className="flex items-start gap-5 pt-1">
          <div data-row className="hidden w-14 shrink-0 pt-1 sm:block">
            <PixelArt runs={GEM_RUNS} width={GEM[0].length} gradId="gem-grad" />
          </div>
          <div className="min-w-0 flex-1 space-y-1 text-xs sm:text-[13px]">
            {NEOFETCH_ROWS.map(([k, v]) => (
              <p key={k} data-row className="flex will-change-transform">
                <span className="w-24 shrink-0 text-[#7aa5ff] sm:w-28">
                  {k}
                </span>
                <span className="flex-1 text-white/80">{v}</span>
              </p>
            ))}
          </div>
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
