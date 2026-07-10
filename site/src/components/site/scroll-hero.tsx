"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";
import { CopyCommand } from "@/components/site/copy-command";
import { PROJECT } from "@/config/site";

const STEPS = [
  {
    src: "/core-1.jpg",
    kicker: "// twój Jarvis",
    title: "Twój Jarvis.\nTwój serwer.",
    sub: "Osobisty agent AI, który mieszka na Twoim komputerze.",
  },
  {
    src: "/core-2.jpg",
    kicker: "// proaktywny",
    title: "Sam zauważa.\nSam działa.",
    sub: "Maile, kalendarz, czujki — reaguje, zanim zdążysz zapytać.",
  },
  {
    src: "/core-3.jpg",
    kicker: "// pod kontrolą",
    title: "Pyta o to,\nco ważne.",
    sub: "Suwak uprawnień i skrzynka decyzji. Ostatnie słowo masz Ty.",
  },
  {
    src: "/core-4.jpg",
    kicker: "// open source",
    title: "Na Twoim\nsprzęcie.",
    sub: "Zero chmury. Zero telemetrii. Twoje dane zostają u Ciebie.",
  },
];

export function ScrollHero() {
  const trackRef = useRef<HTMLDivElement>(null);
  const [progress, setProgress] = useState(0); // 0 .. STEPS.length-1
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
      const p = scrollable > 0 ? scrolled / scrollable : 0;
      setProgress(p * (STEPS.length - 1));
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

  const layerOpacity = (i: number) =>
    reduced ? (i === 0 ? 1 : 0) : Math.max(0, 1 - Math.abs(progress - i));

  const active = Math.round(progress);

  return (
    <section
      ref={trackRef}
      className="relative bg-[#05070c]"
      style={{ height: reduced ? "100vh" : `${STEPS.length * 100}vh` }}
      aria-label="Prezentacja agenta"
    >
      <div className="sticky top-0 h-screen w-full overflow-hidden">
        {/* crossfading image layers */}
        {STEPS.map((step, i) => (
          <div
            key={step.src}
            className="absolute inset-0 will-change-[opacity]"
            style={{ opacity: layerOpacity(i) }}
            aria-hidden="true"
          >
            <Image
              src={step.src}
              alt=""
              fill
              priority={i === 0}
              sizes="100vw"
              className="object-cover"
            />
          </div>
        ))}

        {/* legibility veil */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "radial-gradient(120% 90% at 50% 40%, rgba(5,7,12,0.15), rgba(5,7,12,0.72) 70%, rgba(5,7,12,0.92))",
          }}
          aria-hidden="true"
        />

        {/* content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center">
          <div className="relative h-[13rem] w-full max-w-2xl sm:h-[15rem]">
            {STEPS.map((step, i) => (
              <div
                key={step.src}
                className="absolute inset-0 flex flex-col items-center justify-center"
                style={{
                  opacity: reduced ? (i === 0 ? 1 : 0) : layerOpacity(i) ** 2,
                  transform: reduced
                    ? "none"
                    : `translateY(${(i - progress) * 24}px)`,
                  pointerEvents: active === i ? "auto" : "none",
                }}
              >
                <p className="font-mono text-xs tracking-[0.25em] text-[#22d3ee] uppercase">
                  {step.kicker}
                </p>
                <h2 className="mt-4 text-4xl leading-[1.05] font-semibold whitespace-pre-line text-white sm:text-6xl">
                  {step.title}
                </h2>
                <p className="mt-4 max-w-md text-sm text-white/70 sm:text-base">
                  {step.sub}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* persistent install command */}
        <div className="absolute inset-x-0 bottom-8 flex flex-col items-center gap-3 px-6">
          <CopyCommand />
          <div className="flex items-center gap-2">
            {STEPS.map((_, i) => (
              <span
                key={i}
                className="h-1 rounded-full transition-all duration-300"
                style={{
                  width: active === i ? 22 : 6,
                  background:
                    active === i ? "#22d3ee" : "rgba(255,255,255,0.3)",
                }}
              />
            ))}
          </div>
          {!reduced && (
            <p className="font-mono text-[10px] tracking-widest text-white/40 uppercase">
              scroll ↓
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
