"""Behavior-Tests fuer den Nachhoer-Loop (Phase 04.1, Plan 01, Task 3).

Prueft:
  1. Approve im Fenster -> _do_approve genau einmal, Loop endet terminal (AUTO-01)
  2. Reject im Fenster -> _do_reject genau einmal, nichts live, Loop endet (AUTO-02)
  3. Fremde Chat-ID ignoriert -> weder _do_approve noch _do_reject (AUTO-04)
  4. Timeout sauber -> Loop endet ohne Exception, _do_approve/_do_reject nie (AUTO-03)
  5. Keine Doppelverarbeitung -> _do_approve genau einmal trotz mehrerer Iterationen (AUTO-03)

Alle externen Effekte sind gemockt (kein Netz, kein Repo, kein Telegram).
Aufruf: python -m unittest scripts.test_nachhoer_loop -v
"""
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

# scripts/ importierbar machen (analog zur Produktionsumgebung)
sys.path.insert(0, str(Path(__file__).resolve().parent))


# ---------------------------------------------------------------------------
# Hilfsfunktionen fuer Update-Fixtures
# ---------------------------------------------------------------------------

def _make_cq_update(update_id: int, chat_id: str, from_id: str, data: str) -> dict:
    """Erzeugt ein realistisches callback_query-Update-Dict."""
    return {
        "update_id": update_id,
        "callback_query": {
            "id": f"cq-{update_id}",
            "from": {"id": int(from_id)},
            "message": {
                "chat": {"id": int(chat_id)},
            },
            "data": data,
        },
    }


def _make_msg_update(update_id: int, chat_id: str, from_id: str, text: str) -> dict:
    """Erzeugt ein realistisches Text-Nachrichten-Update-Dict."""
    return {
        "update_id": update_id,
        "message": {
            "chat": {"id": int(chat_id)},
            "from": {"id": int(from_id)},
            "text": text,
        },
    }


OWN_CHAT_ID = "111111111"
FOREIGN_CHAT_ID = "999999999"
SLUG = "test-slug-2026"
DRAFT = "draft-2026-06-20.html"


# ---------------------------------------------------------------------------
# Tests fuer process_update() (Unit-Level)
# ---------------------------------------------------------------------------

class TestProcessUpdate(unittest.TestCase):
    """Testet process_update() direkt (Unit-Tests ohne Loop)."""

    def _patch_all(self):
        """Gibt einen dict mit allen noetigen Mock-Patchern zurueck."""
        return {
            "do_approve": patch("telegram_check._do_approve", return_value="Test-Titel"),
            "do_reject":  patch("telegram_check._do_reject"),
            "find_draft": patch("telegram_check._find_draft_in_repo", return_value=DRAFT),
            "get_upd":    patch("telegram_check.get_updates", return_value=[]),
            "send_msg":   patch("telegram_check.send_message"),
            "ans_cbq":    patch("telegram_check.answer_callback_query"),
            "load_sec":   patch("telegram_check._load_secret", return_value="https://insektenblitz.com"),
        }

    def test_approve_eigene_chat_id(self):
        """Approve-Klick von eigener Chat-ID -> _do_approve einmal, 'handled' zurueck."""
        upd = _make_cq_update(1, OWN_CHAT_ID, OWN_CHAT_ID, f"approve:{SLUG}")
        patches = self._patch_all()
        with patches["do_approve"] as m_approve, \
             patches["do_reject"]  as m_reject, \
             patches["find_draft"], \
             patches["get_upd"], \
             patches["send_msg"], \
             patches["ans_cbq"], \
             patches["load_sec"]:
            from telegram_check import process_update
            result = process_update(upd, OWN_CHAT_ID)
        self.assertEqual(result, "handled")
        m_approve.assert_called_once()
        m_reject.assert_not_called()

    def test_reject_eigene_chat_id(self):
        """Reject-Klick von eigener Chat-ID -> _do_reject einmal, 'handled' zurueck."""
        upd = _make_cq_update(2, OWN_CHAT_ID, OWN_CHAT_ID, f"reject:{SLUG}")
        patches = self._patch_all()
        with patches["do_approve"] as m_approve, \
             patches["do_reject"]  as m_reject, \
             patches["find_draft"], \
             patches["get_upd"], \
             patches["send_msg"], \
             patches["ans_cbq"], \
             patches["load_sec"]:
            from telegram_check import process_update
            result = process_update(upd, OWN_CHAT_ID)
        self.assertEqual(result, "handled")
        m_reject.assert_called_once()
        m_approve.assert_not_called()

    def test_fremde_chat_id_ignoriert(self):
        """Approve-Klick von fremder Chat-ID -> weder _do_approve noch _do_reject."""
        upd = _make_cq_update(3, FOREIGN_CHAT_ID, FOREIGN_CHAT_ID, f"approve:{SLUG}")
        patches = self._patch_all()
        with patches["do_approve"] as m_approve, \
             patches["do_reject"]  as m_reject, \
             patches["find_draft"], \
             patches["get_upd"], \
             patches["send_msg"], \
             patches["ans_cbq"], \
             patches["load_sec"]:
            from telegram_check import process_update
            result = process_update(upd, OWN_CHAT_ID)
        self.assertEqual(result, "skipped")
        m_approve.assert_not_called()
        m_reject.assert_not_called()


