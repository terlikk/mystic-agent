"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { CopyCommand } from "@/components/site/copy-command";

const FRAMES = ["/core-1.jpg", "/core-2.jpg", "/core-3.jpg", "/core-4.jpg"];

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
  const [p, setP] = useState(0); // 0 .. FRAMES.length-1
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    setReduced(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    let raf = 0;
    const update = () => {
      raf = 0;
      const el = trackRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const scrollable = rect.height - window.innerHeight;
      const scrolled = Math.min(Math.max(-rect.top, 0), scrollable);
      const t = scrollable > 0 ? scrolled / scrollable : 0;
      setP(t * (FRAMES.length - 1));
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  const frameOpacity = (i: number) =>
    reduced ? (i === 0 ? 1 : 0) : Math.max(0, 1 - Math.abs(p - i));

  // scroll-linked zoom + drift gives the orb a sense of motion
  const scale = reduced ? 1 : 1 + p * 0.05;
  const drift = reduced ? 0 : (p - 1.5) * 1.5; // subtle vertical parallax %

  // per-step text visibility (bell around each step center)
  const stepOn = (i: number) =>
    reduced ? (i === 0 ? 1 : 0) : Math.max(0, 1 - Math.abs(p - i) * 1.6);

  // install block reveals near the last frame
  const installOn = reduced ? 1 : Math.max(0, (p - 2.2) / 0.8);
  const lastCenter = FRAMES.length - 1;

  return (
    <section
      ref={trackRef}
      className="relative bg-[#04060a]"
      style={{ height: reduced ? "100vh" : `${FRAMES.length * 100}vh` }}
      aria-label="Prezentacja agenta"
    >
      <div className="sticky top-0 h-screen w-full overflow-hidden">
        {/* orb frames — crossfade + zoom + drift */}
        <div
          className="absolute inset-0 animate-[orb-breathe_9s_ease-in-out_infinite] will-change-transform"
          style={{ transform: `scale(${scale}) translateY(${drift}%)` }}
          aria-hidden="true"
        >
          {FRAMES.map((src, i) => (
            <div
              key={src}
              className="absolute inset-0 will-change-[opacity]"
              style={{ opacity: frameOpacity(i) }}
            >
              <Image
                src={src}
                alt=""
                fill
                priority={i === 0}
                sizes="100vw"
                className="object-cover"
              />
            </div>
          ))}
        </div>

        {/* vignette for depth + legibility on the sides */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(100% 100% at 50% 45%, rgba(4,6,10,0) 30%, rgba(4,6,10,0.55) 75%, rgba(4,6,10,0.9))",
          }}
          aria-hidden="true"
        />

        {/* side captions — alternate left / right per step */}
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
                  : `translateX(${(1 - on) * dir * 40}px)`,
                pointerEvents: on > 0.5 ? "auto" : "none",
              }}
            >
              <p className="font-mono text-[11px] tracking-[0.3em] text-[#22d3ee] uppercase">
                {step.kicker}
              </p>
              <h2 className="mt-4 text-4xl leading-[1.05] font-semibold whitespace-pre-line text-white sm:text-5xl">
                {step.title}
              </h2>
              <p className="mt-4 max-w-xs text-sm leading-relaxed text-white/65 sm:text-base">
                {step.sub}
              </p>
            </div>
          );
        })}

        {/* final: install command, dead center */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center"
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
          {FRAMES.map((_, i) => (
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
