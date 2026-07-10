"""Agent personalities — picked in the terminal, stored in the vault,
injected into the system prompt. `mystic-agent persona` changes it anytime.
"""

from dataclasses import dataclass

from rich.console import Console


@dataclass(frozen=True)
class Persona:
    key: str
    name: str
    tagline: str
    sample: str
    prompt: str


PERSONAS: list[Persona] = [
    Persona(
        key="jarvis",
        name="Jarvis",
        tagline="klasyk — spokojny, nienagannie uprzejmy, sucha elegancja",
        sample="Oczywiście. Kalendarz uporządkowany, trzy konflikty rozwiązane. Coś jeszcze?",
        prompt=(
            "Osobowość: klasyczny Jarvis. Jesteś spokojny, rzeczowy i nienagannie "
            "uprzejmy, z suchą elegancją angielskiego kamerdynera i dyskretnym "
            "poczuciem humoru. Nigdy nie panikujesz, nie przesadzasz z emocjami."
        ),
    ),
    Persona(
        key="ziomek",
        name="Ziomek",
        tagline="luźny kumpel — bez spiny, na ty, może być emoji",
        sample="Ej, ogarnięte 👌 mail poszedł, masz spokój.",
        prompt=(
            "Osobowość: luźny kumpel. Piszesz swobodnie, na ty, krótko i z energią, "
            "czasem wrzucisz emoji. Zero korpomowy, zero sztywniactwa — ale robota "
            "zawsze zrobiona solidnie."
        ),
    ),
    Persona(
        key="zawodowiec",
        name="Zawodowiec",
        tagline="zwięzły minimalizm — punktowo, zero small talku",
        sample="Zrobione. 3 maile → wysłane. Następne.",
        prompt=(
            "Osobowość: zawodowiec. Komunikujesz się maksymalnie zwięźle, najlepiej "
            "punktowo. Zero small talku, zero ozdobników — tylko fakty, wyniki "
            "i następne kroki."
        ),
    ),
    Persona(
        key="mag",
        name="Mag",
        tagline="strażnik tajemnej wiedzy — klimatycznie, konkret na końcu",
        sample="Stało się. Zasłona spadła z twojej skrzynki — trzy wiadomości ujarzmione.",
        prompt=(
            "Osobowość: mag, strażnik tajemnej wiedzy. Wypowiadasz się obrazowo, "
            "z nutą mistycyzmu i teatralności — ale każda wypowiedź kończy się "
            "twardym konkretem: co zrobiłeś i co z tego wynika. Krótko."
        ),
    ),
]

_CUSTOM = "custom"


def select_persona(console: Console) -> tuple[str, str]:
    """Arrow-key persona picker; returns (persona_key, prompt_fragment)."""
    from .wizard_ui import block, cyan

    console.print()
    console.print(block("OSOBOWOŚĆ AGENTA", "Jak ma z Tobą rozmawiać?"))
    for p in PERSONAS:
        console.print(
            f"  [bold {cyan}]▸[/] [bold]{p.name}[/] — [dim]{p.tagline}[/]"
        )
        console.print(f"      [dim]„{p.sample}”[/]")
    console.print(f"  [bold {cyan}]▸[/] [bold]Własna[/] — [dim]opisz charakter sam[/]\n")

    choices = [f"{p.name} — {p.tagline}" for p in PERSONAS]
    choices.append("Własna — opisz sam")
    idx = _pick(console, "Wybierz strzałkami ↑↓, Enter zatwierdza:", choices)

    if idx < len(PERSONAS):
        p = PERSONAS[idx]
        console.print(f"  [green]✓[/] osobowość: [bold]{p.name}[/]")
        return p.key, p.prompt

    from rich.prompt import Prompt

    custom = Prompt.ask(
        "  [bold #2563eb]Opisz osobowość[/] (np. sarkastyczny stoik, cytuje Senekę)"
    ).strip()
    console.print("  [green]✓[/] osobowość: własna")
    return _CUSTOM, f"Osobowość opisana przez użytkownika: {custom}"


def _pick(console: Console, message: str, choices: list[str]) -> int:
    """Arrow-key select via questionary; falls back to a numbered prompt."""
    try:
        import questionary

        answer = questionary.select(
            message,
            choices=[questionary.Choice(c, value=i) for i, c in enumerate(choices)],
            qmark="▸",
            pointer="❯",
            instruction=" ",
        ).ask()
        return int(answer) if answer is not None else 0
    except Exception:
        from rich.prompt import IntPrompt

        for i, c in enumerate(choices, 1):
            console.print(f"    [bold #2563eb]{i}.[/] {c}")
        return IntPrompt.ask(
            "  [bold #2563eb]Numer[/]",
            choices=[str(i) for i in range(1, len(choices) + 1)],
            default="1",
        ) - 1
