"use client";

import { useRef, useState, type ReactNode } from "react";
import { animate } from "animejs";

export function ContentTabs({
  tabs,
}: {
  tabs: { key: string; label: string; content: ReactNode }[];
}) {
  const [active, setActive] = useState(0);
  const panelRef = useRef<HTMLDivElement>(null);

  const select = (i: number) => {
    if (i === active) return;
    setActive(i);
    if (
      panelRef.current &&
      !window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      animate(panelRef.current, {
        opacity: [0, 1],
        translateY: [10, 0],
        duration: 420,
        ease: "outCubic",
      });
    }
  };

  return (
    <div id="wiecej" className="mx-auto max-w-6xl scroll-mt-16 px-4 pb-16 sm:px-6">
      <div
        role="tablist"
        aria-label="Sekcje strony"
        className="mx-auto flex w-fit max-w-full overflow-x-auto rounded-full bg-fill p-1"
      >
        {tabs.map((t, i) => (
          <button
            key={t.key}
            role="tab"
            id={`tab-${t.key}`}
            aria-selected={active === i}
            aria-controls={`panel-${t.key}`}
            onClick={() => select(i)}
            className={`shrink-0 rounded-full px-4 py-2 text-xs font-medium whitespace-nowrap transition-all duration-300 sm:px-5 sm:text-sm ${
              active === i
                ? "bg-white text-ink shadow-sm"
                : "text-ink-2 hover:text-ink"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div
        ref={panelRef}
        role="tabpanel"
        id={`panel-${tabs[active].key}`}
        aria-labelledby={`tab-${tabs[active].key}`}
        className="mt-8"
      >
        {tabs[active].content}
      </div>
    </div>
  );
}
