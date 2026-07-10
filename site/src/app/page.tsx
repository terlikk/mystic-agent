import { Navbar } from "@/components/site/navbar";
import { CopyCommand } from "@/components/site/copy-command";
import { PROJECT } from "@/config/site";

const EDGES = [
  {
    title: "Ma ręce, nie tylko język",
    body: "Nie odpowiada — działa. Wysyła maile, rezerwuje, wchodzi na strony i klika za Ciebie. Czat to dopiero początek rozmowy, nie jej koniec.",
  },
  {
    title: "Pracuje, gdy Ciebie nie ma",
    body: "Żyje na strumieniu zdarzeń: przyszedł mail, spadła cena, zbliża się termin. Reaguje pierwszy — zanim zdążysz zauważyć, że był problem.",
  },
  {
    title: "Autonomia na Twoich zasadach",
    body: "Każda zdolność ma suwak: od „pytaj o wszystko” po „działaj sam i nie zawracaj głowy”. A każdy ruch ląduje w audycie — zawsze wiesz, co i dlaczego zrobił.",
  },
  {
    title: "Rośnie razem z Tobą",
    body: "Czego nie umie dziś, dopisze sobie jutro: pisze własne narzędzie, testuje je w izolacji i pyta Cię o zgodę. Im dłużej go masz, tym więcej potrafi.",
  },
];

const SCENARIOS = [
  "Odpisz temu klientowi, a resztę maili posegreguj.",
  "Kup tę kartę graficzną, jak cena spadnie poniżej 300 zł.",
  "Zarezerwuj stolik na sobotę i wrzuć do kalendarza.",
  "Streść mi tę umowę i wypisz, na co uważać.",
  "Przypomnij o fakturze i wyślij ją w piątek rano.",
];

const SKILLS = [
  "Poczta", "Kalendarz", "Notatki", "Zadania", "Kontakty", "Przypomnienia",
  "Research w sieci", "Przeglądarka", "Śledzenie paczek", "Pliki i PDF",
  "Głos i zdjęcia", "Pamięć długotrwała", "Płatności z limitem", "Terminal",
];

export default function Home() {
  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-3xl px-5 pt-24 pb-16 sm:px-6">
        {/* hero */}
        <section className="text-center">
          <p className="inline-flex items-center gap-2 rounded-full bg-fill px-3 py-1 text-[11px] font-medium text-ink-2">
            <span className="pulse-soft size-1.5 rounded-full bg-violet" />
            Open source · Self-hosted · W budowie
          </p>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
            Twój Jarvis. Twój serwer.{" "}
            <span className="text-gradient">Twoje zasady.</span>
          </h1>
          <p className="mx-auto mt-4 max-w-lg text-sm leading-relaxed text-ink-2 sm:text-base">
            Nie kolejny czat, który czeka, aż coś napiszesz. Agent, który sam
            pilnuje, załatwia i przypomina — a odzywa się dopiero, gdy ma coś
            wartościowego albo potrzebuje Twojej zgody.
          </p>
          <div className="mx-auto mt-6 max-w-xl">
            <CopyCommand />
          </div>
          <p className="mt-2.5 text-[11px] text-ink-2">
            Jedna komenda · macOS / Linux · Python 3.11+
          </p>
        </section>

        {/* manifesto */}
        <section className="mt-14 text-center">
          <p className="mx-auto max-w-2xl text-lg leading-snug font-medium text-balance text-ink sm:text-xl">
            To agent z rękami: czyta skrzynkę, wchodzi na strony, wypełnia
            formularze, a gdy czegoś nie umie — pisze sobie nowe narzędzie.{" "}
            <span className="text-ink-2">
              Ty wyznaczasz granice, on robi resztę.
            </span>
          </p>
        </section>

        {/* differentiators */}
        <section className="mt-12 grid gap-3 sm:grid-cols-2">
          {EDGES.map((e) => (
            <div key={e.title} className="rounded-2xl bg-fill p-5">
              <h2 className="text-sm font-semibold text-ink">{e.title}</h2>
              <p className="mt-1.5 text-[13px] leading-relaxed text-ink-2">
                {e.body}
              </p>
            </div>
          ))}
        </section>

        {/* scenarios — talk to it like a person */}
        <section className="mt-12">
          <h2 className="text-[11px] font-semibold tracking-[0.14em] text-ink-2 uppercase">
            Powiedz mu po ludzku
          </h2>
          <ul className="mt-4 space-y-2">
            {SCENARIOS.map((s) => (
              <li
                key={s}
                className="flex items-start gap-3 rounded-xl bg-fill px-4 py-3 text-[14px] text-ink"
              >
                <span className="mt-0.5 select-none text-blue">›</span>
                <span>„{s}”</span>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-[13px] text-ink-2">
            Wkrótce także: „Zadzwoń i umów przegląd auta” — jawnie, jako Twój
            asystent.
          </p>
        </section>

        {/* capabilities */}
        <section className="mt-12">
          <h2 className="text-[11px] font-semibold tracking-[0.14em] text-ink-2 uppercase">
            Co ma pod ręką
          </h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {SKILLS.map((s) => (
              <span
                key={s}
                className="rounded-full border border-hairline px-3 py-1 text-[13px] text-ink"
              >
                {s}
              </span>
            ))}
          </div>
          <p className="mt-3 text-[13px] text-ink-2">
            …a czego nie ma na liście, dopisuje sobie sam.
          </p>
        </section>

        {/* the quiet part — privacy without the cliché */}
        <section className="mt-12 rounded-2xl border border-hairline p-5">
          <h2 className="text-sm font-semibold text-ink">
            Mieszka u Ciebie, nie w cudzej chmurze
          </h2>
          <p className="mt-1.5 text-[13px] leading-relaxed text-ink-2">
            Twoje maile, klucze i rozmowy nie trafiają do nikogo — nawet do nas.
            Bo nas tu nie ma: żadnego konta, żadnego centralnego serwera, nic nie
            dzwoni do domu. Każdy uruchamia własnego agenta, na własnym sprzęcie.
          </p>
        </section>

        {/* footer */}
        <footer className="mt-14 flex items-center justify-between border-t border-hairline/60 pt-6 text-xs text-ink-2">
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
