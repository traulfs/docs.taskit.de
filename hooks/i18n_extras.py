"""Additions to mkdocs-static-i18n for the de/en docs.

1. Leave individual pages out of one language's build (EXCLUDE).
   mkdocs-static-i18n has no per-language exclude (exclude_docs cannot be
   overridden per language), and with fallback_to_default every English
   page is copied into /de/ when no German file exists. Listed pages are
   removed from that language's build before the i18n plugin builds its
   file list, and that language is dropped from the page's language
   switcher / hreflang alternates in the other builds.

2. Warn about English pages without a German counterpart. The warning
   makes `mkdocs build --strict` fail locally; the deploy workflow builds
   without --strict, so the site still deploys (with the English page as
   fallback on /de/).

3. hreflang x-default: provide the absolute URL of the English version
   as `x_default_url` for overrides/main.html.

4. 404.html: reset the language switcher / hreflang to the site-level
   links instead of the last built page's.

Paths are relative to the locale folder (docs/en/..., docs/de/...).
"""

from copy import deepcopy
from urllib.parse import urljoin

from mkdocs.plugins import event_priority, get_plugin_logger

log = get_plugin_logger(__name__)

DEFAULT_LOCALE = "en"
LOCALES = ("de", "en")

EXCLUDE = {
    # Customer draft, "not yet released" (DOC9) - no German version for now.
    "de": {"BEACON-LINE/BEACON-LINE Advertisement in JSON Format (EN).md"},
}


def _current_language(config):
    return config.plugins["i18n"].current_language


def _split_locale(src_uri):
    first, _, rest = src_uri.partition("/")
    return (first, rest) if first in LOCALES else (None, src_uri)


# Runs before mkdocs-static-i18n's on_files (priority -100).
@event_priority(0)
def on_files(files, config):
    lang = _current_language(config)
    excluded = EXCLUDE.get(lang, set())

    for file in list(files):
        if _split_locale(file.src_uri)[1] in excluded:
            files.remove(file)
            log.info(f"{file.src_uri} left out of the '{lang}' build")

    if lang != DEFAULT_LOCALE:
        pages = {}
        for file in files:
            if file.src_uri.endswith(".md") and not file.inclusion.is_excluded():
                locale, rel = _split_locale(file.src_uri)
                pages.setdefault(locale, set()).add(rel)
        for rel in sorted(pages.get(DEFAULT_LOCALE, set()) - pages.get(lang, set()) - excluded):
            log.warning(
                f"No '{lang}' translation for {DEFAULT_LOCALE}/{rel} - add docs/{lang}/{rel} "
                f"or list it in EXCLUDE in hooks/i18n_extras.py"
            )
    return files


def on_nav(nav, config, files):
    # files are the i18n files with their alternates (used by sitemap.xml):
    # drop alternates of excluded pages in the languages they are excluded from
    for file in files.documentation_pages():
        rel = _split_locale(file.src_uri)[1]
        for lang, paths in EXCLUDE.items():
            if rel in paths:
                getattr(file, "alternates", {}).pop(lang, None)
    return nav


# Runs after mkdocs-static-i18n's on_page_context (priority 50).
@event_priority(-10)
def on_page_context(context, page, config, nav):
    rel = _split_locale(page.file.src_uri)[1]
    langs = {lang for lang, paths in EXCLUDE.items() if rel in paths}
    alternates = config.extra.alternate or []
    if langs:
        # mkdocs-static-i18n sets config.extra.alternate as an attribute per page
        alternates = [alt for alt in alternates if alt.get("lang") not in langs]
        config.extra.alternate = alternates
        for lang in langs:
            getattr(page.file, "alternates", {}).pop(lang, None)

    # alternate links are site-root relative ("Measure2Go/TSB/", "/de/")
    context["x_default_url"] = None
    for alt in alternates:
        if alt.get("lang") == DEFAULT_LOCALE and config.site_url:
            context["x_default_url"] = urljoin(config.site_url, alt["link"])
    return context


def on_template_context(context, template_name, config):
    # 404.html is rendered after the last page and would inherit that page's
    # alternates (language switcher / hreflang); reset to the site-level ones.
    if template_name == "404.html":
        default_alternates = getattr(config.plugins["i18n"], "extra_alternate", None)
        if default_alternates:
            config.extra.alternate = deepcopy(default_alternates)
    return context
