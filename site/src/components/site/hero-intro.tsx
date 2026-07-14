"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { animate, stagger } from "animejs";

/**
 * The page-load moment: hero pieces settle in, one after another, so the
 * first thing you feel is the agent "waking up" rather than a static wall.
 */
export function HeroIntro({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = ref.current;
    if (!root) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const items = root.querySelectorAll<HTMLElement>("[data-intro]");
    items.forEach((el) => (el.style.opacity = "0"));
    animate(items, {
      opacity: [0, 1],
      translateY: [16, 0],
      duration: 780,
      delay: stagger(90, { start: 80 }),
      ease: "outExpo",
    });
  }, []);

  return <div ref={ref}>{children}</div>;
}
