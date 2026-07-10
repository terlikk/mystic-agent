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
      const cw = canvas.clientWidth;
      const ch = canvas.clientHeight;
      if (canvas.width !== cw * dpr || canvas.height !== ch * dpr) {
        canvas.width = cw * dpr;
        canvas.height = ch * dpr;
      }
      // draw "cover": fill the whole canvas, cropping overflow, keep center
      const W = canvas.width;
      const H = canvas.height;
      const ir = img.width / img.height;
      const cr = W / H;
      let dw = W;
      let dh = H;
      if (cr > ir) dh = W / ir;
      else dw = H * ir;
      ctx.drawImage(img, (W - dw) / 2, (H - dh) / 2, dw, dh);
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
      <div className="sticky top-0 h-screen w-full overflow-hidden">
        {/* orb — full-screen, scroll drives the frame */}
        <canvas
          ref={canvasRef}
          className="absolute inset-0 h-full w-full"
          aria-hidden="true"
        />

        {/* vignette for depth + side legibility */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(100% 100% at 50% 45%, rgba(4,6,10,0) 32%, rgba(4,6,10,0.5) 74%, rgba(4,6,10,0.9))",
          }}
          aria-hidden="true"
        />

        {/* side captions — alternate left / right over the orb */}
        {STEPS.map((step, i) => {
          const on = stepOn(i);
          const dir = step.side === "left" ? -1 : 1;
          return (
            <div
              key={i}
              className={`absolute inset-y-0 flex w-full max-w-md flex-col justify-center px-8 sm:px-14 ${
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
              <h2 className="mt-4 text-4xl leading-[1.05] font-semibold whitespace-pre-line text-white sm:text-5xl">
                {step.title}
              </h2>
              <p className="mt-4 max-w-xs text-sm leading-relaxed text-white/70 sm:text-base">
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
