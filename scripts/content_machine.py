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
from html_assembler import assemble_draft, resolve_hero
from github_api import push_file
from telegram_bot import send_draft_message, send_post_text, send_message
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

    try:
        post = generate_post(hits)
        print(f"  Titel: {post.get('title')}")

        # Pre-flight: callback_data "approve:{slug}" und "reject:{slug}" muessen
        # <= 64 Byte (UTF-8) bleiben — sonst lehnt Telegram den Button still ab.
        # _slugify kappt auf 50 Z. (= 58 Byte mit "approve:"); der Check faengt
        # Randfaelle ab, in denen ein Kollisions-Suffix die Grenze ueberschreitet.
        slug = post["slug"]
        for prefix in ("approve:", "reject:"):
            if len((prefix + slug).encode("utf-8")) > 64:
                sys.exit(
                    f"Slug zu lang fuer Telegram callback_data (>64 Byte): {slug}"
                )

        hero_image = resolve_hero(post.get("hero_keyword", ""))
        draft_path = assemble_draft(post, hero_image=hero_image)
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

        # D-12: Health-Ping — nur beim daily-content-Lauf (content_machine.main())
        # post-approval-Lauf ruft telegram_check.py auf, NICHT main() — bleibt ping-frei.
        n_hits = len(hits) if not (hits and hits[0].get("evergreen")) else 0
        send_message(f"Lauf OK — {n_hits} Treffer, Post: {post['title'][:60]}")

    except Exception as exc:
        try:
            send_message(
                f"FEHLER im Generierungslauf: {type(exc).__name__}: {str(exc)[:200]}"
            )
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
