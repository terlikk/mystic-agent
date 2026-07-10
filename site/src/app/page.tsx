import { Navbar } from "@/components/site/navbar";
import { CopyCommand } from "@/components/site/copy-command";
import { PROJECT } from "@/config/site";

const EDGES = [
  {
    title: "Produkt, nie framework",
    body: "Instalacja jedną komendą, reszta w przejrzystym panelu w przeglądarce. Zero plików konfiguracyjnych.",
  },
  {
    title: "Ty trzymasz smycz",
    body: "Każda zdolność ma suwak — od „pytaj o wszystko” po „działaj sam”. Ważne rzeczy zatwierdzasz, resztę robi bez pytania.",
  },
  {
    title: "Sam z siebie",
    body: "Pilnuje maili, cen i terminów, reaguje pierwszy — nie czeka na komendę.",
  },
  {
    title: "Uczy się w locie",
    body: "Gdy czegoś nie umie, pisze sobie nowe narzędzie, testuje je w sandboxie i pyta Cię o zgodę.",
  },
];

const SKILLS = [
  "Poczta", "Kalendarz", "Notatki", "Zadania", "Kontakty", "Przypomnienia",
  "Research w sieci", "Przeglądarka", "Pliki i PDF", "Terminal",
  "Pamięć długotrwała", "Płatności z limitem",
];

export default function Home() {
  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-3xl px-5 pt-24 pb-16 sm:px-6">
        {/* hero — install command is the centerpiece */}
        <section className="text-center">
          <p className="inline-flex items-center gap-2 rounded-full bg-fill px-3 py-1 text-[11px] font-medium text-ink-2">
            <span className="pulse-soft size-1.5 rounded-full bg-violet" />
            Open source · Self-hosted · W budowie
          </p>
          <h1 className="mt-5 text-3xl font-semibold tracking-tight text-balance sm:text-4xl">
            Twój Jarvis. Twój serwer.{" "}
            <span className="text-gradient">Twoje zasady.</span>
          </h1>
          <p className="mx-auto mt-3 max-w-md text-sm text-ink-2 sm:text-base">
            Osobisty agent AI, który mieszka na Twoim komputerze i sam załatwia
            sprawy. Postaw go u siebie jedną komendą:
          </p>
          <div className="mx-auto mt-6 max-w-xl">
            <CopyCommand />
          </div>
          <p className="mt-2.5 text-[11px] text-ink-2">
            macOS / Linux · Python 3.11+ · Twoje dane zostają u Ciebie
          </p>
        </section>

        {/* differentiators — compact, small type */}
        <section className="mt-14 grid gap-3 sm:grid-cols-2">
          {EDGES.map((e) => (
            <div key={e.title} className="rounded-2xl bg-fill p-4">
              <h2 className="text-sm font-semibold text-ink">{e.title}</h2>
              <p className="mt-1 text-[13px] leading-relaxed text-ink-2">
                {e.body}
              </p>
            </div>
          ))}
        </section>

        {/* capabilities — one tight row of chips */}
        <section className="mt-8">
          <h2 className="text-[11px] font-semibold tracking-[0.14em] text-ink-2 uppercase">
            Co potrafi
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
            …a czego nie ma, dopisuje sobie sam.
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
