"""Locale-aware replacement for mkdocs-roamlinks-plugin.

mkdocs-roamlinks-plugin resolves [[wikilinks]] by walking the *entire*
docs_dir and using the last match it finds - it has no concept of the
per-language subtrees that mkdocs-static-i18n's "folder" docs_structure
creates (docs/de/..., docs/en/...). With two locales sharing identical
filenames (e.g. TSB.md in both de/ and en/), that made every wikilink -
in both languages - resolve to whichever locale os.walk happened to
visit last, producing links into the other language's build.

This hook reimplements the same [[filename#title|alias|WxH]] syntax but
scopes the filename search to the current page's own locale folder
(derived from the first path segment of page.file.src_path), falling
back to the full docs_dir for paths outside any locale folder (shared
assets, non-localized files).
"""

import os
import re

from mkdocs.plugins import get_plugin_logger

log = get_plugin_logger(__name__)

ROAMLINK_RE = r"""\[\[(.*?)(\#.*?)?(?:\|([\D][^\|\]]+[\d]*))?(?:\|(\d+)(?:x(\d+))?)?\]\]"""

KNOWN_LOCALES = {"de", "en"}


def simplify(filename):
    return re.sub(r"[\-_ ]", "", filename.lower()).replace(".md", "")


def gfm_anchor(title):
    if title:
        title = title.strip().lower()
        title = re.sub(r"[^\w一-鿿\- ]", "", title)
        title = re.sub(r" +", "-", title)
        return title
    return ""


class RoamLinkReplacer:
    def __init__(self, base_docs_url, page_url):
        self.base_docs_url = base_docs_url
        self.page_url = page_url

        # Scope the search to the current page's own locale subtree, if any.
        first_segment = page_url.split("/", 1)[0]
        if first_segment in KNOWN_LOCALES:
            self.search_root = os.path.join(base_docs_url, first_segment)
        else:
            self.search_root = base_docs_url

    def __call__(self, match):
        whole_link = match.group(0)
        filename = match.group(1).strip() if match.group(1) else ""
        title = match.group(2).strip() if match.group(2) else ""
        format_title = gfm_anchor(title)
        alias = match.group(3) if match.group(3) else ""
        width = match.group(4) if match.group(4) else ""
        height = match.group(5) if match.group(5) else ""

        abs_linker_url = os.path.dirname(os.path.join(self.base_docs_url, self.page_url))

        rel_link_url = ""
        if filename:
            if "/" in filename:
                if "http" in filename:
                    rel_link_url = filename
                else:
                    rel_file = filename
                    if "." not in filename:
                        rel_file = filename + ".md"
                    abs_link_url = os.path.dirname(os.path.join(self.base_docs_url, rel_file))
                    rel_link_url = os.path.join(
                        os.path.relpath(abs_link_url, abs_linker_url), os.path.basename(rel_file)
                    )
                    if title:
                        rel_link_url = rel_link_url + "#" + format_title
            else:
                for root, _dirs, files in os.walk(self.search_root):
                    for name in files:
                        if simplify(name) == simplify(filename):
                            abs_link_url = os.path.dirname(os.path.join(root, name))
                            rel_link_url = os.path.join(
                                os.path.relpath(abs_link_url, abs_linker_url), name
                            )
                            if title:
                                rel_link_url = rel_link_url + "#" + format_title
            if rel_link_url == "":
                log.warning(f"roamlinks_i18n unable to find {filename} in {self.search_root}")
                return whole_link
        else:
            rel_link_url = "#" + format_title

        rel_link_url = rel_link_url.replace("\\", "/")

        if filename:
            link = f"[{alias}](<{rel_link_url}>)" if alias else f"[{filename + title}](<{rel_link_url}>)"
        else:
            link = f"[{alias}](<{rel_link_url}>)" if alias else f"[{title}](<{rel_link_url}>)"

        if width and not height:
            link = f'{link}{{ width="{width}" }}'
        elif not width and height:
            link = f'{link}{{ height="{height}" }}'
        elif width and height:
            link = f'{link}{{ width="{width}"; height="{height}" }}'

        return link


def on_page_markdown(markdown, page, config, **kwargs):
    base_docs_url = config["docs_dir"]
    page_url = page.file.src_path
    return re.sub(ROAMLINK_RE, RoamLinkReplacer(base_docs_url, page_url), markdown)
