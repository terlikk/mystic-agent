import { PROJECT } from "@/config/site";

const LINKS = [
  { href: "#filary", label: "filary" },
  { href: "#mozliwosci", label: "możliwości" },
  { href: "#jak-dziala", label: "jak działa" },
];

export function Navbar() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-line/60 bg-background/80 backdrop-blur-md">
      <nav className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4 sm:px-6">
        <a
          href="#"
          className="flex items-center gap-2 font-mono text-sm font-medium text-foreground"
        >
          <span className="text-cyan" aria-hidden="true">
            ▚
          </span>
          {PROJECT.cli}
        </a>

        <span className="hidden items-center gap-1.5 rounded-full border border-amber/30 px-2.5 py-0.5 font-mono text-[10px] tracking-widest text-amber uppercase sm:flex">
          <span className="pulse-amber size-1.5 rounded-full bg-amber" />
          w budowie
        </span>

        <div className="ml-auto flex items-center gap-5">
          {LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="hidden font-mono text-xs text-dim transition-colors hover:text-cyan sm:block"
            >
              {l.label}
            </a>
          ))}
          <a
            href={PROJECT.repoUrl}
            target="_blank"
            rel="noreferrer"
            className="rounded-md border border-cyan/40 px-3 py-1.5 font-mono text-xs text-cyan transition-colors hover:bg-cyan/10"
          >
            GitHub ↗
          </a>
        </div>
      </nav>
    </header>
  );
}
