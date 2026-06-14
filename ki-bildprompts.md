# KI-Bildprompts – EPS Drohnen Website

Alle Prompts sind für **Midjourney** (bevorzugt) und **DALL·E** (ChatGPT) ausgelegt.
Stil-Ziel: **echt, authentisch, warm – keine CGI-Ästhetik, kein Stockfoto-Look**.

---

## Wie nutzen?

**Midjourney:** `/imagine [Prompt] --ar 16:9 --style raw --v 6`
**DALL·E (ChatGPT):** Prompt direkt eingeben (auf Englisch), Format 16:9 wählen

---

## Bild 1: Hero – Drohne über Wald (Video-Alternative)

**Slot in HTML:** `[VIDEO-PLACEHOLDER-URL]` → als Bild: Hero-Hintergrund, Verhältnis 16:9

**Prompt (EN):**
```
A white professional agricultural drone flying low over a sunlit German oak forest in early summer, viewed from slightly below, treetops with fresh green leaves stretching to the horizon, golden hour light breaking through the canopy, cinematic and authentic, documentary photography style, no CGI, natural colors, 16:9 ratio
```

**Midjourney-Zusatz:** `--ar 16:9 --style raw --v 6 --q 2`

**Hinweis:** Dieses Bild als `<img>` in der Hero-Section einbauen, wenn kein Video vorhanden ist. Alternativ funktioniert auch ein echter Drohnen-Aufnahme-Screenshot.

---

## Bild 2: Über Uns – Gründer mit Drohne

**Slot in HTML:** `[IMAGE-PLACEHOLDER-TEAM-ABOUT]`
**Maße im Design:** Breite variabel, Höhe 340px

**Prompt (EN):**
```
A focused man in his early 30s, wearing a light outdoor jacket, holding a compact white drone in both hands, standing in front of oak trees with dappled summer sunlight, looking directly at the camera with a calm confident expression, authentic documentary portrait, natural light, no stock photo look, shallow depth of field, warm tones
```

**Midjourney-Zusatz:** `--ar 3:4 --style raw --v 6`

**Tipp:** Falls ihr ein eigenes Foto habt (z.B. mit eurem echten Team), ist das immer besser als ein KI-Bild. KI nur als Platzhalter verwenden.

---

## Bild 3: Alert-Karte 1 – Kinder in Gefahr

**Slot in HTML:** `[IMAGE-PLACEHOLDER-CHILDREN-DANGER]`
**Maße im Design:** Breite 100%, Höhe 150px (Landscape-Crop)

**Prompt (EN):**
```
A young girl around 6 years old with blonde hair, playing alone in a green garden with large oak trees in the background, soft afternoon light, she is unaware of the caterpillar nests above her, the mood is peaceful but subtly unsettling, photorealistic, natural German garden setting, 16:9 crop
```

**Midjourney-Zusatz:** `--ar 16:9 --style raw --v 6`

**Hinweis:** Keine offensichtlich erschreckenden Bilder – der subtile Kontrast (unbesorgt spielendes Kind, Gefahr im Hintergrund) wirkt stärker.

---

## Bild 4: Alert-Karte 2 – Haustiere gefährdet

**Slot in HTML:** `[IMAGE-PLACEHOLDER-PETS-DANGER]`
**Maße im Design:** Breite 100%, Höhe 150px (Landscape-Crop)

**Prompt (EN):**
```
A golden retriever dog curiously sniffing the base of a large oak tree in a sunny German garden, nose close to the bark and roots, warm afternoon light, photorealistic, natural garden environment, no humans visible, authentic documentary style, 16:9 ratio
```

**Midjourney-Zusatz:** `--ar 16:9 --style raw --v 6`

---

## Bild 5: Alert-Karte 3 – Umwelt / Drohne im Einsatz

**Slot in HTML:** `[IMAGE-PLACEHOLDER-ENVIRONMENT]`
**Maße im Design:** Breite 100%, Höhe 150px (Landscape-Crop)

**Prompt (EN):**
```
A white agricultural drone flying precisely between the branches of oak trees in a lush green forest, bright daylight, the drone's spray mechanism targeting a specific area on the trunk, no wide chemical mist, precise and surgical, photorealistic documentary photography, 16:9 ratio
```

**Midjourney-Zusatz:** `--ar 16:9 --style raw --v 6`

