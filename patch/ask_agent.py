"""ANSWER AGENT (the "Ask" tab).

How a question is answered:
1. Planner    builds up to three search phrasings from the question (plain wording -> rule wording).
2. Retriever  pulls the 10 best passages from the verified library (official documents + essentials briefs).
3. Answerer   writes a direct, complete answer using ONLY those passages, citing each fact like [E1].
4. Verifier   keeps only citations that point to a real passage and records how well the library covered it.
5. If the library does not fully cover the question, the Watcher searches the live web (official UAE
   sources first), the Reader pulls the relevant paragraphs, and the answer cites those pages. Only if the web
   has nothing either is careful general guidance given. Both are always labelled as NOT from the verified
   library, and no citation is ever invented.
"""
import os
import re
from urllib.parse import urlparse

from .. import config, llm, store


def retrieve(*a, **k):
    from . import checker
    return checker.retrieve(*a, **k)


def _evidence_block(evidence):
    from . import checker
    return checker._evidence_block(evidence)


# Extra search phrases for everyday wording, so a plain question finds the right rule passage.
_HINTS = [
    (("instagram", "tiktok", "facebook", "social", "advert", "ad ", "ads", "post", "billboard", "marketing", "promot", "influencer"),
     "real estate advertising permit Trakheesi QR code advert"),
    (("fee", "cost", "charge", "how much", "pay", "price", "percent", "%"),
     "DLD transfer fee registration fee 4% administration fee"),
    (("commission", "brokerage fee", "agent fee"), "broker commission 2% sale price brokerage agreement Form A Form B"),
    (("broker", "agent", "rera card", "licen", "register as"), "broker registration RERA broker card By-law 85 of 2006 DREI exam"),
    (("ejari", "register the lease", "tenancy contract", "register my contract"), "Ejari tenancy contract registration mandatory RERA"),
    (("rent increase", "increase rent", "raise rent", "raise the rent", "rental index", "rent cap", "increase the rent"),
     "maximum rent increase Decree 43 of 2013 rental index percentage"),
    (("evict", "vacate", "leave the property", "kick out", "notice to tenant", "move out"),
     "eviction notice 12 months notary public Article 25 tenancy law"),
    (("deposit", "maintenance", "sublet", "repair"), "security deposit maintenance subletting landlord tenant obligations"),
    (("dispute", "rdc", "complain", "sue", "court"), "Rental Disputes Center filing fee 3.5% annual rent"),
    (("escrow", "off-plan", "off plan", "offplan", "developer", "oqood", "handover"),
     "escrow account off-plan Law 8 of 2007 interim register Oqood developer"),
    (("default", "stop paying", "cancel", "refund", "terminate"), "off-plan buyer default Article 11 Law 13 of 2008 developer retain percentage"),
    (("visa", "golden", "residency", "residence"), "Golden Visa property investment AED 2 million residence"),
    (("mortgage", "loan", "down payment", "ltv", "finance", "bank"), "mortgage loan-to-value down payment Central Bank mortgage registration fee"),
    (("token", "crypto", "vara", "virtual asset", "blockchain", "fraction"), "VARA licence tokenized real estate Asset-Referenced Virtual Asset issuance"),
    (("airbnb", "holiday home", "short-term", "short term", "booking.com", "nightly"), "holiday home permit DET short-term rental licence"),
    (("service charge", "owners association", "mollak", "community fee", "defect", "snag"),
     "service charges jointly owned property Law 6 of 2019 Mollak defects liability"),
    (("foreign", "expat", "freehold", "own property", "ownership", "title deed", "buy a", "buying", "sell", "selling"),
     "freehold ownership designated areas title deed registration Form F NOC transfer"),
    (("aml", "kyc", "cash", "money laundering", "source of funds", "identity"), "AML KYC cash transaction AED 55,000 goAML real estate activity report"),
    (("tax", "vat"), "property tax VAT residential commercial 5% housing fee"),
]


def _search_queries(question: str) -> list[str]:
    """The question itself plus up to two extra phrasings built from the topics it mentions."""
    q = " " + question.lower() + " "
    extra = [phrase for keys, phrase in _HINTS if any(k in q for k in keys)]
    return [question] + extra[:2]


