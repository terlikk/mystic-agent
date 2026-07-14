import { Navbar } from "@/components/site/navbar";
import { CopyCommand } from "@/components/site/copy-command";
import { DecisionDemo } from "@/components/site/decision-demo";
import { HeroIntro } from "@/components/site/hero-intro";
import { Reveal } from "@/components/site/reveal";
import { PROJECT } from "@/config/site";

const EDGES = [
  {
    title: "Ma ręce, nie tylko język",
    body: "Nie odpowiada — działa. Wysyła maile, rezerwuje, wchodzi na strony i klika za Ciebie.",
  },
  {
    title: "Pracuje, gdy Ciebie nie ma",
    body: "Mail, spadek ceny, zbliżający się termin — reaguje pierwszy, zanim zdążysz zauważyć.",
  },
  {
    title: "Autonomia na Twoich zasadach",
    body: "Suwak od „pytaj o wszystko” po „działaj sam”. Każdy ruch w audycie.",
  },
  {
    title: "Rośnie razem z Tobą",
    body: "Czego nie umie dziś, dopisze sobie jutro — nowe narzędzie, test w izolacji, Twoja zgoda.",
  },
];

const CAPS = [
  ["Komunikacja", "poczta · telefon (wkrótce)"],
  ["Czas", "kalendarz · przypomnienia · zadania"],
  ["Wiedza", "research w sieci · przeglądarka · pliki i PDF"],
  ["Pamięć", "notatki · kontakty · pamięć długotrwała"],
  ["Zmysły", "wiadomości głosowe · zdjęcia"],
  ["Ostrożnie", "płatności z limitem · terminal · śledzenie paczek"],
];

const SCENARIOS = [
  "Odpisz temu klientowi, a resztę maili posegreguj.",
  "Kup tę kartę graficzną, jak cena spadnie poniżej 300 zł.",
  "Zarezerwuj stolik na sobotę i wrzuć do kalendarza.",
  "Zadzwoń i umów przegląd auta — jawnie, jako mój asystent.",
];

export default function Home() {
  return (
    <div className="grain relative overflow-clip">
      <Navbar />
      <main className="relative mx-auto max-w-5xl px-5 pt-24 pb-20 sm:px-6">
        <div className="ambient-glow" aria-hidden="true" />

        {/* hero */}
        <HeroIntro>
          <section className="relative grid items-center gap-12 lg:grid-cols-[1.05fr_1fr] lg:gap-16">
            <div>
              <p
                data-intro
                className="font-mono text-[11px] tracking-[0.2em] text-ink-2 uppercase"
              >
                open source · self-hosted ·{" "}
                <span className="text-indigo">wczesna wersja</span>
              </p>
              <h1
                data-intro
                className="mt-5 font-heading text-[2.7rem] leading-[1.02] font-medium tracking-[-0.01em] text-balance sm:text-[4rem]"
              >
                Agent, który nie
                <br />
                czeka, aż <em className="text-indigo italic">napiszesz</em>.
              </h1>
              <p
                data-intro
                className="mt-6 max-w-md text-[15px] leading-relaxed text-ink-2 sm:text-base"
              >
                {PROJECT.name} mieszka na Twoim komputerze i sam pilnuje,
                załatwia i przypomina — a odzywa się dopiero, gdy ma coś
                wartościowego albo potrzebuje Twojej zgody.
              </p>
              <div data-intro className="mt-7 max-w-md">
                <CopyCommand />
              </div>
              <p data-intro className="mt-2.5 font-mono text-[11px] text-ink-2">
                jedna komenda · macOS / Linux · Python 3.11+
              </p>
            </div>

            <div data-intro>
              <DecisionDemo />
            </div>
          </section>
        </HeroIntro>

        {/* manifesto */}
        <Reveal className="mt-28 max-w-3xl">
          <p className="font-heading text-2xl leading-snug font-medium text-balance sm:text-[2rem]">
            To agent z rękami: czyta skrzynkę, wchodzi na strony, a gdy czegoś
            nie umie —{" "}
            <span className="text-indigo">pisze sobie nowe narzędzie</span>. Ty
            wyznaczasz granice, on robi resztę.
          </p>
        </Reveal>

        {/* differentiators */}
        <section className="mt-16 grid gap-x-12 gap-y-9 sm:grid-cols-2">
          {EDGES.map((e, i) => (
            <Reveal key={e.title} delay={(i % 2) * 80}>
              <div className="border-t border-hairline pt-4">
                <h2 className="font-heading text-lg font-medium text-ink">
                  {e.title}
                </h2>
                <p className="mt-1.5 text-sm leading-relaxed text-ink-2">
                  {e.body}
                </p>
              </div>
            </Reveal>
          ))}
        </section>

        {/* capabilities — the agent's reach, as an index in its own voice */}
        <Reveal className="mt-24">
          <h2 className="font-heading text-2xl font-medium sm:text-[1.7rem]">
            Co ma pod ręką
          </h2>
          <div className="mt-7 grid gap-x-12 gap-y-6 sm:grid-cols-2">
            {CAPS.map(([label, tools]) => (
              <div
                key={label}
                className="flex flex-col gap-1 border-t border-hairline/70 pt-3 sm:flex-row sm:items-baseline sm:gap-6"
              >
                <span className="w-32 shrink-0 font-heading text-[15px] text-ink">
                  {label}
                </span>
                <span className="font-mono text-[13px] leading-relaxed text-ink-2">
                  {tools}
                </span>
              </div>
            ))}
          </div>
          <p className="mt-6 text-[13px] text-ink-2">
            …a czego nie ma na liście, dopisuje sobie sam.
          </p>
        </Reveal>

        {/* scenarios — say it like a person */}
        <Reveal className="mt-24">
          <h2 className="font-heading text-2xl font-medium sm:text-[1.7rem]">
            Powiedz mu po ludzku
          </h2>
          <ul className="mt-6 space-y-3.5">
            {SCENARIOS.map((s) => (
              <li key={s} className="flex items-baseline gap-4">
                <span className="font-mono text-xs text-indigo">→</span>
                <span className="font-heading text-lg text-ink italic sm:text-xl">
                  „{s}”
                </span>
              </li>
            ))}
          </ul>
        </Reveal>

        {/* privacy — quiet, clever */}
        <Reveal className="mt-24 border-t border-hairline pt-8">
          <p className="max-w-2xl font-heading text-xl leading-snug font-medium text-balance">
            Mieszka u Ciebie, nie w cudzej chmurze.{" "}
            <span className="text-ink-2">
              Twoje maile, klucze i rozmowy nie trafiają do nikogo — nawet do
              nas. Bo nas tu nie ma: żadnego konta, żadnego serwera, nic nie
              dzwoni do domu.
            </span>
          </p>
        </Reveal>

        <footer className="mt-16 flex items-center justify-between border-t border-hairline/70 pt-6 font-mono text-xs text-ink-2">
          <span>{PROJECT.name} · MIT</span>
          <a
            href={PROJECT.repoUrl}
            target="_blank"
            rel="noreferrer"
            className="transition-colors hover:text-ink"
          >
            github.com/{PROJECT.repoSlug}
          </a>
        </footer>
      </main>
    </div>
  );
}
