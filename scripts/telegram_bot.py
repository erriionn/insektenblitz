"""Telegram-API Hilfsfunktionen fuer die Content-Maschine.

Stellt Funktionen bereit:
  - send_draft_message  : Vorschau-Nachricht mit Approve/Reject-Buttons senden
  - get_updates         : getUpdates einmal pollen (fuer Skript B / Plan 02)
  - answer_callback_query : Lade-Symbol nach Button-Klick entfernen (Plan 02)

Secrets (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID) werden aus der Umgebung / .env geladen.
Bot-Token erscheint nur in der URL, nie in print-Ausgaben oder Fehlermeldungen.
"""
import os
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
TELEGRAM_API = "https://api.telegram.org/bot{token}/{method}"


def _load_secret(key_name: str) -> str:
    """Laedt einen Secret-Wert: erst os.environ, dann .env-Datei, sonst sys.exit."""
    val = os.environ.get(key_name)
    if val:
        return val
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for raw in env_file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            if name.strip() == key_name:
                return value.strip().strip('"').strip("'")
    sys.exit(f"{key_name} fehlt — bitte in .env setzen (siehe .env.example).")


def send_draft_message(
    draft_filename: str,
    slug: str,
    title: str,
    meta_desc: str = "",
) -> dict:
    """Schickt Approve/Reject-Vorschau-Nachricht an TELEGRAM_CHAT_ID.

    Nachricht enthaelt Titel, Vorschau-Link und zwei Inline-Buttons.
    callback_data traegt Aktion + Slug: "approve:{slug}" / "reject:{slug}".

    Args:
        draft_filename: Dateiname des Drafts (z.B. "draft-2026-06-18.html").
        slug:           URL-Slug des Posts (z.B. "eps-bekampfung-2026").
        title:          Titel des Posts.
        meta_desc:      Optionale Kurzbeschreibung fuer den Nachrichtentext.

    Returns:
        result-dict aus der Telegram-API-Antwort (enthaelt u.a. message_id).

    Raises:
        SystemExit bei HTTP-Fehler oder Telegram-API-Fehler (kritisch).
    """
    token = _load_secret("TELEGRAM_BOT_TOKEN")
    chat_id = _load_secret("TELEGRAM_CHAT_ID")

    base = os.environ.get("SITE_BASE_URL", "https://insektenblitz.com").rstrip("/")
    preview_url = f"{base}/{draft_filename}"

    lines = [
        f"<b>{title}</b>",
        "",
        f"Vorschau: {preview_url}",
    ]
    if meta_desc:
        lines += ["", meta_desc]

    text = "\n".join(lines)

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "Freigeben", "callback_data": f"approve:{slug}"},
                {"text": "Verwerfen", "callback_data": f"reject:{slug}"},
            ]
        ]
    }

    url = TELEGRAM_API.format(token=token, method="sendMessage")
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": reply_markup,
    }

    resp = requests.post(url, json=payload, timeout=15)
    # Kein raise_for_status() hier: das wuerde die nackte HTTPError MIT der
    # Token-URL werfen (Secret-Leak) und Telegrams Klartext-Grund verschlucken.
    # Stattdessen den JSON-Body lesen und "description" ausgeben — ohne Token/URL.
    try:
        data = resp.json()
    except ValueError:
        sys.exit(f"Telegram API Fehler: HTTP {resp.status_code} (keine JSON-Antwort)")
    if not data.get("ok"):
        sys.exit(f"Telegram API Fehler: HTTP {resp.status_code} — {data.get('description')}")
    return data["result"]


def get_updates(offset: int = 0) -> list:
    """Pollt getUpdates einmal und gibt Liste von Update-Objekten zurueck.

    Wird von Skript B (telegram_check.py, Plan 02) verwendet.
    Bei Fehler: tolerant (print + leere Liste) — kein Update ist ok,
    naechster Cron-Run holt nach.

    Args:
        offset: Update-ID-Offset (verhindert Doppelverarbeitung).

    Returns:
        Liste von Update-Dicts (kann leer sein).
    """
    token = _load_secret("TELEGRAM_BOT_TOKEN")
    url = TELEGRAM_API.format(token=token, method="getUpdates")
    try:
        resp = requests.get(url, params={"offset": offset, "timeout": 1}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            print(f"  getUpdates: Telegram-Fehler: {data.get('description')}")
            return []
        return data.get("result", [])
    except Exception as e:  # noqa: BLE001 — Polling-Fehler darf Lauf nicht abbrechen
        print(f"  getUpdates fehlgeschlagen: {e}")
        return []


def answer_callback_query(callback_query_id: str, text: str = "") -> None:
    """Beantwortet einen Callback-Query (entfernt das Lade-Symbol nach Button-Klick).

    Wird von Skript B (Plan 02) nach Approve/Reject aufgerufen.
    Bei Fehler: tolerant (nur print) — Lade-Symbol ist kosmetisch.

    Args:
        callback_query_id: ID aus dem callback_query-Objekt.
        text:              Optionaler kurzer Bestaetigungs-Text.
    """
    token = _load_secret("TELEGRAM_BOT_TOKEN")
    url = TELEGRAM_API.format(token=token, method="answerCallbackQuery")
    try:
        resp = requests.post(
            url,
            json={"callback_query_id": callback_query_id, "text": text},
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as e:  # noqa: BLE001 — kosmetisch, kein Abbruch
        print(f"  answerCallbackQuery fehlgeschlagen: {e}")