_ASK_SYSTEM = """You are RuleWatch's answer agent for Dubai / UAE real estate rules.
Answer the question using ONLY the passages given. Be direct and complete:
- Start with the direct answer (yes / no / the number / the rule) in the first sentence.
- Then give the concrete details a professional needs: exact percentages, amounts in AED, deadlines, notice periods,
  the law or article name, who is responsible, and the penalty if the passages state one.
- When a rule has several tiers or conditions, list ALL of them, each on its own line starting with "• ".
- Cite the passage id after each fact, like [E1]. Never cite a passage that does not support the fact.
- Plain text only (no markdown, no tables). 3 to 9 short lines.
Set "covered" to "full" if the passages answer the question, "partial" if they answer only part of it,
and "none" if they do not answer it at all. For "partial", answer the part you can and say what is missing.
Never invent a rule, number or citation."""


def _tidy(text: str) -> str:
    """Each bullet on its own line, no markdown marks, no blank-line pile-ups."""
    text = re.sub(r"\*\*|__|^#+\s*", "", str(text), flags=re.M)
    text = re.sub(r"[ \t]*\n?[ \t]*•[ \t]*", "\n• ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _web_answer(question: str, lang: str, run_id: str) -> tuple[str, list] | None:
    """Live web lookup for questions the library does not cover. The answer is written ONLY from the pages
    found, with each fact tied to a page. Returns (answer, sources) or None when the web is not reachable."""
    if llm.is_mock() or os.getenv("WEB_LOOKUP", "on").strip().lower() == "off":
        return None
    try:
        from .. import web_lookup
        store.log(run_id, "Watcher", "Not in the library yet: searching official sources on the live web")
        pages = web_lookup.lookup(question)
        if not pages:
            store.log(run_id, "Watcher", "Live web search returned nothing usable")
            return None
        n_official = sum(1 for p in pages if p["official"])
        store.log(run_id, "Reader", f"Reading {len(pages)} web page(s), {n_official} from official sources: "
                  + "; ".join((urlparse(p['url']).hostname or '') for p in pages))
        block = "\n\n".join(f"[{p['eid']}] {'OFFICIAL SOURCE' if p['official'] else 'other source'} | {p['title']} | "
                            f"{p['url']}\n{p['text']}" for p in pages)
        out = llm.chat_json(
            """You answer questions about Dubai / UAE real estate rules using ONLY the web passages given.
- Direct answer first, then the key figures, deadlines and law names the passages state, each extra point on its
  own line starting with "• ". Plain text, 3 to 8 lines.
- Cite the passage after each fact, like [W1]. Prefer passages marked OFFICIAL SOURCE.
- Use only what the passages say. Never add a number, law name or deadline that is not in them.
Set "found" to true only if the passages really answer the question.""",
            f"""Question: {question}

Web passages:
{block}

Return JSON: {{"answer": "answer in {lang} with [W#] citations", "evidence": ["W1"], "found": true}}""",
            mock=lambda: {"answer": "", "evidence": [], "found": False})
        by_id = {p["eid"]: p for p in pages}
        answer = _tidy(out.get("answer", ""))
        cited = [c for c in out.get("evidence", []) if c in by_id]
        for c in re.findall(r"\[(W\d+)\]", answer):
            if c in by_id and c not in cited:
                cited.append(c)
        if not out.get("found") or not cited or len(answer) < 40:
            store.log(run_id, "Verifier", "The web pages found do not answer the question")
            return None
        store.log(run_id, "Verifier", f"Web answer cites {len(cited)} real page(s)")
        sources = [{"eid": c, "title": by_id[c]["title"], "page": 1, "url": by_id[c]["url"],
                    "regulator": ("Official web source" if by_id[c]["official"] else "Web source") + ": "
                                 + (urlparse(by_id[c]["url"]).hostname or ""),
                    "kind": "html", "quote": by_id[c]["text"][:350]} for c in cited]
        return answer, sources
    except Exception as e:
        store.log(run_id, "Watcher", f"Live web search not available ({str(e)[:70]})")
        return None


def _general_answer(question: str, lang: str, run_id: str, partial: str = "") -> str | None:
    """Last resort when neither the library nor the live web covers the question: careful general guidance,
    clearly labelled, that points the user to the right regulator instead of guessing figures."""
    try:
        out = llm.chat_json(
            """You are an expert on Dubai and UAE real estate regulation (DLD, RERA, VARA, Dubai tenancy and
property law, UAE federal rules). The verified rule library did not cover this question, so give careful general
guidance from your professional knowledge.
- Direct answer first (the general position), then 2 to 5 practical points, each on its own line starting with "• ".
- Accuracy matters more than detail. State a specific number, fee, deadline, penalty or law/article number ONLY if
  you are certain of it; otherwise describe the rule in words and say the exact figure must be confirmed.
- Always finish with one line naming which regulator or official service to confirm with (for example DLD, RERA,
  the Rental Disputes Center, VARA, DET, the UAE Central Bank, the Federal Tax Authority).
- Plain text, no markdown.
If the question is not about UAE real estate, property, tenancy or its regulation, reply only that RuleWatch
covers Dubai / UAE real estate rules and suggest a related question it can answer.""",
            f"""Question: {question}
{('What the verified library already said: ' + partial) if partial else ''}

Return JSON: {{"answer": "the answer in {lang}"}}""",
            mock=lambda: {"answer": ""}, temperature=0.1)
        text = _tidy(out.get("answer", ""))
        return text or None
    except Exception as e:
        store.log(run_id, "Manager", f"General answer unavailable ({str(e)[:80]})")
        return None


def ask(question: str, language: str, run_id: str) -> dict:
    queries = _search_queries(question)
    if len(queries) > 1:
        store.log(run_id, "Planner", f"Searching the library {len(queries)} ways for this question")
    evidence = retrieve(queries, run_id, per_query=4, limit=10)
    if not evidence:
        return {"answer": "No rules are loaded yet. Run the Watcher or upload a PDF first.", "sources": []}

    def mock():
        return {"answer": f"[Demo answer] The closest rule passage is {evidence[0]['eid']}.", "evidence": [evidence[0]["eid"]],
                "covered": "full"}
    ar = language == "ar"
    lang = "Arabic" if ar else "simple English"
    out = llm.chat_json(
        _ASK_SYSTEM,
        f"""Question: {question}

Passages:
{_evidence_block(evidence)}

Return JSON: {{"answer": "answer in {lang} with [E#] citations", "evidence": ["E1"], "covered": "full | partial | none"}}""",
        mock=mock)
    by_id = {e["eid"]: e for e in evidence}
    answer = _tidy(out.get("answer", ""))
    cited = [c for c in out.get("evidence", []) if c in by_id]
    for c in re.findall(r"\[(E\d+)\]", answer):          # also count ids used inside the text
        if c in by_id and c not in cited:
            cited.append(c)
    covered = str(out.get("covered", "full")).strip().lower()
    if covered not in ("full", "partial", "none"):
        covered = "full"
    if not cited or not answer:
        covered = "none"
    store.log(run_id, "Verifier", f"Answer cites {len(cited)} real passage(s); library coverage: {covered}")

    sources = [{"eid": c, "title": by_id[c]["title"], "page": by_id[c]["page"], "url": by_id[c]["url"],
                "regulator": by_id[c]["regulator"], "kind": by_id[c].get("kind"), "quote": by_id[c]["text"][:350]}
               for c in cited]
    if covered == "full":
        return {"answer": answer, "sources": sources, "coverage": "verified"}

    # The verified library does not fully cover it. Try the live web (cited by page), then careful general
    # guidance. Either way the extra part is labelled, and no citation is ever invented.
    web = _web_answer(question, lang, run_id)
    extra, web_sources = (web if web else (None, []))
    from_web = bool(extra)
    if not extra:
        store.log(run_id, "Manager", "Adding general guidance, labelled as unverified")
        extra = _general_answer(question, lang, run_id, partial=answer if covered == "partial" else "")
    if ar:
        head = "من مكتبة القواعد الموثقة:"
        none_msg = "لم أجد إجابة في مكتبة القواعد الموثقة."
        label = ("من بحث مباشر على الإنترنت (ليس من مكتبة القواعد الموثقة بعد، المصادر في الأسفل):" if from_web else
                 "إرشاد عام (غير مأخوذ من مكتبة القواعد الموثقة، يرجى التأكد من الجهة التنظيمية):")
    else:
        head = "From the verified rule library:"
        none_msg = "The verified rule library does not cover this question yet."
        label = ("From a live web search (not yet in RuleWatch's verified rule library; pages listed below):" if from_web
                 else "General guidance (not from RuleWatch's verified rule library, confirm with the regulator):")
    if covered == "partial" and extra:
        text, sources = f"{head}\n{answer}\n\n{label}\n{extra}", sources + web_sources
    elif covered == "partial":
        text = answer
    elif extra:
        text, sources = f"{label}\n{extra}", web_sources
    else:
        text, sources = none_msg, []
    return {"answer": text, "sources": sources,
            "coverage": "partial" if covered == "partial" else ("web" if from_web else "general")}
