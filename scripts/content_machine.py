"""Orchestrator der Content-Maschine — Skript A.

Phase 2: collect_hits -> generate -> assemble_draft -> Draft via GitHub-API auf main pushen
-> Telegram-Vorschau mit Approve/Reject-Buttons senden -> Pending-State schreiben.

Die Antwort-Auswertung (Approve/Reject) folgt in Plan 02 (telegram_check.py — Skript B).
Aufruf:  python scripts/content_machine.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ importierbar machen

from news_scraper import collect_hits, forced_evergreen_hit
from content_generator import generate_post
from html_assembler import assemble_draft
from github_api import push_file
from telegram_bot import send_draft_message, send_post_text
from pending_state import write_pending


def main() -> None:
    # Demo-Themensteuerung: workflow_dispatch-Input 'thema' (via env INPUT_THEMA)
    # erzwingt ein Evergreen-Thema; leer = normaler aktueller News-Lauf.
    thema = os.environ.get("INPUT_THEMA", "").strip()
    if thema:
        hits = forced_evergreen_hit(thema)
        print("Erzwungenes Thema:", thema)
    else:
        hits = collect_hits()
    if hits and hits[0].get("evergreen"):
        print("Keine aktuellen Treffer — Evergreen-Thema:", hits[0]["title"])
    else:
        print(f"{len(hits)} Treffer (Google News + Reddit, 24-48h) — generiere Post mit Claude ...")

    post = generate_post(hits)
    print(f"  Titel: {post.get('title')}")

    draft_path = assemble_draft(post)
    name = Path(draft_path).name  # "draft-YYYY-MM-DD.html"

    # Schritt 1: Draft via GitHub Contents-API auf main pushen (Single-File-Push)
    # Netlify deployt automatisch -> Draft ist als {SITE_BASE_URL}/{name} erreichbar
    print(f"\nPushe Draft auf main: {name} ...")
    push_file(name, Path(draft_path).read_bytes(), f"Draft-Vorschau: {post['title']}")

    # Schritt 2a: Volltext zum Korrekturlesen senden (reiner Text, ggf. gesplittet)
    print("Sende Volltext zum Korrekturlesen ...")
    send_post_text(post)

    # Schritt 2b: Telegram-Vorschau mit Approve/Reject-Buttons senden
    print("Sende Telegram-Vorschau ...")
    result = send_draft_message(name, post["slug"], post["title"], post.get("meta_description", ""))

    # Schritt 3: Pending-State fuer Skript B (telegram_check.py) speichern
    write_pending({
        "draft_filename": name,
        "slug": post["slug"],
        "title": post["title"],
        "message_id": result["message_id"],
        "offset": 0,
    })

    print("\nDraft gepusht + Telegram gesendet.")
    print(f"  Titel:    {post['title']}")
    print(f"  Draft:    {name}")
    print(f"  Pending:  .telegram-pending.json (message_id={result['message_id']})")
    print("\nNaechster Schritt: python scripts/telegram_check.py (Plan 02) ausfuehren,")
    print("um die Antwort auszuwerten (Approve -> live / Reject -> loeschen).")


if __name__ == "__main__":
    main()
