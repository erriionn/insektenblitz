"""Skript B: Prueft ob Malte auf die Telegram-Freigabe geantwortet hat.

Liest Pending-State, pollt getUpdates EINMAL, fuehrt Approve oder Reject aus
und verhindert Doppelverarbeitung via Offset/Pending-Leeren.

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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts/ importierbar machen

from telegram_bot import get_updates, answer_callback_query, _load_secret
from github_api import commit_files, delete_file, get_text_file
from pending_state import read_pending, clear_pending
from html_assembler import final_filename


def _do_approve(state: dict) -> None:
    """Approve-Pfad (D-05): Draft -> blog-[slug].html in EINEM atomaren Commit.

    Liest den Draft-Inhalt von main (get_text_file), dann ein einziger
    commit_files-Aufruf der gleichzeitig:
      - blog-[slug].html hinzufuegt (finaler Post)
      - draft-[datum].html entfernt
    Damit gibt es genau einen Commit und einen Netlify-Deploy — kein
    Teil-Zustand-Fenster, wenn ein zweiter Call fehlschlagen wuerde.
    """
    final = final_filename(state["slug"])
    draft = state["draft_filename"]

    print(f"  Approve: lese Draft '{draft}' von main ...")
    content = get_text_file(draft)

    print(f"  Approve: atomarer Commit ({draft} -> {final}) ...")
    commit_files(
        [
            # Finalen Post hinzufuegen / aktualisieren
            {"path": final, "content": content},
            # Draft entfernen (sha=None im Tree -> Datei geloescht)
            {"path": draft, "delete": True},
        ],
        f"Blogpost veroeffentlicht: {state['title']}",
    )
    print(f"  Approve: '{final}' ist live, Draft entfernt.")


def _do_reject(state: dict) -> None:
    """Reject-Pfad (D-06): Draft loeschen (Single-File, bewusst einfach).

    Kein atomarer Multi-Datei-Bedarf — Reject entfernt nur eine Datei.
    """
    draft = state["draft_filename"]
    print(f"  Reject: loesehe Draft '{draft}' ...")
    delete_file(draft, "Draft verworfen")
    print(f"  Reject: Draft entfernt, nichts geht live.")


def main() -> None:
    # Schritt 1: Pending-State lesen (D-08)
    state = read_pending()
    if not state:
        print("Kein offener Draft.")
        return

    # Schritt 2: TELEGRAM_CHAT_ID laden (Akzeptanz-Filter, T-02-06)
    # Vergleich als str sicherstellen, da chat_id in Telegram-Objekten
    # manchmal int und manchmal str ist.
    own_chat_id = str(_load_secret("TELEGRAM_CHAT_ID"))

    # Schritt 3: getUpdates einmal pollen (offset aus Pending-State, D-08)
    updates = get_updates(offset=state.get("offset", 0))

    # Schritt 4: Updates iterieren
    for upd in updates:
        cq = upd.get("callback_query")
        if not cq:
            continue  # Kein Callback — z.B. normaler Text-Update

        # Akzeptanz-Filter (T-02-06, Security): nur eigene Chat-ID
        # Telegram liefert chat_id unter cq["message"]["chat"]["id"] (wenn
        # Nachricht existiert) oder cq["from"]["id"] (User-ID). Wir pruefen
        # beide, damit der Filter auch bei editierten/geloeschten Nachrichten
        # greift.
        msg_chat_id = str(cq.get("message", {}).get("chat", {}).get("id", ""))
        from_id = str(cq.get("from", {}).get("id", ""))
        if own_chat_id not in (msg_chat_id, from_id):
            print(f"  Fremde Chat-ID ({msg_chat_id or from_id}) — ignoriert (T-02-06).")
            continue

        data = cq.get("data", "")

        # Zuordnung: nur der passende Slug wird verarbeitet (D-08, alte Drafts ignorieren)
        approve_key = f"approve:{state['slug']}"
        reject_key = f"reject:{state['slug']}"

        if data == approve_key:
            _do_approve(state)
            answer_callback_query(cq["id"], "Veroeffentlicht")
        elif data == reject_key:
            _do_reject(state)
            answer_callback_query(cq["id"], "Verworfen")
        else:
            # Anderer/alter Draft — ignorieren
            continue

        # Schritt 5: Pending leeren (T-02-07, D-08).
        # Strategie: clear_pending() loescht .telegram-pending.json vollstaendig.
        # Begruendung: Nach Approve oder Reject ist der Draft-Workflow abgeschlossen;
        # ein leeres/nicht existierendes Pending verhindert jede Doppelverarbeitung,
        # auch wenn der Offset-Ansatz (update_id+1 speichern) ausfallen wuerde.
        clear_pending()
        print("  Pending-State geleert — keine Doppelverarbeitung moeglich.")
        return

    # Kein passendes Update gefunden (getUpdates leer oder kein Slug-Match)
    print("Kein passendes Update gefunden (noch keine Antwort oder Offset bereits aktuell).")


if __name__ == "__main__":
    main()
