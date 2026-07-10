import { PROJECT } from "@/config/site";

const LINKS = [
  { href: "#filary", label: "Filary" },
  { href: "#mozliwosci", label: "Możliwości" },
  { href: "#jak-dziala", label: "Jak działa" },
];

export function Navbar() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-hairline/60 bg-white/75 backdrop-blur-xl">
      <nav className="mx-auto flex h-14 max-w-5xl items-center gap-6 px-4 sm:px-6">
        <a href="#" className="text-sm font-semibold tracking-tight">
          {PROJECT.name}
        </a>

        <div className="ml-auto flex items-center gap-6">
          {LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="hidden text-xs text-ink-2 transition-colors hover:text-ink sm:block"
            >
              {l.label}
            </a>
          ))}
          <a
            href={PROJECT.repoUrl}
            target="_blank"
            rel="noreferrer"
            className="rounded-full bg-blue px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-blue-soft"
          >
            GitHub
          </a>
        </div>
      </nav>
    </header>
  );
}
