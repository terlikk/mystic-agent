"use client";

import { useEffect, useState } from "react";
import { PROJECT } from "@/config/site";

export function Navbar() {
  const [solid, setSolid] = useState(false);

  useEffect(() => {
    // hero is 4 screens tall; go solid only once past it (over light content)
    const onScroll = () => setSolid(window.scrollY > window.innerHeight * 3.3);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-colors duration-300 ${
        solid
          ? "border-b border-hairline/60 bg-white/75 backdrop-blur-xl"
          : "border-b border-transparent"
      }`}
    >
      <nav className="mx-auto flex h-14 max-w-6xl items-center px-4 sm:px-6">
        <a
          href="#"
          className={`text-sm font-semibold tracking-tight transition-colors ${
            solid ? "text-ink" : "text-white"
          }`}
        >
          {PROJECT.name}
        </a>
        <a
          href={PROJECT.repoUrl}
          target="_blank"
          rel="noreferrer"
          className={`ml-auto rounded-full px-4 py-1.5 text-xs font-medium transition-colors ${
            solid
              ? "bg-blue text-white hover:bg-blue-soft"
              : "bg-white/15 text-white backdrop-blur-sm hover:bg-white/25"
          }`}
        >
          GitHub
        </a>
      </nav>
    </header>
  );
}
