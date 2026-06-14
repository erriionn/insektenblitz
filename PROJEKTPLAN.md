---
name: project-insektenblitz-website
description: "Insektenblitz.com Website – Projektplan, Verlauf, offene Aufgaben und Erfolgsmessung"
metadata:
  type: project
---

# Insektenblitz Website – Projektplan

**Zuletzt aktualisiert: 14.06.2026 um 15:02:26 Uhr**

---

## 1. Ausgangslage

- Kollaboratives Website-Projekt zwischen Malte Ilert und Jonathan (GitHub: thetopseller-ops)
- Repo bereits auf GitHub vorhanden, mit Netlify verbunden, Domain bei GoDaddy registriert
- Bei Session-Start: Website existierte im Repo, aber war **nicht erreichbar** (Domain zeigte auf GoDaddy-Parking, Netlify zeigte 404, kein Impressum, kein Datenschutz, kein Kontaktformular)
- Reine HTML/CSS/JS-Website ohne Framework

---

## 2. Was bisher umgesetzt wurde

### Infrastruktur & Deployment ✅
| Problem | Ursache | Lösung |
|---|---|---|
| Netlify 404 auf `/` | Datei `Index` (ohne Extension) kollidierte mit `index.html` auf Linux | `Index` gelöscht, `netlify.toml` mit `command = ""` hinzugefügt |
| Deploy wurde nicht live | Publishing war auf alten Deploy gelockt | Manuell „Publish deploy" + „Unlock to start auto publishing" |
| insektenblitz.com → GoDaddy Parking | Nameserver falsch | Alle 4 Netlify-Nameserver (dns1–4.p02.nsone.net) bei GoDaddy eingetragen |
| Netlify blockiert Kollaborateur | Free Plan: Private Repo nur 1 Contributor | Repo auf **Public** gestellt |
| Netlify Forms nicht aktiv | Form detection war deaktiviert | Aktiviert + Cache-Deploy erzwungen |

### Rechtliche Seiten ✅
- **`impressum.html`** – vollständig (Senior Living UG, Malte Ilert, HRB 10878, USt-IdNr. DE367260473)
- **`datenschutz.html`** – umfassend aktualisiert am 14.06.2026 (siehe unten)
- Beide Seiten im Footer von `index.html` verlinkt

#### Datenschutzerklärung – Inhalte (Stand 14.06.2026, 15:02 Uhr)
- Verantwortlicher: Senior Living UG
- Hosting: Netlify inkl. AVV nach Art. 28 DSGVO + EU-U.S. Data Privacy Framework
- Google Fonts: Hinweis auf IP-Übertragung an Google
- Anruf-Tracking: localStorage, kein Drittanbieter
- Server-Logs: Netlify, anonymisierte IP
- Cookies: nur technisch notwendige, kein Consent-Banner nötig
- **Kontaktformular (8.1):** Netlify Forms als Auftragsverarbeiter, Speicherfristen (90 Tage / §147 AO / §257 HGB)
- **Weitergabe (8.3):** Drei Szenarien dokumentiert – Eigenausführung, verbundenes Unternehmen, externer Fachbetrieb → wichtig für Vermittlungsmodell
- Aufsichtsbehörde: LDI NRW, Kavalleriestraße 2–4, 40213 Düsseldorf

### Kontaktfunnel ✅
- 4-stufiger Multi-Step-Funnel in `index.html`
- **Step 1:** Land (zuerst!) → Name → Straße + Nr. → PLZ + Ort (nebeneinander) → Region → Rufnummer → E-Mail → Kundentyp
- **Step 2:** Welcher Schädling? (EPS / Goldafter / Palmenzünsler / Anderer)
- **Step 3:** Was ist befallen? (Ein Baum / Mehrere Bäume / Ganzes Areal) + Datenschutz-Checkbox (Pflicht)
- **Step 4:** Calendly-Link (calendly.com/fassadenblitzgmbh/termin-mit-malte-ilert)
- Netlify Forms aktiv, Form-Name erscheint als Submission-Titel ✅
- E-Mail- und Telefon-Validierung mit spezifischen Fehlermeldungen ✅
- Datenschutz-Pflichtcheckbox vor Absenden ✅

### Jonathan's Beiträge (parallel, 14.06.2026) ✅
- 3 Blog-Artikel erstellt: EPS-Saison, Gifthaare-Schutz, Palmenzünsler Mallorca
- Google Fonts **lokal gehostet** (kein externer Google-Aufruf → löst Cookie-Problem)
- Neue Bilder: Hero, Haustiere, Kinder, Umwelt
- Impressum angepasst

---

## 3. Technische Details

### Repo & Deployment
- GitHub: `https://github.com/thetopseller-ops/insektenblitz` (public)
- Lokal (Malte): `/Users/milert/Desktop/Malte_Claude/privat_Claude/insektenblitz/`
- Hosting: Netlify (Projekt: insektenblitz.com), Auto-Publishing aktiv seit 14.06.2026
- Domain: insektenblitz.com (Netlify DNS, propagiert)
- `netlify.toml`: `[build] command = ""`

### Firmendaten
- **Senior Living UG (haftungsbeschränkt)** | GF: Malte Ilert
- Taubenweg 17, 32805 Horn-Bad Meinberg
- Tel: +49 151 51001255 | E-Mail: info@insektenblitz.com
- HRB 10878, AG Lemgo | USt-IdNr.: DE367260473
- Datenschutzbehörde: LDI NRW, Kavalleriestraße 2–4, 40213 Düsseldorf

### Netlify Forms – Felder (form-name: „kontaktanfrage")
`name` · `land` · `strasse` · `plz` · `ort` · `region` · `telefon` · `email` · `kundentyp` · `schaedling` · `befall`

