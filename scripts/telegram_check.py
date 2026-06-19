"""Skript B: Prueft ob Malte auf die Telegram-Freigabe geantwortet hat.

State-frei (Plan 03-03): kein lokaler Pending-State noetig. Der Draft liegt im
Repo (Quelle der Wahrheit), der Slug kommt aus der callback_data. getUpdates wird
EINMAL gepollt; jedes verarbeitete Update wird sofort per Offset (update_id+1)
bestaetigt -> keine Doppelverarbeitung zwischen zwei ephemeren Actions-Laeufen.

Approve (D-05/PUB-01):
  Draft-Inhalt lesen + in EINEM atomaren Commit (commit_files):
    - blog-[slug].html hinzufuegen
    - draft-[datum].html entfernen
  -> genau ein Commit auf main, ein Netlify-Deploy, kein Teil-Zustand.

Reject (D-06/PUB-02):
  draft-[datum].html per API loeschen (Single-File, delete_file).

Sicherheit (T-02-06): Nur callback_query von der eigenen TELEGRAM_CHAT_ID
wird verarbeitet — fremde Klicks werden ignoriert.

Aufruf:  python scripts/telegram_check.py
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ importierbar machen

from telegram_bot import get_updates, answer_callback_query, send_message, _load_secret
from github_api import commit_files, delete_file, get_text_file
from html_assembler import final_filename


def _do_approve(state: dict) -> str:
    """Approve-Pfad (D-05 + D-03 + D-09): Draft -> blog-[slug].html in EINEM atomaren Commit.

    Liest den Draft-Inhalt von main (get_text_file), dann ein einziger
    commit_files-Aufruf der gleichzeitig:
      - blog-[slug].html hinzufuegt (finaler Post)
      - draft-[datum].html entfernt
    Damit gibt es genau einen Commit und einen Netlify-Deploy — kein
    Teil-Zustand-Fenster, wenn ein zweiter Call fehlschlagen wuerde.

    Neu (04-04):
      - Extrahiert echten Titel via <h1>-Regex aus Draft-Inhalt (state["title"] = slug, L-05)
      - D-03-Reset: ersetzt noindex, nofollow durch index, follow im finalen Post-Content
      - Gibt extrahierten Titel zurueck (fuer Live-Link-Bestaetigungs-Nachricht in main())

    Hinweis: commit_files-Liste als erweiterbare Struktur belassen (04-06 fuegt Sitemap + Index ein).

    Returns:
        Echter Titel des Posts (aus <h1>), Fallback = state["slug"].
    """
    final = final_filename(state["slug"])
    draft = state["draft_filename"]

    print(f"  Approve: lese Draft '{draft}' von main ...")
    content = get_text_file(draft)

    # Titel aus Draft-HTML extrahieren (state["title"] traegt nur den Slug — L-05)
    m = re.search(r"<h1>(.*?)</h1>", content)
    title = html.unescape(m.group(1)) if m else state["slug"]

    # D-03-Reset: Draft ist noindex,nofollow (04-02); finaler Post muss index,follow sein
    content = content.replace(
        '<meta name="robots" content="noindex, nofollow" />',
        '<meta name="robots" content="index, follow" />',
        1,  # maxreplace=1 — nur den ersten Treffer (genau ein robots-Tag pro Seite)
    )

    print(f"  Approve: atomarer Commit ({draft} -> {final}) ...")
    commit_files(
        [
            # Finalen Post hinzufuegen / aktualisieren
            {"path": final, "content": content},
            # Draft entfernen (sha=None im Tree -> Datei geloescht)
            {"path": draft, "delete": True},
        ],
        f"Blogpost veroeffentlicht: {title}",
    )
    print(f"  Approve: '{final}' ist live, Draft entfernt.")
    return title


def _do_reject(state: dict) -> None:
    """Reject-Pfad (D-06): Draft loeschen (Single-File, bewusst einfach).

    Kein atomarer Multi-Datei-Bedarf — Reject entfernt nur eine Datei.
    """
    draft = state["draft_filename"]
    print(f"  Reject: loesche Draft '{draft}' ...")
    delete_file(draft, "Draft verworfen")
    print(f"  Reject: Draft entfernt, nichts geht live.")


def _find_draft_in_repo() -> "str | None":
    """Findet den neuesten draft-*.html im Repo via GitHub Contents-API.

    State-frei (Repo = Quelle der Wahrheit): listet das Repo-Root, filtert auf
    draft-*.html und gibt den alphabetisch letzten zurueck (= chronologisch, da
    der Dateiname YYYY-MM-DD traegt). Kein Treffer -> None.
    """
    import requests
    from github_api import _load_secret, _get_headers

    repo = _load_secret("GH_REPO")
    pat = _load_secret("GH_PAT")  # in Actions auf GITHUB_TOKEN gemappt (Plan 03-01)
    url = f"https://api.github.com/repos/{repo}/contents/"
    resp = requests.get(url, headers=_get_headers(pat), timeout=15)
    if not resp.ok:
        return None
    files = [
        f["name"]
        for f in resp.json()
        if f.get("type") == "file"
        and f["name"].startswith("draft-")
        and f["name"].endswith(".html")
    ]
    return sorted(files)[-1] if files else None


def main() -> None:
    # State-frei (Q1): kein read_pending mehr — der Draft liegt im Repo, der Slug
    # kommt aus callback_data. Offset-Bestaetigung (Q2) ersetzt den Pending-State.
    updates = get_updates(offset=0)
    if not updates:
        print("Keine Updates.")
        return

    # Akzeptanz-Filter (T-02-06 / T-03-07): nur die eigene Chat-ID.
    # str-Vergleich, da chat_id in Telegram-Objekten int oder str sein kann.
    own_chat_id = str(_load_secret("TELEGRAM_CHAT_ID"))

    for upd in updates:
        update_id = upd["update_id"]
        cq = upd.get("callback_query")
        if not cq:
            # Nicht-Callback (z.B. Text): bestaetigen und ueberspringen.
            get_updates(offset=update_id + 1)
            continue

        # chat_id unter cq["message"]["chat"]["id"] oder cq["from"]["id"] — beide
        # pruefen, damit der Filter auch bei editierten/geloeschten Nachrichten greift.
        msg_chat_id = str(cq.get("message", {}).get("chat", {}).get("id", ""))
        from_id = str(cq.get("from", {}).get("id", ""))
        if own_chat_id not in (msg_chat_id, from_id):
            print(f"  Fremde Chat-ID ({msg_chat_id or from_id}) — ignoriert (T-03-07).")
            get_updates(offset=update_id + 1)  # bestaetigen, nicht erneut holen
            continue

        data = cq.get("data", "")

        if data.startswith("approve:"):
            slug = data.split(":", 1)[1]
            draft = _find_draft_in_repo()
            if draft is None:
                print("Kein offener Draft im Repo gefunden.")
                get_updates(offset=update_id + 1)
                return
            title = _do_approve({"draft_filename": draft, "slug": slug, "title": slug})
            answer_callback_query(cq["id"], "Veroeffentlicht")
            # D-09: klickbarer Live-Link (Titel als Link-Text, HTML-escaped; NIE MarkdownV2)
            site_url = _load_secret("SITE_BASE_URL").rstrip("/")
            live_url = f"{site_url}/blog-{slug}.html"
            send_message(
                f'✅ Veroeffentlicht: <a href="{live_url}">{html.escape(title)}</a>',
                parse_mode="HTML",
            )
            get_updates(offset=update_id + 1)  # Q2: sofort bestaetigen = Persistenz
            return
        elif data.startswith("reject:"):
            slug = data.split(":", 1)[1]
            draft = _find_draft_in_repo()
            if draft:
                _do_reject({"draft_filename": draft})
            answer_callback_query(cq["id"], "Verworfen")
            send_message(f"\U0001f5d1 Verworfen: {slug}")
            get_updates(offset=update_id + 1)  # Q2: sofort bestaetigen = Persistenz
            return
        else:
            # Anderer/alter Callback — bestaetigen und ueberspringen.
            get_updates(offset=update_id + 1)
            continue

    print("Kein passendes Update gefunden.")


if __name__ == "__main__":
    main()