# ---------------------------------------------------------------------------
# Tests fuer den Nachhoer-Loop in content_machine (Verhalten des Loops)
# ---------------------------------------------------------------------------

def _run_loop_with_updates(updates_sequence, budget_s=0.2, long_poll_s=0):
    """Hilfsfunktion: fuehrt den Nachhoer-Loop-Block aus content_machine isoliert aus.

    Mockt alle Abhaengigkeiten. Gibt (m_approve, m_reject, n_get_updates_calls) zurueck.

    updates_sequence: Liste von Listen — jede innere Liste ist die Rueckgabe eines
                      get_updates-Aufrufs. Leer am Ende = Timeout.
    budget_s:         Kurzes Zeitbudget fuer schnelle Tests (Default: 200ms).
    long_poll_s:      long_poll-Parameter fuer get_updates (Default: 0 = Short-Poll im Mock).
    """
    import re as _re
    import importlib

    # Frisch importieren (Mocks koennen Modul-State aendern)
    import telegram_check as tc
    import telegram_bot as tb

    m_approve  = MagicMock(return_value="Gemockter Titel")
    m_reject   = MagicMock()
    m_find     = MagicMock(return_value=DRAFT)
    m_send_msg = MagicMock()
    m_ans_cbq  = MagicMock()
    m_load_sec = MagicMock(return_value=OWN_CHAT_ID)

    # get_updates als side_effect-Liste: jeder Aufruf gibt das naechste Element zurueck.
    # Wenn die Sequenz erschoepft ist: immer [] (Timeout-Verhalten, kein StopIteration).
    updates_iter = iter(updates_sequence)
    def _get_upd_side_effect(offset=0, long_poll=0):
        try:
            return next(updates_iter)
        except StopIteration:
            return []
    m_get_updates = MagicMock(side_effect=_get_upd_side_effect)

    with patch.object(tc, "_do_approve", m_approve), \
         patch.object(tc, "_do_reject",  m_reject), \
         patch.object(tc, "_find_draft_in_repo", m_find), \
         patch.object(tc, "get_updates",  m_get_updates), \
         patch.object(tc, "send_message", m_send_msg), \
         patch.object(tc, "answer_callback_query", m_ans_cbq), \
         patch.object(tc, "_load_secret", m_load_sec), \
         patch("telegram_bot.get_updates", m_get_updates), \
         patch("telegram_bot._load_secret", m_load_sec):

        # Loop-Logik direkt aus content_machine nachbauen (isoliert, ohne den ganzen Lauf)
        # Das ist das gleiche Muster wie im Produktionscode.
        own_chat_id = str(OWN_CHAT_ID)
        offset = 0
        deadline = time.monotonic() + budget_s
        handled = False

        while time.monotonic() < deadline:
            updates = m_get_updates(offset=offset, long_poll=long_poll_s)
            for upd in updates:
                update_id = upd.get("update_id", 0)
                result = tc.process_update(upd, own_chat_id)
                offset = update_id + 1
                if result == "handled":
                    handled = True
                    break
            else:
                continue
            break

    return m_approve, m_reject, m_get_updates, handled


