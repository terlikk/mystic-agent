"""E-mail skill: IMAP for reading, SMTP for sending.

Works with a regular mailbox + app password (Gmail: włącz 2FA →
myaccount.google.com/apppasswords). Sending defaults to the "propose"
permission level, so nothing leaves without the owner's approval.
"""

import asyncio
import email
import imaplib
import smtplib
from email.header import decode_header, make_header
from email.mime.text import MIMEText
from typing import Any

from .tools import Tool


def derive_hosts(address: str) -> tuple[str, str]:
    """Best-guess IMAP/SMTP hosts from the address domain."""
    domain = address.rsplit("@", 1)[-1].lower()
    if domain in ("gmail.com", "googlemail.com"):
        return "imap.gmail.com", "smtp.gmail.com"
    if domain in ("outlook.com", "hotmail.com", "live.com"):
        return "outlook.office365.com", "smtp-mail.outlook.com"
    return f"imap.{domain}", f"smtp.{domain}"


def _decode(value: str | None) -> str:
    if not value:
        return ""
    return str(make_header(decode_header(value)))


def _body_text(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(
                        part.get_content_charset() or "utf-8", "replace"
                    )
        return "(brak części tekstowej)"
    payload = msg.get_payload(decode=True)
    if payload:
        return payload.decode(msg.get_content_charset() or "utf-8", "replace")
    return ""


class Mailbox:
    def __init__(
        self, address: str, password: str, imap_host: str, smtp_host: str
    ) -> None:
        self.address = address
        self.password = password
        self.imap_host = imap_host
        self.smtp_host = smtp_host

    # sync internals, wrapped with asyncio.to_thread by the tools

    def unread(self, limit: int = 5) -> str:
        with imaplib.IMAP4_SSL(self.imap_host) as imap:
            imap.login(self.address, self.password)
            imap.select("INBOX", readonly=True)
            _, data = imap.search(None, "UNSEEN")
            uids = data[0].split()
            if not uids:
                return "brak nieprzeczytanych maili"
            lines = []
            for uid in uids[-limit:][::-1]:
                _, msg_data = imap.fetch(
                    uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])"
                )
                msg = email.message_from_bytes(msg_data[0][1])
                lines.append(
                    f"[{uid.decode()}] od: {_decode(msg['From'])}"
                    f" · temat: {_decode(msg['Subject'])}"
                )
            more = len(uids) - len(lines)
            if more > 0:
                lines.append(f"… i jeszcze {more} starszych nieprzeczytanych")
            return "\n".join(lines)

    def read(self, uid: str) -> str:
        with imaplib.IMAP4_SSL(self.imap_host) as imap:
            imap.login(self.address, self.password)
            imap.select("INBOX", readonly=True)
            _, msg_data = imap.fetch(uid.encode(), "(BODY.PEEK[])")
            if not msg_data or msg_data[0] is None:
                return f"nie znalazłem maila o id {uid}"
            msg = email.message_from_bytes(msg_data[0][1])
            body = _body_text(msg).strip()
            return (
                f"od: {_decode(msg['From'])}\n"
                f"temat: {_decode(msg['Subject'])}\n"
                f"data: {_decode(msg['Date'])}\n\n{body[:3000]}"
            )

    def send(self, to: str, subject: str, body: str) -> str:
        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = self.address
        msg["To"] = to
        msg["Subject"] = subject
        try:
            with smtplib.SMTP_SSL(self.smtp_host, 465, timeout=20) as smtp:
                smtp.login(self.address, self.password)
                smtp.send_message(msg)
        except (OSError, smtplib.SMTPException):
            with smtplib.SMTP(self.smtp_host, 587, timeout=20) as smtp:
                smtp.starttls()
                smtp.login(self.address, self.password)
                smtp.send_message(msg)
        return f"wysłano maila do {to} (temat: {subject})"


def email_tools(mailbox: Mailbox) -> list[Tool]:
    async def check_email(args: dict[str, Any]) -> str:
        limit = int(args.get("limit", 5))
        return await asyncio.to_thread(mailbox.unread, limit)

    async def read_email(args: dict[str, Any]) -> str:
        return await asyncio.to_thread(mailbox.read, str(args.get("id", "")))

    async def send_email(args: dict[str, Any]) -> str:
        return await asyncio.to_thread(
            mailbox.send,
            str(args.get("to", "")),
            str(args.get("subject", "")),
            str(args.get("body", "")),
        )

    return [
        Tool(
            name="check_email",
            capability="email_read",
            description="Sprawdza nieprzeczytane maile w skrzynce użytkownika"
            " (nadawca + temat).",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Ile maksymalnie"}
                },
            },
            func=check_email,
        ),
        Tool(
            name="read_email",
            capability="email_read",
            description="Czyta treść konkretnego maila po id z check_email.",
            parameters={
                "type": "object",
                "properties": {
                    "id": {"type": "string", "description": "Id maila"}
                },
                "required": ["id"],
            },
            func=read_email,
        ),
        Tool(
            name="send_email",
            capability="email_send",
            description="Wysyła maila z konta użytkownika (też jako odpowiedź"
            " — daj 'Re: temat').",
            parameters={
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Adresat"},
                    "subject": {"type": "string", "description": "Temat"},
                    "body": {"type": "string", "description": "Treść"},
                },
                "required": ["to", "subject", "body"],
            },
            func=send_email,
        ),
    ]
