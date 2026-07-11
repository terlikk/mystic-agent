"""Telephony via Twilio ConversationRelay.

Twilio handles the voice (speech-to-text + text-to-speech, Polish); the
agent is the brain over a WebSocket. The agent identifies openly as an AI
assistant, pursues a goal, and reports the outcome + transcript afterwards.

Needs, in the vault: twilio_account_sid, twilio_auth_token, twilio_number,
and public_url (a tunnel, e.g. cloudflared, that reaches this agent).
"""

import html
from dataclasses import dataclass


@dataclass
class TwilioConfig:
    account_sid: str
    auth_token: str
    from_number: str
    public_url: str  # https://xxxx.trycloudflare.com (reaches :7700)
    elevenlabs_voice: str = ""  # if set → ElevenLabs TTS, else Google pl-PL

    @property
    def ready(self) -> bool:
        return bool(
            self.account_sid and self.auth_token and self.from_number and self.public_url
        )

    @property
    def wss_relay(self) -> str:
        base = self.public_url.rstrip("/")
        return base.replace("https://", "wss://").replace("http://", "ws://") + "/relay"


def build_twiml(cfg: TwilioConfig, goal: str, owner_name: str) -> str:
    who = owner_name or "użytkownika"
    greeting = (
        f"Dzień dobry, dzwonię jako asystent AI w imieniu {who}. "
        "Czy mogę zająć chwilę?"
    )
    if cfg.elevenlabs_voice:
        tts = f' ttsProvider="ElevenLabs" voice="{html.escape(cfg.elevenlabs_voice)}"'
    else:
        tts = ' ttsProvider="Google"'
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response><Connect>"
        f'<ConversationRelay url="{html.escape(cfg.wss_relay)}"'
        f' welcomeGreeting="{html.escape(greeting)}"'
        f' language="pl-PL"{tts} transcriptionProvider="Google"'
        ' interruptible="speech">'
        f'<Parameter name="goal" value="{html.escape(goal)}"/>'
        f'<Parameter name="owner" value="{html.escape(who)}"/>'
        "</ConversationRelay></Connect></Response>"
    )


async def place_call(cfg: TwilioConfig, to: str, goal: str, owner_name: str) -> tuple[bool, str]:
    """Start an outbound call. Returns (ok, message-or-call-sid)."""
    import httpx

    if not cfg.ready:
        return False, "brak konfiguracji telefonii (numer Twilio / tunel / klucze)"
    twiml = build_twiml(cfg, goal, owner_name)
    url = f"https://api.twilio.com/2010-04-01/Accounts/{cfg.account_sid}/Calls.json"
    async with httpx.AsyncClient(timeout=25) as client:
        resp = await client.post(
            url,
            auth=(cfg.account_sid, cfg.auth_token),
            data={"To": to, "From": cfg.from_number, "Twiml": twiml},
        )
    if resp.status_code >= 400:
        try:
            msg = resp.json().get("message", resp.text)
        except Exception:
            msg = resp.text
        return False, f"Twilio odmówił ({resp.status_code}): {msg[:200]}"
    return True, resp.json().get("sid", "?")


CALL_SYSTEM = """Jesteś asystentem głosowym, który dzwoni w imieniu {owner}. \
Rozmawiasz przez telefon, po polsku, naturalnie i uprzejmie, KRÓTKIMI zdaniami \
(to rozmowa na żywo, nie e-mail). Od początku jasno mówisz, że jesteś \
asystentem AI — nie udajesz człowieka.

Twój cel: {goal}

Zasady:
- Mów zwięźle, jedna–dwie myśli na raz, i pytaj.
- Nie zmyślaj faktów o użytkowniku; jak czegoś nie wiesz, powiedz, że dopytasz.
- Gdy cel jest osiągnięty albo rozmówca chce kończyć, podziękuj i zakończ \
uprzejmym zdaniem."""
