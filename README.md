# docs.taskit.de

Technische Dokumentation der [taskit GmbH](https://www.taskit.de) (Berlin) zu Sensornetzwerken, BLE-Formaten und IO-Modulen. Live unter <https://docs.taskit.de>.

## Aufbau

- [MkDocs](https://www.mkdocs.org) mit [Material-Theme](https://squidfunk.github.io/mkdocs-material/), Konfiguration in `mkdocs.yml`.
- Inhalte in `docs/en/<Thema>/…md` (Themen: `Measure2Go`, `BLE`, `BEACON-LINE`, `gpio.net`), Startseite `docs/en/index.md`. Die Navigation entsteht automatisch aus den Ordnern.
- `docs/assets/` (Logo, Favicon), `docs/stylesheets/extra.css`, `docs/robots.txt`.
- Plugins: `mkdocs-static-i18n` (Ordnerstruktur pro Sprache), `search`, `swagger-ui-tag` (OpenAPI-YAMLs als Swagger UI).
- `hooks/roamlinks_i18n.py` löst Obsidian-`[[Wikilinks]]` auf. Die Dokumente werden als [Obsidian](https://obsidian.md)-Vault gepflegt; `*.excalidraw.md` und `*.numbers` werden nicht veröffentlicht.

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

## Veröffentlichen

Jeder Push auf `main` startet den GitHub-Actions-Workflow `.github/workflows/deploy.yml`: `mkdocs build` und Deploy auf GitHub Pages. Die Custom Domain `docs.taskit.de` ist in den Pages-Einstellungen des Repositorys eingetragen. Änderungen am besten per Branch und Pull Request einbringen.
