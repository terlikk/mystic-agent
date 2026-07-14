import { PROJECT } from "@/config/site";

export function Navbar() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-hairline/70 bg-[#fbfbfc]/80 backdrop-blur-xl">
      <nav className="mx-auto flex h-14 max-w-5xl items-center px-4 sm:px-6">
        <a
          href="#"
          className="font-mono text-sm font-semibold tracking-tight text-ink"
        >
          {PROJECT.name}
          <span className="text-signal">.</span>
        </a>
        <a
          href={PROJECT.repoUrl}
          target="_blank"
          rel="noreferrer"
          className="ml-auto rounded-md bg-ink px-4 py-1.5 font-mono text-xs font-medium text-white transition-opacity hover:opacity-80"
        >
          GitHub
        </a>
      </nav>
    </header>
  );
}