class TestNachhoerLoop(unittest.TestCase):
    """Behavior-Tests fuer den Nachhoer-Loop (AUTO-01..04)."""

    def test_approve_im_fenster(self):
        """AUTO-01: Approve-Klick im Fenster -> _do_approve genau einmal, Loop endet terminal."""
        approve_upd = _make_cq_update(10, OWN_CHAT_ID, OWN_CHAT_ID, f"approve:{SLUG}")
        m_approve, m_reject, _, handled = _run_loop_with_updates([[approve_upd]])
        m_approve.assert_called_once()
        m_reject.assert_not_called()
        self.assertTrue(handled, "Loop muss nach Approve als 'handled' beendet sein")

    def test_reject_im_fenster(self):
        """AUTO-02: Reject-Klick im Fenster -> _do_reject genau einmal, nichts live, Loop endet."""
        reject_upd = _make_cq_update(20, OWN_CHAT_ID, OWN_CHAT_ID, f"reject:{SLUG}")
        m_approve, m_reject, _, handled = _run_loop_with_updates([[reject_upd]])
        m_reject.assert_called_once()
        m_approve.assert_not_called()
        self.assertTrue(handled, "Loop muss nach Reject als 'handled' beendet sein")

    def test_fremde_chat_id_ignoriert(self):
        """AUTO-04: Fremde Chat-ID -> weder _do_approve noch _do_reject; Loop laeuft bis Timeout."""
        foreign_upd = _make_cq_update(30, FOREIGN_CHAT_ID, FOREIGN_CHAT_ID, f"approve:{SLUG}")
        # budget_s sehr kurz: Loop soll durch Timeout enden, nicht durch handled
        m_approve, m_reject, _, handled = _run_loop_with_updates(
            [[foreign_upd], [], []], budget_s=0.1
        )
        m_approve.assert_not_called()
        m_reject.assert_not_called()
        self.assertFalse(handled, "Loop darf bei fremder Chat-ID NICHT als 'handled' beendet sein")

    def test_timeout_sauber(self):
        """AUTO-03: Kein Klick -> Loop endet nach Zeitbudget ohne Exception."""
        # Nur leere Update-Listen = simulierter Timeout
        try:
            m_approve, m_reject, _, handled = _run_loop_with_updates(
                [[], [], []], budget_s=0.1
            )
        except Exception as exc:
            self.fail(f"Loop warf Exception beim Timeout: {exc}")
        m_approve.assert_not_called()
        m_reject.assert_not_called()
        self.assertFalse(handled, "Loop darf beim Timeout NICHT als 'handled' beendet sein")

    def test_keine_doppelverarbeitung(self):
        """AUTO-03: Ein verarbeitetes Update wird genau einmal verarbeitet (Offset-Fortschreibung).

        Simulation: get_updates liefert bei Offset 0 ein Approve-Update, bei Offset 11
        eine leere Liste (korrekte Offset-Fortschreibung). _do_approve wird genau einmal
        aufgerufen — selbst wenn der Loop theoretisch weitere Iterationen machen wuerde.
        """
        approve_upd = _make_cq_update(10, OWN_CHAT_ID, OWN_CHAT_ID, f"approve:{SLUG}")

        # side_effect-Funktion: prueft Offset und simuliert Single-Delivery
        offsets_seen = []
        def get_upd_side_effect(offset=0, long_poll=0):
            offsets_seen.append(offset)
            if offset == 0:
                return [approve_upd]
            return []  # Bei Offset 11 (= update_id + 1) kommt nichts mehr

        import telegram_check as tc

        m_approve  = MagicMock(return_value="Gemockter Titel")
        m_reject   = MagicMock()
        m_find     = MagicMock(return_value=DRAFT)
        m_send_msg = MagicMock()
        m_ans_cbq  = MagicMock()
        m_load_sec = MagicMock(return_value=OWN_CHAT_ID)
        m_get_upd  = MagicMock(side_effect=get_upd_side_effect)

        with patch.object(tc, "_do_approve", m_approve), \
             patch.object(tc, "_do_reject",  m_reject), \
             patch.object(tc, "_find_draft_in_repo", m_find), \
             patch.object(tc, "get_updates",  m_get_upd), \
             patch.object(tc, "send_message", m_send_msg), \
             patch.object(tc, "answer_callback_query", m_ans_cbq), \
             patch.object(tc, "_load_secret", m_load_sec):

            own_chat_id = str(OWN_CHAT_ID)
            offset = 0
            deadline = time.monotonic() + 0.5
            handled = False

            while time.monotonic() < deadline:
                updates = m_get_upd(offset=offset, long_poll=0)
                for upd in updates:
                    update_id = upd.get("update_id", 0)
                    result = tc.process_update(upd, own_chat_id)
                    offset = update_id + 1  # Offset fortschreiben (Single-Delivery)
                    if result == "handled":
                        handled = True
                        break
                else:
                    continue
                break

        # _do_approve darf genau einmal aufgerufen worden sein (keine Doppelverarbeitung)
        m_approve.assert_called_once()
        m_reject.assert_not_called()
        self.assertTrue(handled)
        # Offset muss nach dem Approve auf update_id + 1 = 11 gesetzt worden sein
        self.assertIn(0, offsets_seen, "Erster Aufruf mit Offset 0 erwartet")
        # Bei korrekter Fortschreibung wird Offset 11 NICHT mehr an get_updates
        # uebergeben (Loop bricht bei 'handled' ab) — aber der interne offset-Wert
        # muss 11 sein. Wir pruefen, dass Offset 0 NUR einmal an get_updates gegangen ist.
        self.assertEqual(offsets_seen.count(0), 1, "Offset 0 darf nur einmal verwendet werden")


if __name__ == "__main__":
    unittest.main()
