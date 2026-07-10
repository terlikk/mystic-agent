"use client";

import { useState } from "react";
import { PROJECT } from "@/config/site";

/** One-line terminal with the real install command and a copy button. */
export function CopyCommand() {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(PROJECT.installCmd);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      /* clipboard blocked — the text is selectable anyway */
    }
  };

  return (
    <div className="mx-auto flex w-full max-w-2xl items-center gap-3 rounded-xl bg-term px-4 py-3 font-mono text-sm shadow-[0_10px_40px_-16px_rgba(29,29,31,0.5)]">
      <span className="shrink-0 select-none text-[#7aa5ff]">$</span>
      <code className="min-w-0 flex-1 truncate text-left text-white/90">
        {PROJECT.installCmd}
      </code>
      <button
        onClick={copy}
        aria-label="Skopiuj komendę instalacji"
        className={`shrink-0 rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
          copied
            ? "bg-blue/20 text-[#7aa5ff]"
            : "bg-white/10 text-white/70 hover:bg-white/15 hover:text-white"
        }`}
      >
        {copied ? "skopiowano ✓" : "kopiuj"}
      </button>
    </div>
  );
}
