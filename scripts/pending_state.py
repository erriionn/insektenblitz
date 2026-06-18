"""Lesen und Schreiben des Pending-State (.telegram-pending.json).

State-Felder (D-08):
  - draft_filename : str   — Dateiname des Drafts (z.B. "draft-2026-06-18.html")
  - slug           : str   — URL-Slug des Posts
  - title          : str   — Titel des Posts
  - message_id     : int   — Telegram message_id der gesendeten Vorschau-Nachricht
  - offset         : int   — letzter getUpdates-Offset (Doppelverarbeitung verhindern)

Die Datei liegt im Repo-Root und ist via .gitignore ignoriert (nie ins oeffentliche Repo).
"""
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = REPO_ROOT / ".telegram-pending.json"


def write_pending(state: dict) -> None:
    """Schreibt den Pending-State in .telegram-pending.json.

    Args:
        state: Dict mit den D-08-Feldern (draft_filename, slug, title,
               message_id, offset).
    """
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_pending() -> "dict | None":
    """Liest den Pending-State aus .telegram-pending.json.

    Returns:
        State-Dict oder None wenn keine Datei vorhanden.
    """
    if not STATE_FILE.exists():
        return None
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def clear_pending() -> None:
    """Loescht .telegram-pending.json (nach Approve oder Reject in Plan 02).

    Kein Fehler wenn Datei nicht existiert.
    """
    if STATE_FILE.exists():
        STATE_FILE.unlink()
