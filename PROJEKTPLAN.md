---
name: project-insektenblitz-website
description: "Insektenblitz.com Website – Projektplan, Verlauf, offene Aufgaben und Erfolgsmessung"
metadata: 
  node_type: memory
  type: project
  originSessionId: b1219277-afcc-4e21-8f7a-85c21710ed1d
---

# Insektenblitz Website – Projektplan

**Zuletzt aktualisiert: 14.06.2026 um 13:11:16 Uhr**

---

## 1. Ausgangslage

- Kollaboratives Website-Projekt zwischen Malte Ilert und einem Kollegen (Jonathan, GitHub: thetopseller-ops)
- Repo bereits auf GitHub vorhanden, mit Netlify verbunden, Domain bei GoDaddy registriert
- Bei Session-Start: Website existierte im Repo, aber war **nicht erreichbar** (Domain zeigte auf GoDaddy-Parking, Netlify zeigte 404, kein Impressum, kein Datenschutz, kein Kontaktformular)
- Reine HTML/CSS/JS-Website ohne Framework

---

## 2. Was wir in dieser Session aufgebaut haben

### Infrastruktur & Deployment (gelöst)
| Problem | Ursache | Lösung |
|---|---|---|
| Netlify 404 auf `/` | Datei `Index` (ohne Extension) kollidierte mit `index.html` auf Linux | `Index` gelöscht, `netlify.toml` mit `command = ""` hinzugefügt |
| Deploy wurde nicht live | Publishing war auf alten Deploy gelockt | Manuell „Publish deploy" geklickt + „Unlock to start auto publishing" |
| insektenblitz.com → GoDaddy Parking | Nameserver nicht vollständig auf Netlify umgestellt | Alle 4 Netlify-Nameserver (dns1–4.p02.nsone.net) bei GoDaddy eingetragen |
| Netlify blockiert Kollaborateur | Free Plan: Private Repo nur 1 Contributor | Repo auf **Public** gestellt |
| Netlify Forms nicht aktiv | Form detection war deaktiviert | Aktiviert + Cache-Deploy erzwungen |

### Rechtliche Seiten (neu erstellt)
- **`impressum.html`** – vollständig ausgefüllt mit echten Firmendaten (Senior Living UG)
- **`datenschutz.html`** – orientiert an ledistagency.de/datenschutz, abdeckt: Netlify-Hosting (inkl. US-Datentransfer), Google Fonts, Anruf-Tracking, LDI NRW als Aufsichtsbehörde
- Beide Seiten im Footer von `index.html` verlinkt

