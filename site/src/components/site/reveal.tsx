"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { animate } from "animejs";

/**
 * Scroll-triggered reveal. Content is server-rendered visible (SEO, no-JS),
 * hidden just before first paint and animated in when it enters the viewport.
 * Respects prefers-reduced-motion.
 */
export function Reveal({
  children,
  className,
  delay = 0,
}: {
  children: ReactNode;
  className?: string;
  delay?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    el.style.opacity = "0";

    const io = new IntersectionObserver(
      (entries) => {
        if (!entries[0].isIntersecting) return;
        io.disconnect();
        animate(el, {
          opacity: [0, 1],
          translateY: [18, 0],
          duration: 750,
          delay,
          ease: "outCubic",
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -8% 0px" }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [delay]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