---

## Bild 6: Blog-Artikel 1 – EPS-Saison

**Slot in HTML:** `[IMAGE-PLACEHOLDER-BLOG-1]`
**Thema:** "Eichenprozessionsspinner 2025: Warum der Befall immer früher beginnt"
**Maße:** Breite 100%, Höhe 200px

**Prompt (EN):**
```
Close-up of a mature oak tree trunk in early May with fresh green leaves, dappled sunlight filtering through the canopy, bark texture visible, serene forest atmosphere, warm golden light, photorealistic nature photography, no people, 16:9 ratio
```

**Midjourney-Zusatz:** `--ar 16:9 --style raw --v 6`

---

## Bild 7: Blog-Artikel 2 – Sicherheit Familie

**Slot in HTML:** `[IMAGE-PLACEHOLDER-BLOG-2]`
**Thema:** "Gifthaare im Garten: So schützen Sie Kinder und Haustiere richtig"
**Maße:** Breite 100%, Höhe 200px

**Prompt (EN):**
```
A mother standing in a lush German garden, looking protectively at her young child playing nearby, large oak trees in the background, warm afternoon sunlight, authentic family moment, candid documentary photography, soft natural light, no stock photo look, 16:9 ratio
```

**Midjourney-Zusatz:** `--ar 16:9 --style raw --v 6`

---

## Bild 8: Blog-Artikel 3 – Palmenzünsler Mallorca

**Slot in HTML:** `[IMAGE-PLACEHOLDER-BLOG-3]`
**Thema:** "Palmenzünsler auf Mallorca: 5 Warnzeichen"
**Maße:** Breite 100%, Höhe 200px

**Prompt (EN):**
```
A row of tall Mediterranean palm trees under a bright blue Mallorca sky, one palm showing signs of decline with wilting crown, dry golden grass below, authentic documentary photography, warm Mediterranean light, no tourists, photorealistic, 16:9 ratio
```

**Midjourney-Zusatz:** `--ar 16:9 --style raw --v 6`

---

## Übersicht: Fortschritt

| # | Slot | Quelle | Status |
|---|------|--------|--------|
| 1 | EPS-Schädling | Wikimedia Commons (CC BY-SA 3.0) | ✅ Eingebettet |
| 2 | Goldafter-Schädling | Wikimedia Commons (CC BY-SA 3.0) | ✅ Eingebettet |
| 3 | Palmrüssler-Schädling | Wikimedia Commons (CC BY-SA 3.0) | ✅ Eingebettet |
| 4 | Hero-Video/-Bild | KI-Prompt oben | ⏳ Prompt bereit |
| 5 | Über Uns – Team | KI-Prompt oben | ⏳ Prompt bereit |
| 6 | Kinder-Gefahr (Alert 1) | KI-Prompt oben | ⏳ Prompt bereit |
| 7 | Haustiere (Alert 2) | KI-Prompt oben | ⏳ Prompt bereit |
| 8 | Umwelt/Drohne (Alert 3) | KI-Prompt oben | ⏳ Prompt bereit |
| 9 | Blog 1 – Eiche | KI-Prompt oben | ⏳ Prompt bereit |
| 10 | Blog 2 – Familie | KI-Prompt oben | ⏳ Prompt bereit |
| 11 | Blog 3 – Mallorca | KI-Prompt oben | ⏳ Prompt bereit |

**Nicht lösbar mit KI:** Hero-Video → echtes Drohnen-Video einfügen wenn vorhanden.

---

## Empfohlene Reihenfolge für die Generierung

1. **Bild 2 (Über Uns)** – wichtigster Vertrauensanker, echtes Foto bevorzugen
2. **Bild 1 (Hero)** – größte visuelle Wirkung
3. **Bild 5–7 (Alert-Karten)** – werden zusammen gesehen
4. **Bild 6–8 (Blog)** – niedrigste Priorität

---

## Lizenz-Erinnerung

Die 3 Wikimedia-Bilder (CC BY-SA 3.0) erfordern sichtbare Namensnennung.
Diese ist bereits im HTML als Bildnachweise-Zeile eingefügt (unterhalb der Schädlinge-Sektion).
Wenn du die Seite veröffentlichst: sicherstellen, dass die Zeile sichtbar bleibt.
