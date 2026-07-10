import { PROJECT } from "@/config/site";

export function Navbar() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-hairline/60 bg-[#0e0f13]/80 backdrop-blur-xl">
      <nav className="mx-auto flex h-14 max-w-4xl items-center px-4 sm:px-6">
        <a href="#" className="text-sm font-semibold tracking-tight text-ink">
          {PROJECT.name}
        </a>
        <a
          href={PROJECT.repoUrl}
          target="_blank"
          rel="noreferrer"
          className="ml-auto rounded-full bg-blue px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-blue-soft"
        >
          GitHub
        </a>
      </nav>
    </header>
  );
}
