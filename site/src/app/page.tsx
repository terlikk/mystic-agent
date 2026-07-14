import { Navbar } from "@/components/site/navbar";
import { CopyCommand } from "@/components/site/copy-command";
import { DecisionDemo } from "@/components/site/decision-demo";
import { HeroIntro } from "@/components/site/hero-intro";
import { Reveal } from "@/components/site/reveal";
import { PROJECT } from "@/config/site";

const EDGES = [
  {
    id: "act",
    title: "Ma ręce, nie tylko język",
    body: "Nie odpowiada — działa. Wysyła maile, rezerwuje, wchodzi na strony i klika za Ciebie.",
  },
  {
    id: "proactive",
    title: "Pracuje, gdy Ciebie nie ma",
    body: "Mail, spadek ceny, zbliżający się termin — reaguje pierwszy, zanim zdążysz zauważyć.",
  },
  {
    id: "control",
    title: "Autonomia na Twoich zasadach",
    body: "Suwak od „pytaj o wszystko” po „działaj sam”. Każdy ruch w audycie.",
  },
  {
    id: "grow",
    title: "Rośnie razem z Tobą",
    body: "Czego nie umie dziś, dopisze sobie jutro — nowe narzędzie, test w izolacji, Twoja zgoda.",
  },
];

const CAPS = [
  ["komunikacja", "poczta · telefon (wkrótce)"],
  ["czas", "kalendarz · przypomnienia · zadania"],
  ["wiedza", "research w sieci · przeglądarka · pliki i PDF"],
  ["pamięć", "notatki · kontakty · pamięć długotrwała"],
  ["zmysły", "wiadomości głosowe · zdjęcia"],
  ["ostrożnie", "płatności z limitem · terminal · śledzenie paczek"],
];

const SCENARIOS = [
  "Odpisz temu klientowi, a resztę maili posegreguj.",
  "Kup tę kartę graficzną, jak cena spadnie poniżej 300 zł.",
  "Zarezerwuj stolik na sobotę i wrzuć do kalendarza.",
  "Zadzwoń i umów przegląd auta — jawnie, jako mój asystent.",
];

function SectionLabel({ children }: { children: string }) {
  return (
    <h2 className="font-mono text-sm font-semibold tracking-tight text-ink">
      <span className="text-signal">// </span>
      {children}
    </h2>
  );
}

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
                className="font-mono text-[11px] tracking-[0.18em] text-ink-2 uppercase"
              >
                open source · self-hosted ·{" "}
                <span className="text-signal">wczesna wersja</span>
              </p>
              <h1
                data-intro
                className="mt-5 font-mono text-[2rem] leading-[1.08] font-bold tracking-[-0.02em] text-balance sm:text-[3.1rem]"
              >
                Agent, który nie
                <br />
                czeka, aż <span className="text-signal">napiszesz</span>.
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
          <p className="text-2xl leading-snug font-medium tracking-tight text-balance sm:text-[2rem]">
            To agent z rękami: czyta skrzynkę, wchodzi na strony, a gdy czegoś
            nie umie —{" "}
            <span className="text-signal">pisze sobie nowe narzędzie</span>. Ty
            wyznaczasz granice, on robi resztę.
          </p>
        </Reveal>

        {/* differentiators */}
        <section className="mt-16 grid gap-x-12 gap-y-9 sm:grid-cols-2">
          {EDGES.map((e, i) => (
            <Reveal key={e.id} delay={(i % 2) * 80}>
              <div className="border-t-2 border-ink pt-4">
                <h3 className="font-mono text-[15px] font-semibold text-ink">
                  {e.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-ink-2">
                  {e.body}
                </p>
              </div>
            </Reveal>
          ))}
        </section>

        {/* capabilities — the agent's reach as a spec sheet in its own voice */}
        <Reveal className="mt-24">
          <SectionLabel>co ma pod ręką</SectionLabel>
          <div className="mt-6 divide-y divide-hairline border-y border-hairline">
            {CAPS.map(([label, tools]) => (
              <div
                key={label}
                className="flex flex-col gap-1 py-3.5 sm:flex-row sm:items-baseline sm:gap-6"
              >
                <span className="w-32 shrink-0 font-mono text-[13px] font-medium text-signal">
                  {label}
                </span>
                <span className="font-mono text-[13px] leading-relaxed text-ink-2">
                  {tools}
                </span>
              </div>
            ))}
          </div>
          <p className="mt-4 text-[13px] text-ink-2">
            …a czego nie ma na liście, dopisuje sobie sam.
          </p>
        </Reveal>

        {/* scenarios — say it like a person */}
        <Reveal className="mt-24">
          <SectionLabel>powiedz mu po ludzku</SectionLabel>
          <ul className="mt-6 space-y-3">
            {SCENARIOS.map((s) => (
              <li
                key={s}
                className="flex items-baseline gap-4 font-mono text-[15px] text-ink"
              >
                <span className="text-signal">$</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </Reveal>

        {/* privacy */}
        <Reveal className="mt-24 border-t-2 border-ink pt-8">
          <p className="max-w-2xl text-xl leading-snug font-medium tracking-tight text-balance">
            Mieszka u Ciebie, nie w cudzej chmurze.{" "}
            <span className="text-ink-2">
              Twoje maile, klucze i rozmowy nie trafiają do nikogo — nawet do
              nas. Bo nas tu nie ma: żadnego konta, żadnego serwera, nic nie
              dzwoni do domu.
            </span>
          </p>
        </Reveal>

        <footer className="mt-16 flex items-center justify-between border-t border-hairline pt-6 font-mono text-xs text-ink-2">
          <span>
            {PROJECT.name}
            <span className="text-signal">.</span> · MIT
          </span>
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
