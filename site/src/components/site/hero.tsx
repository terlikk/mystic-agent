"use client";

import { useEffect, useRef } from "react";
import { animate, stagger } from "animejs";
import { FlickeringGrid } from "@/components/ui/flickering-grid";
import { Terminal } from "@/components/site/terminal";
import { PROJECT } from "@/config/site";

export function Hero() {
  const copyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = copyRef.current;
    if (!root) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const items = root.querySelectorAll<HTMLElement>("[data-hero-item]");
    items.forEach((el) => (el.style.opacity = "0"));
    animate(items, {
      opacity: [0, 1],
      translateY: [22, 0],
      duration: 850,
      delay: stagger(110, { start: 120 }),
      ease: "outExpo",
    });
  }, []);

  return (
    <section className="relative overflow-hidden pt-14">
      {/* ambient pixel grid, masked to the top — quiet, not a light show */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          maskImage:
            "radial-gradient(ellipse 90% 70% at 70% 10%, black 30%, transparent 75%)",
          WebkitMaskImage:
            "radial-gradient(ellipse 90% 70% at 70% 10%, black 30%, transparent 75%)",
        }}
        aria-hidden="true"
      >
        <FlickeringGrid
          className="size-full"
          squareSize={3}
          gridGap={9}
          color="#22D3EE"
          maxOpacity={0.14}
          flickerChance={0.12}
        />
      </div>

      <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 py-16 sm:px-6 sm:py-24 lg:grid-cols-[1.05fr_1fr] lg:gap-14">
        <div ref={copyRef}>
          <p
            data-hero-item
            className="font-mono text-xs tracking-wide text-cyan"
          >
            {"// open source · self-hosted · MIT"}
          </p>

          <h1
            data-hero-item
            className="mt-5 font-heading text-4xl leading-[1.08] font-bold tracking-tight text-balance sm:text-5xl lg:text-6xl"
          >
            Twój Jarvis.
            <br />
            Twój serwer.
            <br />
            <span className="glow-cyan text-cyan">Twoje zasady.</span>
          </h1>

          <p
            data-hero-item
            className="mt-6 max-w-xl text-base leading-relaxed text-dim sm:text-lg"
          >
            {PROJECT.name} to agent AI, który mieszka na Twoim komputerze —
            ogarnia maile, kalendarz i codzienne sprawy, a o każdą ważną
            decyzję pyta Ciebie. Twoje dane i klucze nigdy nie opuszczają
            Twojego sprzętu.
          </p>

          <div data-hero-item className="mt-8 flex flex-wrap items-center gap-4">
            <a
              href={PROJECT.repoUrl}
              target="_blank"
              rel="noreferrer"
              className="rounded-md bg-cyan px-5 py-3 font-mono text-sm font-medium text-[#06222a] shadow-[0_0_24px_rgba(34,211,238,0.35)] transition-transform hover:scale-[1.03] active:scale-[0.98]"
            >
              Zobacz na GitHubie ↗
            </a>
            <a
              href="#filary"
              className="rounded-md border border-line px-5 py-3 font-mono text-sm text-foreground/80 transition-colors hover:border-cyan/50 hover:text-cyan"
            >
              Jak to działa ↓
            </a>
          </div>

          <p data-hero-item className="mt-5 font-mono text-xs text-dim">
            instalacja jedną komendą — wkrótce
          </p>
        </div>

        <Terminal />
      </div>
    </section>
  );
}
