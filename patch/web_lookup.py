"""LIVE WEB LOOKUP: when the verified library cannot answer a question, look it up on the open web.

It searches, keeps official UAE sources first (government and regulator sites), downloads the best pages,
and hands the most relevant paragraphs to the answer agent. The answer then cites those pages by address,
and is always labelled as coming from a live web search, not from the verified rule library.

Everything here fails soft: any network problem simply returns nothing and the caller falls back.
"""
import re
import time
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup

OFFICIAL = (".gov.ae", "vara.ae", "u.ae", "centralbank.ae", "rdc.gov.ae", "dubailand.gov.ae", "dlp.dubai.gov.ae",
            "visitdubai.com", "difc.ae", "difc.com", "adgm.com", "sca.gov.ae", "dfsa.ae", "dewa.gov.ae", "empower.ae")
SKIP = ("youtube.com", "facebook.com", "instagram.com", "tiktok.com", "linkedin.com", "twitter.com", "x.com",
        "pinterest.", "reddit.com", "quora.com")
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
           "Accept-Language": "en-US,en;q=0.9"}
_off_until = 0.0
_cache: dict[str, tuple[float, list]] = {}


def is_official(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == d.lstrip(".") or host.endswith(d if d.startswith(".") else "." + d) for d in OFFICIAL)


def _clean_link(href: str) -> str:
    if href.startswith("//"):
        href = "https:" + href
    if "duckduckgo.com/l/" in href:                      # DuckDuckGo wraps the real address
        real = parse_qs(urlparse(href).query).get("uddg", [""])[0]
        href = unquote(real) if real else href
    return href


def parse_results(html: str) -> list[dict]:
    """Reads a search results page (DuckDuckGo HTML or Bing) into [{url, title, snippet}]."""
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for res in soup.select("div.result, div.web-result"):
        a = res.select_one("a.result__a")
        if not a or not a.get("href"):
            continue
        sn = res.select_one(".result__snippet")
        out.append({"url": _clean_link(a["href"]), "title": a.get_text(" ", strip=True),
                    "snippet": sn.get_text(" ", strip=True) if sn else ""})
    if not out:
        for res in soup.select("li.b_algo"):
            a = res.select_one("h2 a")
            if not a or not a.get("href"):
                continue
            sn = res.select_one("p, .b_caption p")
            out.append({"url": a["href"], "title": a.get_text(" ", strip=True),
                        "snippet": sn.get_text(" ", strip=True) if sn else ""})
    seen, clean = set(), []
    for r in out:
        u = r["url"]
        if not u.startswith("http") or u in seen or any(s in u for s in SKIP) or u.lower().endswith(".pdf"):
            continue
        seen.add(u)
        clean.append(r)
    return clean


def search(query: str, timeout: float = 8) -> list[dict]:
    for url in (f"https://html.duckduckgo.com/html/?q={quote_plus(query)}&kl=ae-en",
                f"https://www.bing.com/search?q={quote_plus(query)}&cc=AE&setlang=en"):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200:
                results = parse_results(r.text)
                if results:
                    return results
        except Exception:
            continue
    return []


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]{3,}", text.lower())
            if w not in {"the", "and", "for", "what", "are", "how", "can", "does", "with", "from", "that", "this",
                         "dubai", "uae", "you", "your", "have", "need", "rules", "rule"}}


def best_paragraphs(html: str, question: str, max_chars: int = 1700) -> str:
    """The paragraphs of a page that share the most words with the question, in page order."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "form", "noscript", "svg", "aside"]):
        tag.decompose()
    parts = []
    for el in soup.find_all(["p", "li", "td", "h2", "h3"]):
        t = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
        if 40 <= len(t) <= 900:
            parts.append(t)
    if not parts:
        return ""
    q = _words(question)
    scored = sorted(range(len(parts)), key=lambda i: -len(q & _words(parts[i])))
    keep, used = [], 0
    for i in scored:
        if len(q & _words(parts[i])) == 0 or used + len(parts[i]) > max_chars:
            continue
        keep.append(i)
        used += len(parts[i])
    return " ".join(parts[i] for i in sorted(keep))


def lookup(question: str, max_pages: int = 3) -> list[dict]:
    """Returns up to max_pages web passages: [{eid, url, title, text, official}]. Empty list when unavailable."""
    global _off_until
    key = question.strip().lower()
    if key in _cache and time.time() - _cache[key][0] < 3600:
        return _cache[key][1]
    if time.time() < _off_until:
        return []
    results = search(f"{question} Dubai UAE official rules")
    if not results:
        _off_until = time.time() + 600                      # search not reachable right now: pause for 10 minutes
        return []
    results.sort(key=lambda r: 0 if is_official(r["url"]) else 1)     # official sources first, order otherwise kept
    passages = []
    for r in results[:6]:
        if len(passages) >= max_pages:
            break
        text = ""
        try:
            page = requests.get(r["url"], headers=HEADERS, timeout=7, stream=True)
            if page.status_code == 200 and "html" in page.headers.get("content-type", "html"):
                text = best_paragraphs(page.raw.read(400_000, decode_content=True).decode("utf-8", "ignore"), question)
        except Exception:
            text = ""
        text = text or r["snippet"]
        if len(text) < 60:
            continue
        passages.append({"eid": f"W{len(passages) + 1}", "url": r["url"], "title": r["title"][:140], "text": text,
                         "official": is_official(r["url"])})
    _cache[key] = (time.time(), passages)
    return passages
