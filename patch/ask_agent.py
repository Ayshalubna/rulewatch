"""ANSWER AGENT (the "Ask" tab).

How a question is answered:
1. Planner    builds up to three search phrasings from the question (plain wording -> rule wording).
2. Retriever  pulls the 10 best passages from the verified library (official documents + essentials briefs).
3. Answerer   writes a direct, complete answer using ONLY those passages, citing each fact like [E1].
4. Verifier   keeps only citations that point to a real passage and records how well the library covered it.
5. If the library does not fully cover the question, a live web lookup (official sources first) or, failing
   that, general guidance is added. It is always labelled as NOT from the verified library. No citation is
   ever invented.
"""
import os
import re
import time

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


_web_off_until = 0.0


def _web_answer(question: str, lang: str, run_id: str) -> str | None:
    """Live web lookup for questions the library does not cover (uses the AI provider's built-in web search
    model when the account has one). Returns None when it is not available, so the caller falls back."""
    global _web_off_until
    model = os.getenv("WEB_SEARCH_MODEL", "groq/compound-mini").strip()
    if llm.is_mock() or not model or model.lower() == "off" or time.time() < _web_off_until:
        return None
    if "groq" not in config.LLM_BASE_URL and not os.getenv("WEB_SEARCH_MODEL"):
        return None
    try:
        store.log(run_id, "Watcher", "Not in the library yet: searching official sources on the live web")
        client = llm._get_client().with_options(timeout=45, max_retries=0)
        r = client.chat.completions.create(
            model=model, temperature=0.1,
            messages=[
                {"role": "system", "content":
                    "You answer questions about Dubai / UAE real estate rules. Search the web and rely on official "
                    "sources first (dubailand.gov.ae, dlp.dubai.gov.ae, vara.ae, u.ae, centralbank.ae, "
                    "visitdubai.com / det.gov.ae, mof.gov.ae). Give the direct answer first, then the key figures, "
                    "deadlines and law names, each extra point on its own line starting with '• '. Plain text only, "
                    "no markdown, 3 to 8 lines. Finish with a line 'Sources:' followed by the page addresses you used. "
                    "If the question is not about UAE real estate or its regulation, say RuleWatch only covers that."},
                {"role": "user", "content": f"{question}\n\nAnswer in {lang}."}])
        text = (r.choices[0].message.content or "").strip()
        text = re.sub(r"\*\*|__|^#+\s*", "", text, flags=re.M)
        if len(text) < 40:
            return None
        store.log(run_id, "Watcher", "Found an answer on the live web")
        return text[:2200]
    except Exception as e:
        _web_off_until = time.time() + 1800     # not available on this account right now: skip for 30 minutes
        store.log(run_id, "Watcher", f"Live web search not available ({str(e)[:70]})")
        return None


def _general_answer(question: str, lang: str, run_id: str, partial: str = "") -> str | None:
    """Fallback when the verified library does not cover the question: a clearly-labelled general answer."""
    try:
        out = llm.chat_json(
            """You are an expert on Dubai and UAE real estate regulation (DLD, RERA, VARA, Dubai tenancy and
property law, UAE federal rules). The verified rule library did not cover this question, so answer from your own
professional knowledge. Be specific and useful: give the direct answer first, then the key figures, deadlines,
law names and practical steps, each extra point on its own line starting with "• ". Plain text, 3 to 8 lines.
If you are not sure of an exact figure, say it is approximate and tell the user which regulator to confirm it with.
If the question is not about UAE real estate, property, tenancy or its regulation, reply that RuleWatch only
covers Dubai / UAE real estate rules and suggest a related question it can answer.""",
            f"""Question: {question}
{('What the verified library already said: ' + partial) if partial else ''}

Return JSON: {{"answer": "the answer in {lang}"}}""",
            mock=lambda: {"answer": ""}, temperature=0.2)
        text = str(out.get("answer", "")).strip()
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
    answer = str(out.get("answer", "")).strip()
    cited = [c for c in out.get("evidence", []) if c in by_id]
    for c in re.findall(r"\[(E\d+)\]", answer):          # also count ids used inside the text
        if c in by_id and c not in cited:
            cited.append(c)
    covered = str(out.get("covered", "full")).strip().lower()
    if not cited or not answer:
        covered = "none"
    store.log(run_id, "Verifier", f"Answer cites {len(cited)} real passage(s); library coverage: {covered}")

    sources = [{"eid": c, "title": by_id[c]["title"], "page": by_id[c]["page"], "url": by_id[c]["url"],
                "regulator": by_id[c]["regulator"], "kind": by_id[c].get("kind"), "quote": by_id[c]["text"][:350]}
               for c in cited]
    if covered == "full":
        return {"answer": answer, "sources": sources, "coverage": "verified"}

    # The verified library does not fully cover it: add a clearly-labelled general answer, never a made-up citation.
    extra = _web_answer(question, lang, run_id)
    from_web = bool(extra)
    if not extra:
        store.log(run_id, "Manager", "Library does not fully cover this; adding general guidance (labelled as unverified)")
        extra = _general_answer(question, lang, run_id, partial=answer if covered == "partial" else "")
    if ar and from_web:
        label = "من بحث مباشر على الإنترنت (ليس من مكتبة القواعد الموثقة بعد، المصادر مذكورة في الأسفل):"
        head = "من مكتبة القواعد الموثقة:"
        none_msg = "لم أجد إجابة في مكتبة القواعد الموثقة."
    elif from_web:
        label = "From a live web search (not yet in RuleWatch's verified rule library; sources listed below):"
        head = "From the verified rule library:"
        none_msg = "The verified rule library does not cover this question yet."
    elif ar:
        label = "إرشاد عام (غير مأخوذ من مكتبة القواعد الموثقة، يرجى التأكد من الجهة التنظيمية):"
        head = "من مكتبة القواعد الموثقة:"
        none_msg = "لم أجد إجابة في مكتبة القواعد الموثقة."
    else:
        label = "General guidance (not from RuleWatch's verified rule library, confirm with the regulator):"
        head = "From the verified rule library:"
        none_msg = "The verified rule library does not cover this question yet."
    if covered == "partial" and extra:
        text = f"{head}\n{answer}\n\n{label}\n{extra}"
    elif covered == "partial":
        text = answer
    elif extra:
        text, sources = f"{label}\n{extra}", []
    else:
        text, sources = none_msg, []
    return {"answer": text, "sources": sources,
            "coverage": "partial" if covered == "partial" else ("web" if from_web else "general")}
