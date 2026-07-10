"use client";

import { useEffect, useRef } from "react";
import { animate, stagger } from "animejs";
import { Terminal } from "@/components/site/terminal";
import { CopyCommand } from "@/components/site/copy-command";
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
        className="mx-auto flex max-w-3xl flex-col items-center px-4 pt-14 pb-10 text-center sm:px-6 sm:pt-20"
      >
        <p
          data-hero-item
          className="inline-flex items-center gap-2 rounded-full bg-fill px-4 py-1.5 text-xs font-medium text-ink-2"
        >
          <span className="pulse-soft size-1.5 rounded-full bg-violet" />
          Open source · Self-hosted · W budowie
        </p>

        <h1
          data-hero-item
          className="mt-6 text-4xl leading-[1.05] font-semibold tracking-tight text-balance sm:text-6xl"
        >
          Twój Jarvis. Twój serwer.
          <br />
          <span className="text-gradient">Twoje zasady.</span>
        </h1>

        <p
          data-hero-item
          className="mt-5 max-w-xl text-base leading-relaxed text-ink-2 sm:text-lg"
        >
          Osobisty agent AI, który mieszka na Twoim komputerze — ogarnia
          maile, kalendarz i codzienne sprawy, a o każdą ważną decyzję pyta
          Ciebie.
        </p>

        <div data-hero-item className="mt-9 w-full">
          <CopyCommand />
          <p className="mt-2.5 text-xs text-ink-2">
            Jedna komenda w terminalu — reszta w dashboardzie.
          </p>
        </div>

        <div
          data-hero-item
          className="mt-7 flex flex-wrap items-center justify-center gap-5"
        >
          <a
            href={PROJECT.repoUrl}
            target="_blank"
            rel="noreferrer"
            className="rounded-full bg-blue px-6 py-3 text-sm font-medium text-white transition-all hover:bg-blue-soft hover:shadow-[0_8px_24px_-8px_rgba(29,78,216,0.5)] active:scale-[0.98]"
          >
            Zobacz na GitHubie
          </a>
          <a
            href="#wiecej"
            className="text-sm font-medium text-blue transition-colors hover:text-violet"
          >
            Co potrafi <span aria-hidden="true">↓</span>
          </a>
        </div>

        <div data-hero-item className="mt-14 w-full max-w-2xl">
          <Terminal />
        </div>
      </div>
    </section>
  );
}