### Design-System
- Fonts: Merriweather (Serif) + Open Sans (Sans) – lokal gehostet
- Grün: #1d5a3d · #2d8659 · #3fb566 | Hintergrund: #f8f9f7 | Text: #1a2423

---

## 4. Offene Aufgaben (Backlog)

### Priorität Hoch
- [ ] **AGBs erstellen** – `agb.html` anlegen (in Arbeit)
  - Geltungsbereich, Vertragsschluss, Leistungsumfang
  - Vergütung & Zahlung, Stornierung, Gewährleistung & Haftung
  - Besonderheit: Vermittlungsmodell (Weitergabe an regionale Fachbetriebe) muss abgedeckt sein
  - Footer-Link auf `#` → auf `agb.html` updaten nach Fertigstellung

- [ ] **Bestätigungsmail via n8n** – Netlify Forms → Outgoing Webhook → n8n → E-Mail an Absender
  - E-Mail-Feld vorhanden (field: `email`)
  - Felder: name, land, strasse, plz, ort, region, telefon, email, kundentyp, schaedling, befall

- [ ] **E-Mail-Dienst für insektenblitz.com einrichten**
  - MX-Records in Netlify DNS eintragen
  - Empfohlene Anbieter: Google Workspace (~€6/Mo), Zoho Mail (kostenlos bis 5 User), IONOS (~€1/Mo)

- [ ] **Footer-Platzhalter aktualisieren** in `index.html`:
  - Telefon: `+49 123 456789` → `+49 151 51001255`
  - E-Mail: `info@insektenblitz.de` → `info@insektenblitz.com`
  - Adresse: `[VOLLSTÄNDIGE ADRESSE]` → Taubenweg 17, 32805 Horn-Bad Meinberg
  - Öffnungszeiten: eintragen oder entfernen

- [ ] **E-Mail-Benachrichtigung für Malte** in Netlify: Forms → Form notifications → E-Mail

- [ ] **Google Analytics + GTM einrichten** (geplant, noch nicht umgesetzt)
  - **Schritt 1:** GTM-Container anlegen (tagmanager.google.com) → Container-ID notieren (GTM-XXXXXXX)
  - **Schritt 2:** GA4-Property anlegen (analytics.google.com) → Measurement-ID notieren (G-XXXXXXXXXX)
  - **Schritt 3:** Cookie-Banner vollständig umbauen – aktuell nur „Verstanden", muss werden:
    - Kategorie „Notwendige Cookies" (immer aktiv)
    - Kategorie „Statistik" (Google Analytics) – Opt-In
    - Kategorie „Marketing" (GTM) – Opt-In
    - Buttons: „Alle akzeptieren" / „Auswahl speichern" / „Ablehnen"
  - **Schritt 4:** GTM/GA nur laden wenn Consent gegeben → via `dataLayer.push` Consent-Signal
  - **Schritt 5:** Datenschutzerklärung um GA/GTM-Abschnitt ergänzen
  - **Wichtig:** Ohne Opt-In darf GA/GTM nicht feuern (DSGVO – kein Opt-Out, sondern Opt-In!)
  - **Aktueller Banner-Text** muss von „keine Tracking-Cookies" auf echtes Consent-Management geändert werden

### Priorität Mittel
- [ ] **Spanische Version** (`/es/`) – Mallorca-Markt (Palmenzünsler)
  - `es/index.html` – Fokus Palmenzünsler
  - `es/impressum.html` → „Aviso Legal" (spanisches Recht)
  - `es/datenschutz.html` → „Política de Privacidad"
  - Sprachumschalter 🇩🇪 / 🇪🇸 in Navigation
  - Funnel auf Spanisch
  - Separate Seiten für SEO (nicht JS-i18n)

- [ ] **GitHub Token erneuern** – Token vom 14.06.2026 war in Session kompromittiert

### Priorität Niedrig
- [ ] Fallbeispiele-Sektion aktivieren (aktuell `display:none` in `index.html`)
- [ ] Kundenbewertungen aktivieren (aktuell `display:none` in `index.html`)
- [ ] Favicon einbinden (`images/logo-insektenblitz.svg`)
- [ ] Google Search Console einrichten (nach vollständigem Launch)
- [ ] Google Business Profile anlegen

---

## 5. Build–Measure–Learn

| Metrik | Wo messen | Ziel |
|---|---|---|
| Funnel-Submissions | Netlify Forms → kontaktanfrage | >15% Conversion |
| Calendly-Buchungen | Calendly Dashboard | Erstgespräche / Woche |
| Anruf-Klicks | localStorage (eingebaut) | Klickrate auf CTA |
| Organischer Traffic | Google Search Console | DE + ES |
| Schädlingsverteilung | Netlify Forms CSV | Welche Schädlinge dominieren? |
| Länderverteilung | Netlify Forms CSV | DE vs. ES/Mallorca |

**Loop:** Build → Measure (Netlify Forms CSV wöchentlich auswerten) → Learn (Konversionstreiber) → Iterate (Texte, Reihenfolge, Angebote)

---

## 6. Kollaborations-Setup

### GitHub-Repository
- **URL:** https://github.com/thetopseller-ops/insektenblitz
- **Sichtbarkeit:** Public (Netlify Free Plan)
- **Branch:** `main`
- **Dieser Projektplan:** https://github.com/thetopseller-ops/insektenblitz/blob/main/PROJEKTPLAN.md

### Team
- **Malte Ilert** (GitHub: milert) – lokal via Claude Code
- **Jonathan** (GitHub: thetopseller-ops) – Repo-Owner, direkt via GitHub

### Workflow
- Push auf `main` → Netlify deployt automatisch
- Bei Konflikt: `git pull --no-rebase origin main` dann `git push`
- Projektplan: direkt in `PROJEKTPLAN.md` bearbeiten
