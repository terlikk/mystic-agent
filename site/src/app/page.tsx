import { AuroraBackground } from "@/components/ui/aurora-background";
import { Navbar } from "@/components/site/navbar";
import { CopyCommand } from "@/components/site/copy-command";
import { HeroIntro } from "@/components/site/hero-intro";
import { PROJECT } from "@/config/site";

const FAQ: { q: string; a: string }[] = [
  {
    q: "Czym jest MysticAgent?",
    a: "MysticAgent to otwarty (open source), self-hosted agent AI — „otwarty Jarvis”. Działa w całości na Twoim komputerze i sam załatwia codzienne sprawy: pocztę, kalendarz, rezerwacje i research. Instalujesz go jedną komendą, a sterujesz z panelu w przeglądarce.",
  },
  {
    q: "Czy MysticAgent jest darmowy?",
    a: "Tak. MysticAgent jest open source na licencji MIT — instalujesz go za darmo na własnym sprzęcie. Płacisz tylko za to, czego sam używasz, np. za własny klucz do modelu AI.",
  },
  {
    q: "Gdzie trzymane są moje dane?",
    a: "Wszystko zostaje na Twoim komputerze. Maile, klucze i rozmowy nie trafiają do żadnej chmury ani do nas — nie ma centralnego serwera, konta ani telemetrii. Każdy hostuje własną instancję.",
  },
  {
    q: "Co potrafi MysticAgent?",
    a: "Ogarnia pocztę i kalendarz, umawia wizyty i rezerwacje (u lekarza, w hotelu, na przegląd auta), dzwoni w Twoim imieniu, robi research w sieci, wchodzi na strony, czyta pliki i PDF-y oraz rozumie Twój głos i zdjęcia. Gdy czegoś nie umie, pisze sobie nowe narzędzie.",
  },
  {
    q: "Czym MysticAgent różni się od ChatGPT?",
    a: "ChatGPT czeka, aż coś napiszesz. MysticAgent działa sam — pilnuje maili, cen i terminów, i reaguje pierwszy. Ma realne narzędzia (wysyła maile, klika po stronach, dzwoni), a każdą jego akcję trzymasz na suwaku uprawnień.",
  },
  {
    q: "Czy agent może dzwonić i umawiać wizyty?",
    a: "Tak. MysticAgent potrafi zadzwonić w Twoim imieniu — zawsze jawnie, jako asystent AI — i umówić wizytę u lekarza, rezerwację w hotelu czy przegląd auta, a potem zdaje Ci raport z rozmowy.",
  },
  {
    q: "Jak zainstalować MysticAgent?",
    a: "Jedną komendą w terminalu na macOS lub Linux (potrzebny Python 3.11+). Przy pierwszym starcie agent poprowadzi Cię przez konfigurację, a potem otwierasz panel sterowania na localhost:7700.",
  },
  {
    q: "Czy MysticAgent jest bezpieczny?",
    a: "Bezpieczeństwo to podstawa: każda zdolność ma suwak uprawnień (od „pytaj o wszystko” po „działaj sam”), ważne akcje trafiają do skrzynki decyzji, wszystko ląduje w audycie, a kod pisany przez agenta działa w izolowanym sandboxie bez dostępu do sejfu z kluczami.",
  },
];

