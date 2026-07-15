import { PROJECT } from "@/config/site";

export function Navbar() {
  return (
    <header className="fixed inset-x-0 top-0 z-50">
      <nav className="mx-auto flex h-16 max-w-4xl items-center px-5 sm:px-6">
        <a href="#" className="text-sm font-medium tracking-tight text-white">
          {PROJECT.name}
        </a>
        <a
          href={PROJECT.repoUrl}
          target="_blank"
          rel="noreferrer"
          className="ml-auto rounded-full border border-white/15 px-4 py-1.5 text-xs font-medium text-white/90 backdrop-blur-sm transition-colors hover:bg-white/10"
        >
          GitHub
        </a>
      </nav>
    </header>
  );
}
