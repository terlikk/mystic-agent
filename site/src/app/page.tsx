import { AuroraBackground } from "@/components/ui/aurora-background";
import { Navbar } from "@/components/site/navbar";
import { CopyCommand } from "@/components/site/copy-command";
import { HeroIntro } from "@/components/site/hero-intro";
import { PROJECT } from "@/config/site";

export default function Home() {
  return (
    <AuroraBackground
      showRadialGradient
      className="!h-auto min-h-screen !items-stretch !justify-start !bg-[#08080f]"
    >
      <Navbar />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-3xl flex-col items-center justify-center px-6 text-center">
        <HeroIntro>
          <p
            data-intro
            className="font-mono text-[11px] tracking-[0.28em] text-white/45 uppercase"
          >
            open source · self-hosted
          </p>

          <h1
            data-intro
            className="mt-7 text-4xl leading-[1.08] font-medium tracking-tight text-balance text-white sm:text-6xl"
          >
            Agent, który nie czeka,
            <br />
            aż <span className="text-[#c7d2fe]">napiszesz</span>.
          </h1>

          <p
            data-intro
            className="mx-auto mt-6 max-w-lg text-[15px] leading-relaxed text-white/60 sm:text-base"
          >
            Mieszka na Twoim komputerze i sam pilnuje, załatwia i przypomina —
            a odzywa się dopiero, gdy ma coś wartościowego albo potrzebuje
            Twojej zgody.
          </p>

          <div data-intro className="mx-auto mt-9 w-full max-w-md">
            <CopyCommand />
          </div>

          <p data-intro className="mt-3 font-mono text-[11px] text-white/40">
            jedna komenda · macOS / Linux · Python 3.11+
          </p>

          <p
            data-intro
            className="mx-auto mt-12 max-w-xl font-mono text-[12px] leading-relaxed text-white/35"
          >
            maile · kalendarz · research · przeglądarka · głos · pamięć ·
            płatności z limitem — a czego nie umie, dopisuje sobie sam.
          </p>
        </HeroIntro>
      </div>

      <footer className="relative z-10 mx-auto flex w-full max-w-4xl items-center justify-between px-6 pb-8 font-mono text-xs text-white/35">
        <span>{PROJECT.name} · MIT</span>
        <a
          href={PROJECT.repoUrl}
          target="_blank"
          rel="noreferrer"
          className="transition-colors hover:text-white/70"
        >
          github.com/{PROJECT.repoSlug}
        </a>
      </footer>
    </AuroraBackground>
  );
}