### Kontaktfunnel (neu erstellt)
- 4-stufiger Multi-Step-Funnel direkt in `index.html` eingebaut
- **Step 1:** Name, Land (DE / Spanien-Mallorca), Adresse, Rufnummer, E-Mail, Kundentyp (Privat / Geschäft / Institution)
- **Step 2:** Welcher Schädling? (EPS / Goldafter / Palmenzünsler / Anderer)
- **Step 3:** Was ist befallen? (Ein Baum / Mehrere Bäume / Ganzes Areal)
- **Step 4:** Calendly-Link zum Erstgespräch (calendly.com/fassadenblitzgmbh/termin-mit-malte-ilert)
- Submission via **Netlify Forms** (form-name: „kontaktanfrage")
- Netlify Forms aktiv + Form erkannt ✅

---

## 3. Technische Details

### Repo & Deployment
- GitHub: `https://github.com/thetopseller-ops/insektenblitz` (public)
- Lokal geklont: `/Users/milert/Desktop/insektenblitz/`
- Hosting: Netlify (Projekt: insektenblitz.com), Auto-Publishing aktiv
- Domain: insektenblitz.com (Netlify DNS, Nameserver propagiert)
- `netlify.toml`: `[build] command = ""`

### Betreiber / Impressumsdaten
- Firma: **Senior Living UG (haftungsbeschränkt)**
- GF: Malte Ilert
- Adresse: Taubenweg 17, 32805 Horn-Bad Meinberg
- Telefon: +49 151 51001255
- E-Mail: info@insektenblitz.com
- HRB 10878, AG Lemgo | USt-IdNr.: DE367260473
- Datenschutzbehörde: LDI NRW, Kavalleriestraße 2–4, 40213 Düsseldorf

### Design-System
- Fonts: Merriweather (Serif, Überschriften) + Open Sans (Sans, Fließtext)
- Primärfarbe: #1d5a3d (dunkelgrün), #2d8659 (mittelgrün), #3fb566 (hellgrün)
- Hintergrund: #f8f9f7 | Text: #1a2423 | Grau: #6b7574

---

## 4. Nächste Schritte (Backlog)

### Priorität Hoch
- [ ] **Bestätigungsmail via n8n** – Netlify Forms → Outgoing Webhook → n8n → E-Mail an Absender
  - E-Mail-Feld bereits im Formular vorhanden (field: `email`)
  - Alle Felder: name, land, adresse, telefon, email, kundentyp, schaedling, befall
  - Ziel: Nutzer bekommt direkt nach Absenden eine Eingangsbestätigung

- [ ] **Footer-Platzhalter aktualisieren** in `index.html`:
  - Telefon: `+49 123 456789` → `+49 151 51001255`
  - E-Mail: `info@insektenblitz.de` → prüfen (Impressum: info@insektenblitz.com)
  - Adresse: `[VOLLSTÄNDIGE ADRESSE]` → eintragen
  - Öffnungszeiten: eintragen oder entfernen

### Priorität Mittel
- [ ] **Spanische Version** (`/es/`) – Malte ist auch auf Mallorca aktiv (Palmenzünsler)
  - `es/index.html` – Fokus auf Palmenzünsler, spanischsprachiger Markt
  - `es/impressum.html` → „Aviso Legal" (spanisches Recht, kein deutsches TMG)
  - `es/datenschutz.html` → „Política de Privacidad"
  - Sprachumschalter 🇩🇪 / 🇪🇸 in der Navigation beider Versionen
  - Funnel auf Spanisch übersetzen
  - Separate Seiten (nicht JS-i18n) → besser für SEO

- [ ] **E-Mail-Benachrichtigung für Malte** einrichten: Netlify → Forms → Form notifications → E-Mail

### Priorität Niedrig
- [ ] Echte Bilder ersetzen (Hero, Team, Fallbeispiele) – siehe `Erforderliche Ergänzungen vor Veröffentlichung.md`
- [ ] Fallbeispiele-Sektion aktivieren (aktuell `display:none`)
- [ ] Kundenbewertungen aktivieren (aktuell `display:none`)
- [ ] Blog-Artikel schreiben (3 Artikel verlinkt, aber noch leer)
- [ ] Favicon einbinden
- [ ] AGB-Link im Footer: echte AGBs oder Link entfernen

---

## 5. Build–Measure–Learn

### Was wir messen wollen
| Metrik | Wo | Ziel |
|---|---|---|
| Funnel-Completion-Rate | Netlify Forms → Submissions | >15% der Besucher füllen Funnel aus |
| Calendly-Buchungen | Calendly Dashboard | Erstgespräche pro Woche |
| Anruf-Klicks | localStorage Tracking (eingebaut) | Klickrate auf „Jetzt anrufen" |
| Seitenaufrufe | Google Search Console (nach Launch) | Organischer Traffic aus DE + ES |

### Feedback-Loop
1. **Build** – Wir bauen Features iterativ (Funnel, Sprache, Blog)
2. **Measure** – Netlify Forms zeigt Submissions, Calendly zeigt Buchungen
3. **Learn** – Was konvertiert? Welche Schädlinge werden am häufigsten angegeben? Welches Land?
4. **Iterate** – Texte, Reihenfolge und Angebote anpassen

---

## 6. Kollaborations-Setup

- **Malte** (GitHub: milert) – pushes via Claude Code lokal
- **Jonathan** (GitHub: thetopseller-ops) – pushes direkt via GitHub
- **Netlify** deployt automatisch bei jedem Push auf `main`
- **Kein manuelles Publish mehr nötig** (Auto-Publishing aktiv seit 14.06.2026)
- Wichtig: GitHub Token wurde in der Session kompromittiert → neuen Token generieren und alten invalidieren