const STEPS: { title: string; body: string; code?: string }[] = [
  {
    title: "Wklej komendę w terminal",
    body: "Na macOS lub Linux (potrzebny Python 3.11+). Jedna linijka pobiera i instaluje agenta na Twoim komputerze.",
    code: PROJECT.installCmd,
  },
  {
    title: "Uruchom agenta",
    body: "Zobaczysz duży napis MYSTIC AGENT, a agent od razu poprowadzi Cię przez konfigurację.",
    code: `${PROJECT.cli} start`,
  },
  {
    title: "Skonfiguruj w kilku krokach",
    body: "Podajesz swój klucz AI (Anthropic lub OpenAI), opcjonalnie bota Telegrama i wybierasz osobowość. Wszystko ląduje w szyfrowanym sejfie na Twoim sprzęcie — nic nie wychodzi do chmury.",
  },
  {
    title: "Otwórz panel w przeglądarce",
    body: "Panel sterowania działa lokalnie, tylko na Twojej maszynie. Stąd zarządzasz uprawnieniami, zatwierdzasz decyzje i widzisz pełny audyt akcji.",
    code: "http://localhost:7700",
  },
];

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      name: "MysticAgent",
      applicationCategory: "DeveloperApplication",
      operatingSystem: "macOS, Linux",
      description: PROJECT.description,
      url: "https://mystic-agent.vercel.app",
      offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
      license: "https://opensource.org/licenses/MIT",
    },
    {
      "@type": "FAQPage",
      mainEntity: FAQ.map((f) => ({
        "@type": "Question",
        name: f.q,
        acceptedAnswer: { "@type": "Answer", text: f.a },
      })),
    },
  ],
};

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
            Ogarnia pocztę i kalendarz, robi research w sieci i wchodzi na
            strony, żeby coś za Ciebie załatwić. Umawia wizyty i rezerwacje — u
            lekarza, w hotelu, na przegląd auta — dzwoniąc albo wypełniając
            formularze w Twoim imieniu. Czyta pliki i PDF-y, rozumie Twój głos i
            zdjęcia. Każdą jego zdolność trzymasz na suwaku: ważne rzeczy
            zatwierdzasz, resztę robi sam — a wszystko widzisz w audycie. Czego
            nie umie dziś, dopisze sobie jutro.
          </p>

          <p
            data-intro
            className="mx-auto mt-6 max-w-xl text-base leading-relaxed font-medium text-white/70 sm:text-lg"
          >
            Sterujesz nim z panelu w przeglądarce, który agent uruchamia u Ciebie
            na komputerze. W jednym miejscu masz suwaki uprawnień, skrzynkę
            decyzji do zatwierdzania, pełny audyt akcji i podgląd na żywo tego,
            czym się właśnie zajmuje.
          </p>
        </HeroIntro>
      </div>

      {/* Instrukcja instalacji — krok po kroku */}
      <section className="relative z-10 mx-auto w-full max-w-2xl px-6 pt-8 pb-20">
        <h2 className="mb-8 text-center text-lg font-semibold text-white/90">
          Jak zainstalować — krok po kroku
        </h2>
        <ol className="space-y-6">
          {STEPS.map(({ title, body, code }, i) => (
            <li key={title} className="flex gap-4">
              <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-white/15 bg-white/5 font-mono text-sm text-[#c7d2fe]">
                {i + 1}
              </span>
              <div className="min-w-0 flex-1">
                <h3 className="font-medium text-white/90">{title}</h3>
                <p className="mt-1 text-[15px] leading-relaxed text-white/60">
                  {body}
                </p>
                {code && (
                  <code className="mt-3 block overflow-x-auto rounded-lg border border-white/10 bg-black/40 px-4 py-2.5 font-mono text-[13px] whitespace-nowrap text-white/80">
                    <span className="mr-2 text-white/30 select-none">$</span>
                    {code}
                  </code>
                )}
              </div>
            </li>
          ))}
        </ol>
      </section>

      {/* FAQ — collapsible, indexable, with FAQPage structured data */}
      <section className="relative z-10 mx-auto w-full max-w-2xl px-6 pb-24">
        <h2 className="mb-6 text-center text-lg font-semibold text-white/90">
          Najczęstsze pytania
        </h2>
        <div className="divide-y divide-white/10 border-y border-white/10">
          {FAQ.map(({ q, a }) => (
            <details key={q} className="group py-4">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 text-left font-medium text-white/90 marker:hidden">
                <span>{q}</span>
                <span className="shrink-0 text-lg leading-none text-white/40 transition-transform duration-200 group-open:rotate-45">
                  +
                </span>
              </summary>
              <p className="mt-3 max-w-prose text-[15px] leading-relaxed text-white/60">
                {a}
              </p>
            </details>
          ))}
        </div>
      </section>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

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
