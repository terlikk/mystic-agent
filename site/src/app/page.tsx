import { AuroraBackground } from "@/components/ui/aurora-background";
import { Navbar } from "@/components/site/navbar";
import { CopyCommand } from "@/components/site/copy-command";
import { HeroIntro } from "@/components/site/hero-intro";
import { PROJECT } from "@/config/site";

export default function Home() {
  return (
    <AuroraBackground
      showRadialGradient
      className="!h-auto min-h-screen !items-stretch !justify-start overflow-x-hidden !bg-[#08080f]"
    >
      <Navbar />

      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-3xl flex-col items-center justify-center px-6 text-center">
        <HeroIntro>
          <h1
            data-intro
            className="text-[2rem] leading-[1.1] font-semibold tracking-tight text-balance break-words text-white sm:text-6xl sm:leading-[1.06]"
          >
            Agent, który nie czeka,
            <br className="hidden sm:block" /> aż{" "}
            <span className="text-[#c7d2fe]">napiszesz</span>.
          </h1>

          <div data-intro className="mx-auto mt-9 w-full max-w-md">
            <CopyCommand />
          </div>

          <p
            data-intro
            className="mx-auto mt-9 max-w-xl text-base leading-relaxed font-medium text-white/80 sm:text-lg"
          >
            MysticAgent to osobisty agent AI, który mieszka na Twoim
            komputerze. Sam pilnuje spraw, załatwia je i przypomina — a odzywa
            się dopiero, gdy ma coś wartościowego albo potrzebuje Twojej zgody.
          </p>

          <p
            data-intro
            className="mx-auto mt-6 max-w-xl text-base leading-relaxed font-medium text-white/70 sm:text-lg"
          >
            Ogarnia pocztę i kalendarz, robi research w sieci, wchodzi na strony
            i wypełnia formularze za Ciebie, czyta pliki i PDF-y, rozumie Twój
            głos i zdjęcia. Każdą jego zdolność trzymasz na suwaku: ważne rzeczy
            zatwierdzasz, resztę robi sam — a wszystko widzisz w audycie. Czego
            nie umie dziś, dopisze sobie jutro.
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
