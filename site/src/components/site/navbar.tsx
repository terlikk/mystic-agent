import { PROJECT } from "@/config/site";

/** Minimal dark overlay nav — the whole page is the full-screen orb. */
export function Navbar() {
  return (
    <header className="fixed inset-x-0 top-0 z-50">
      <div
        className="pointer-events-none absolute inset-0 h-20 bg-gradient-to-b from-black/40 to-transparent"
        aria-hidden="true"
      />
      <nav className="relative mx-auto flex h-14 max-w-6xl items-center px-4 sm:px-6">
        <a href="#" className="text-sm font-semibold tracking-tight text-white">
          {PROJECT.name}
        </a>
        <a
          href={PROJECT.repoUrl}
          target="_blank"
          rel="noreferrer"
          className="ml-auto rounded-full bg-white/15 px-4 py-1.5 text-xs font-medium text-white backdrop-blur-sm transition-colors hover:bg-white/25"
        >
          GitHub
        </a>
      </nav>
    </header>
  );
}
