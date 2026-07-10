"use client";

import { useEffect, useRef, useState } from "react";
import { CopyCommand } from "@/components/site/copy-command";

const FRAME_COUNT = 61;
const SEGMENTS = 4; // 3 side captions + a final install screen
const frameSrc = (i: number) =>
  `/orb-frames/f${String(i + 1).padStart(3, "0")}.jpg`;

const STEPS = [
  {
    side: "left" as const,
    kicker: "// twój Jarvis",
    title: "Twój Jarvis.\nTwój serwer.",
    sub: "Osobisty agent AI, który mieszka na Twoim komputerze.",
  },
  {
    side: "right" as const,
    kicker: "// proaktywny",
    title: "Sam zauważa.\nSam działa.",
    sub: "Maile, kalendarz, czujki — reaguje, zanim zdążysz zapytać.",
  },
  {
    side: "left" as const,
    kicker: "// pod kontrolą",
    title: "Pyta o to,\nco ważne.",
    sub: "Suwak uprawnień i skrzynka decyzji. Ostatnie słowo masz Ty.",
  },
];

export function ScrollHero() {
  const trackRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imagesRef = useRef<HTMLImageElement[]>([]);
  const [p, setP] = useState(0); // 0 .. SEGMENTS-1
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    setReduced(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  // preload frames + draw the one matching scroll progress
  useEffect(() => {
    const imgs: HTMLImageElement[] = [];
    let loaded = 0;
    const drawFrame = (idx: number) => {
      const canvas = canvasRef.current;
      const img = imgs[idx];
      if (!canvas || !img || !img.complete) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const size = canvas.clientWidth;
      if (canvas.width !== size * dpr) {
        canvas.width = size * dpr;
        canvas.height = size * dpr;
      }
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    for (let i = 0; i < FRAME_COUNT; i++) {
      const img = new Image();
      img.src = frameSrc(i);
      img.onload = () => {
        loaded++;
        if (i === 0) drawFrame(0);
      };
      imgs.push(img);
    }
    imagesRef.current = imgs;

    let raf = 0;
    const update = () => {
      raf = 0;
      const el = trackRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const scrollable = rect.height - window.innerHeight;
      const scrolled = Math.min(Math.max(-rect.top, 0), scrollable);
      const t = scrollable > 0 ? scrolled / scrollable : 0; // 0..1
      setP(t * (SEGMENTS - 1));
      drawFrame(Math.min(FRAME_COUNT - 1, Math.round(t * (FRAME_COUNT - 1))));
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };
    // draw first frame once images start arriving
    const kick = setInterval(() => {
      if (loaded > 0) {
        update();
        clearInterval(kick);
      }
    }, 60);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      clearInterval(kick);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  const stepOn = (i: number) =>
    reduced ? (i === 0 ? 1 : 0) : Math.max(0, 1 - Math.abs(p - i) * 1.7);
  const installOn = reduced ? 1 : Math.max(0, (p - 2.3) / 0.7);
  const lastCenter = SEGMENTS - 1;

  return (
    <section
      ref={trackRef}
      className="relative bg-[#04060a]"
      style={{ height: reduced ? "100vh" : `${SEGMENTS * 100}vh` }}
      aria-label="Prezentacja agenta"
    >
      <div className="sticky top-0 flex h-screen w-full items-center justify-center overflow-hidden">
        {/* orb — contained, centered, scroll drives the frame */}
        <div
          className="pointer-events-none absolute top-[38%] -translate-y-1/2 sm:top-1/2"
          style={{ width: "min(78vw, 44vh)", aspectRatio: "1 / 1" }}
          aria-hidden="true"
        >
          <div
            className="absolute -inset-6 rounded-full opacity-60 blur-2xl"
            style={{ background: "radial-gradient(circle, #22d3ee55, transparent 70%)" }}
          />
          <canvas ref={canvasRef} className="relative h-full w-full" />
        </div>

        {/* side captions — alternate left / right; sit beside/below the orb */}
        {STEPS.map((step, i) => {
          const on = stepOn(i);
          const dir = step.side === "left" ? -1 : 1;
          return (
            <div
              key={i}
              className={`absolute bottom-[12%] flex w-full max-w-xs flex-col px-8 sm:bottom-auto sm:top-1/2 sm:max-w-sm sm:-translate-y-1/2 sm:px-14 ${
                step.side === "left"
                  ? "left-0 items-start text-left"
                  : "right-0 items-end text-right"
              }`}
              style={{
                opacity: on,
                transform: reduced
                  ? "none"
                  : `translateX(${(1 - on) * dir * 36}px)`,
                pointerEvents: on > 0.5 ? "auto" : "none",
              }}
            >
              <p className="font-mono text-[10px] tracking-[0.3em] text-[#22d3ee] uppercase sm:text-[11px]">
                {step.kicker}
              </p>
              <h2 className="mt-3 text-3xl leading-[1.05] font-semibold whitespace-pre-line text-white sm:text-5xl">
                {step.title}
              </h2>
              <p className="mt-3 max-w-xs text-sm leading-relaxed text-white/65 sm:text-base">
                {step.sub}
              </p>
            </div>
          );
        })}

        {/* final: install command, dead center */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center bg-[#04060a]/55 px-6 text-center backdrop-blur-[2px]"
          style={{
            opacity: installOn,
            transform: reduced
              ? "none"
              : `translateY(${(1 - installOn) * 24}px)`,
            pointerEvents: installOn > 0.5 ? "auto" : "none",
          }}
        >
          <p className="font-mono text-[11px] tracking-[0.3em] text-[#22d3ee] uppercase">
            // open source · self-hosted
          </p>
          <h2 className="mt-4 max-w-lg text-4xl leading-[1.05] font-semibold text-white sm:text-5xl">
            Postaw u siebie
            <br />w 5 minut.
          </h2>
          <div className="mt-8 w-full max-w-xl">
            <CopyCommand />
          </div>
          <p className="mt-3 text-xs text-white/45">
            Twoje dane zostają u Ciebie. Zero chmury.
          </p>
        </div>

        {/* progress dots */}
        <div className="absolute inset-x-0 bottom-7 flex items-center justify-center gap-2">
          {Array.from({ length: SEGMENTS }).map((_, i) => (
            <span
              key={i}
              className="h-1 rounded-full transition-all duration-300"
              style={{
                width: Math.round(p) === i ? 22 : 6,
                background:
                  Math.round(p) === i ? "#22d3ee" : "rgba(255,255,255,0.28)",
              }}
            />
          ))}
        </div>

        {!reduced && p < lastCenter - 0.3 && (
          <p className="absolute inset-x-0 bottom-12 text-center font-mono text-[10px] tracking-widest text-white/35 uppercase">
            scroll ↓
          </p>
        )}
      </div>
    </section>
  );
}
