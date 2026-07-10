"use client";

import { useEffect, useRef } from "react";
import { animate, stagger } from "animejs";
import { Terminal } from "@/components/site/terminal";
import { PROJECT } from "@/config/site";

export function Hero() {
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const items = root.querySelectorAll<HTMLElement>("[data-hero-item]");
    items.forEach((el) => (el.style.opacity = "0"));
    animate(items, {
      opacity: [0, 1],
      translateY: [20, 0],
      duration: 850,
      delay: stagger(110, { start: 80 }),
      ease: "outExpo",
    });
  }, []);

  return (
    <section className="pt-14">
      <div
        ref={rootRef}
        className="mx-auto grid max-w-6xl items-center gap-10 px-4 pt-12 pb-10 sm:px-6 lg:grid-cols-[1.05fr_1fr] lg:gap-14 lg:pt-16"
      >
        <div className="text-center lg:text-left">
          <p
            data-hero-item
            className="inline-flex items-center gap-2 rounded-full bg-fill px-4 py-1.5 text-xs font-medium text-ink-2"
          >
            <span className="pulse-soft size-1.5 rounded-full bg-violet" />
            Open source · Self-hosted · W budowie
          </p>

          <h1
            data-hero-item
            className="mt-6 text-4xl leading-[1.06] font-semibold tracking-tight text-balance sm:text-5xl lg:text-6xl"
          >
            Twój Jarvis. Twój serwer.
            <br />
            <span className="text-gradient">Twoje zasady.</span>
          </h1>

          <p
            data-hero-item
            className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-ink-2 sm:text-lg lg:mx-0"
          >
            {PROJECT.name} to agent AI, który mieszka na Twoim komputerze —
            ogarnia maile, kalendarz i codzienne sprawy, a o każdą ważną
            decyzję pyta Ciebie. Twoje dane nigdy nie opuszczają Twojego
            sprzętu.
          </p>

          <div
            data-hero-item
            className="mt-8 flex flex-wrap items-center justify-center gap-5 lg:justify-start"
          >
            <a
              href={PROJECT.repoUrl}
              target="_blank"
              rel="noreferrer"
              className="rounded-full bg-blue px-6 py-3 text-sm font-medium text-white transition-all hover:bg-blue-soft hover:shadow-[0_8px_24px_-8px_rgba(29,78,216,0.5)] active:scale-[0.98]"
            >
              Zobacz na GitHubie
            </a>
            <span className="text-xs text-ink-2">
              instalacja jedną komendą — wkrótce
            </span>
          </div>
        </div>

        <div data-hero-item>
          <Terminal />
        </div>
      </div>
    </section>
  );
}
