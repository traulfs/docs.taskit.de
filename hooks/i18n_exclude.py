"""Leave individual pages out of one language's build.

mkdocs-static-i18n has no per-language exclude (exclude_docs cannot be
overridden per language), and with fallback_to_default every English
page is copied into /de/ when no German file exists. This hook removes
the listed pages from the given language's build before the i18n plugin
builds its file list, and drops that language from the page's language
switcher / hreflang alternates in the other builds, so nothing links to
the missing page.

Paths are relative to the locale folder (docs/en/..., docs/de/...).
"""

from mkdocs.plugins import event_priority, get_plugin_logger

log = get_plugin_logger(__name__)

EXCLUDE = {
    # Customer draft, "not yet released" (DOC9) - no German version for now.
    "de": {"BEACON-LINE/BEACON-LINE Advertisement in JSON Format (EN).md"},
}


def _current_language(config):
    return config.plugins["i18n"].current_language


def _locale_relative(src_uri):
    first, _, rest = src_uri.partition("/")
    return rest if first in ("de", "en") else src_uri


# Runs before mkdocs-static-i18n's on_files (priority -100).
@event_priority(0)
def on_files(files, config):
    excluded = EXCLUDE.get(_current_language(config), set())
    for file in list(files):
        if _locale_relative(file.src_uri) in excluded:
            files.remove(file)
            log.info(f"i18n_exclude: {file.src_uri} left out of the '{_current_language(config)}' build")
    return files


# Runs after mkdocs-static-i18n's on_page_context (priority 50).
@event_priority(-10)
def on_page_context(context, page, config, nav):
    rel = _locale_relative(page.file.src_uri)
    langs = {lang for lang, paths in EXCLUDE.items() if rel in paths}
    if langs:
        # mkdocs-static-i18n sets config.extra.alternate as an attribute per page
        config.extra.alternate = [
            alt for alt in (config.extra.alternate or []) if alt.get("lang") not in langs
        ]
        for lang in langs:
            getattr(page.file, "alternates", {}).pop(lang, None)
    return context
