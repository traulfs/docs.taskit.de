# docs.taskit.de

Technische Dokumentation der [taskit GmbH](https://www.taskit.de) (Berlin) zu Sensornetzwerken, BLE-Formaten und IO-Modulen. Live unter <https://docs.taskit.de>.

## Aufbau

- [MkDocs](https://www.mkdocs.org) mit [Material-Theme](https://squidfunk.github.io/mkdocs-material/), Konfiguration in `mkdocs.yml`.
- Inhalte in `docs/en/<Thema>/…md` (Englisch, Standardsprache, unter `/`) und `docs/de/<Thema>/…md` (Deutsch, unter `/de/`). Themen: `Measure2Go`, `BLE`, `BEACON-LINE`, `gpio.net`; Startseiten `docs/en/index.md` und `docs/de/index.md`. Die Navigation entsteht automatisch aus den Ordnern.
- `docs/assets/` (Logo, Favicon), `docs/stylesheets/extra.css`, `docs/robots.txt`.
- Plugins: `mkdocs-static-i18n` (Ordnerstruktur pro Sprache), `search`, `swagger-ui-tag` (OpenAPI-YAMLs als Swagger UI).
- `hooks/roamlinks_i18n.py` löst Obsidian-`[[Wikilinks]]` auf. Die Dokumente werden als [Obsidian](https://obsidian.md)-Vault gepflegt; `*.excalidraw.md` und `*.numbers` werden nicht veröffentlicht.
- `hooks/i18n_extras.py`: Seiten pro Sprache ausschließen, Warnung bei fehlender deutscher Übersetzung, hreflang `x-default`. `overrides/main.html` gibt das `x-default`-Tag aus.

## Lokal bauen und ansehen

Voraussetzung: Python 3.12 oder neuer.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows (Git Bash): source .venv/Scripts/activate
pip install -r requirements.txt
mkdocs serve                     # http://127.0.0.1:8000, lädt bei Änderungen neu
```

Vor dem Pushen prüfen, ob der Build ohne Warnungen durchläuft (kaputte Links brechen den Strict-Build ab):

```bash
mkdocs build --strict
```

Die Build-Ausgabe `site/` ist per `.gitignore` ausgeschlossen; `.venv/` bitte nicht committen.

## Deutsche Übersetzung pflegen

Die englischen Seiten in `docs/en/` sind die Quelle. Jede Seite hat ein deutsches Gegenstück in `docs/de/` mit **demselben Pfad und Dateinamen** (z. B. `docs/en/gpio.net/PORT Mode.md` → `docs/de/gpio.net/PORT Mode.md`). Nur so verknüpfen Sprachumschalter und hreflang die beiden Seiten.

- **Jede Änderung an einer englischen Seite braucht die passende Änderung in der deutschen Seite** – auch Tabellen, Codes und Beispiele, damit beide Sprachen inhaltlich gleich bleiben.
- **Neue Seite:** englische und deutsche Datei anlegen, beide mit eigener `description:` im Front Matter (120–155 Zeichen).
- **Begriffe:** siehe `i18n/glossar-de.md` (Produktnamen, Feldnamen, Code und API-Pfade bleiben unverändert).
- **Wikilinks** in deutschen Seiten mit deutschem Linktext schreiben: `[[PORT Mode|PORT-Modus]]`. Der Dateiname bleibt englisch.
- **Dateien nur in `docs/en/`:** OpenAPI-YAMLs und `io-nuts_carts.csv`. Die deutschen API-Seiten verweisen mit `src="../../en/…"` darauf.
- **Seite bewusst nicht übersetzen:** Pfad in `EXCLUDE` in `hooks/i18n_extras.py` eintragen; die Seite erscheint dann nicht unter `/de/` (derzeit: der Kundenentwurf „BEACON-LINE Advertisement in JSON Format (EN)“).

Prüfen:

```bash
mkdocs build --strict
```

Fehlt zu einer englischen Seite die deutsche Datei, bricht der Strict-Build mit `No 'de' translation for en/…` ab. Der Deploy-Build läuft ohne `--strict` weiter und zeigt unter `/de/` dann die englische Seite. Geänderte Inhalte erkennt der Build nicht – dafür beim Review die englische und die deutsche Datei nebeneinander ansehen.

## Veröffentlichen

Jeder Push auf `main` startet den GitHub-Actions-Workflow `.github/workflows/deploy.yml`: `mkdocs build` und Deploy auf GitHub Pages. Die Custom Domain `docs.taskit.de` ist in den Pages-Einstellungen des Repositorys eingetragen. Änderungen am besten per Branch und Pull Request einbringen.
