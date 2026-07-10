import { Navbar } from "@/components/site/navbar";
import { CopyCommand } from "@/components/site/copy-command";
import { DecisionDemo } from "@/components/site/decision-demo";
import { PROJECT } from "@/config/site";

const EDGES = [
  {
    k: "01",
    title: "Ma ręce, nie tylko język",
    body: "Nie odpowiada — działa. Wysyła maile, rezerwuje, wchodzi na strony i klika za Ciebie.",
  },
  {
    k: "02",
    title: "Pracuje, gdy Ciebie nie ma",
    body: "Mail, spadek ceny, zbliżający się termin — reaguje pierwszy, zanim zdążysz zauważyć.",
  },
  {
    k: "03",
    title: "Autonomia na Twoich zasadach",
    body: "Suwak od „pytaj o wszystko” po „działaj sam”. Każdy ruch w audycie.",
  },
  {
    k: "04",
    title: "Rośnie razem z Tobą",
    body: "Czego nie umie dziś, dopisze sobie jutro — nowe narzędzie, test w izolacji, Twoja zgoda.",
  },
];

export default function Home() {
  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-5xl px-5 pt-24 pb-20 sm:px-6">
        {/* hero — editorial serif + the agent's voice in mono */}
        <section className="grid items-center gap-12 lg:grid-cols-[1.05fr_1fr] lg:gap-16">
          <div>
            <p className="font-mono text-[11px] tracking-[0.2em] text-ink-2 uppercase">
              open source · self-hosted ·{" "}
              <span className="text-indigo">wczesna wersja</span>
            </p>
            <h1 className="mt-5 font-heading text-[2.6rem] leading-[1.02] font-medium tracking-[-0.01em] text-balance sm:text-6xl">
              Agent, który nie
              <br />
              czeka, aż{" "}
              <em className="text-indigo italic">napiszesz</em>.
            </h1>
            <p className="mt-6 max-w-md text-[15px] leading-relaxed text-ink-2 sm:text-base">
              {PROJECT.name} mieszka na Twoim komputerze i sam pilnuje, załatwia
              i przypomina — a odzywa się dopiero, gdy ma coś wartościowego albo
              potrzebuje Twojej zgody.
            </p>
            <div className="mt-7 max-w-md">
              <CopyCommand />
            </div>
            <p className="mt-2.5 font-mono text-[11px] text-ink-2">
              jedna komenda · macOS / Linux · Python 3.11+ · v0.3 — działa,
              ale API może się jeszcze zmieniać
            </p>
          </div>

          {/* signature: the agent's loop, live */}
          <DecisionDemo />
        </section>

        {/* manifesto */}
        <section className="mt-24 max-w-3xl">
          <p className="font-heading text-2xl leading-snug font-medium text-balance sm:text-[2rem]">
            To agent z rękami: czyta skrzynkę, wchodzi na strony, a gdy czegoś
            nie umie — <span className="text-indigo">pisze sobie nowe narzędzie</span>.
            Ty wyznaczasz granice, on robi resztę.
          </p>
        </section>

        {/* differentiators — numbered, editorial */}
        <section className="mt-16 grid gap-x-10 gap-y-8 sm:grid-cols-2">
          {EDGES.map((e) => (
            <div key={e.k} className="flex gap-5">
              <span className="font-mono text-xs text-indigo">{e.k}</span>
              <div className="border-t border-hairline pt-0.5">
                <h2 className="font-heading text-lg font-medium text-ink">
                  {e.title}
                </h2>
                <p className="mt-1.5 text-sm leading-relaxed text-ink-2">
                  {e.body}
                </p>
              </div>
            </div>
          ))}
        </section>

        {/* privacy — quiet, clever */}
        <section className="mt-20 border-t border-hairline pt-8">
          <p className="max-w-2xl font-heading text-xl leading-snug font-medium text-balance">
            Mieszka u Ciebie, nie w cudzej chmurze.{" "}
            <span className="text-ink-2">
              Twoje maile, klucze i rozmowy nie trafiają do nikogo — nawet do
              nas. Bo nas tu nie ma: żadnego konta, żadnego serwera, nic nie
              dzwoni do domu.
            </span>
          </p>
        </section>

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
    </>
  );
}
