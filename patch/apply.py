"""Applies the RuleWatch source patches on top of the packed app (run once during the Docker build).

    python patch/apply.py /app

- rulewatch/knowledge.py          essentials briefs (plain-English reference notes, loaded at start-up)
- rulewatch/agents/ask_agent.py   the improved answer agent for the Ask tab
- rulewatch/web_lookup.py         live web lookup (official UAE sources first) for questions the library lacks
- frontend/dist/enhance.js/.css   the daylight interface layer (3D showcase, buttons) and the rule calculators
- data/eval_seed.json             the last full quality test, shown on the Coverage & quality page
- recolour step                   turns the packed dark theme into the light "Gulf morning" palette
The script stops the build if anything it expects to change is missing, so a bad patch can never go live.
"""
import shutil
import sys
from pathlib import Path

here = Path(__file__).parent
app = Path(sys.argv[1] if len(sys.argv) > 1 else "/app")


def edit(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"PATCH FAILED: expected text not found in {path}: {old[:70]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


shutil.copy(here / "knowledge.py", app / "rulewatch" / "knowledge.py")
shutil.copy(here / "ask_agent.py", app / "rulewatch" / "agents" / "ask_agent.py")
shutil.copy(here / "web_lookup.py", app / "rulewatch" / "web_lookup.py")
shutil.copy(here / "enhance.js", app / "frontend" / "dist" / "enhance.js")
shutil.copy(here / "enhance.css", app / "frontend" / "dist" / "enhance.css")

# 1) the Ask tab uses the improved answer agent
checker = app / "rulewatch" / "agents" / "checker.py"
text = checker.read_text(encoding="utf-8")
if "from .ask_agent import ask" not in text:
    if "def ask(question: str, language: str, run_id: str)" not in text:
        raise SystemExit("PATCH FAILED: checker.ask not found")
    checker.write_text(text.rstrip() + "\n\n\nfrom .ask_agent import ask  # noqa: E402,F811  improved answer agent\n",
                       encoding="utf-8")

# 2) load the essentials briefs at start-up
server = app / "server.py"
edit(server,
     '''def warm_up():
    threading.Thread(target=lambda: embed.embed(["warm up"]), daemon=True).start()''',
     '''def warm_up():
    def work():
        embed.embed(["warm up"])
        try:    # load the plain-English essentials briefs into the library (only when missing or changed)
            from rulewatch import knowledge
            n = knowledge.ensure_loaded()
            if n:
                print(f"Essentials briefs loaded: {n}", flush=True)
        except Exception as e:
            print(f"Essentials briefs could not be loaded: {e!r}"[:300], flush=True)
    threading.Thread(target=work, daemon=True).start()''')

# 3) the home page counts only official documents (not our own briefs)
edit(server,
     '''    docs = store.list_documents(status="read")
    return {
        "business_types"''',
     '''    docs = store.list_documents(status="read")
    official = [d for d in docs if "#rulewatch-essentials" not in (d.get("url") or "")]   # briefs are our own notes
    return {
        "business_types"''')
edit(server, '''            "documents": len(docs),''', '''            "documents": len(official),''')

# 4) the website loads the 3D layer
index = app / "frontend" / "dist" / "index.html"
html = index.read_text(encoding="utf-8")
if "enhance.js" not in html:
    if "</head>" not in html:
        raise SystemExit("PATCH FAILED: index.html has no </head>")
    index.write_text(html.replace(
        "</head>", '  <link rel="stylesheet" href="/enhance.css?v=5">\n    <script defer src="/enhance.js?v=5"></script>\n  </head>', 1),
        encoding="utf-8")

# 5) recolour the packed stylesheet and script: dark teal + brass -> light "Gulf morning" (haze, white, ink, ultramarine)
PALETTE = {
    "0e191e": "e9eef5", "142329": "ffffff", "12222a": "ffffff", "22363e": "d0d9e5", "33505a": "b0bed0",
    "c8a15a": "14213d", "e3c88e": "2f56e0", "1a1408": "ffffff", "efe8dc": "0a101c", "e4ded2": "0e1726",
    "cdbfa7": "334155", "6d8286": "647287", "9aabab": "475569",
    "f07560": "c8322a", "ebb650": "b0740c", "5dc796": "16875a", "b9a0f0": "6d4fd1", "7fc6d0": "1f8fa3",
}
EXTRA = {"rgba(0,0,0,.65)": "rgba(27,42,74,.2)", "#0000008c": "#1b2a4a33", "#0009": "#1b2a4a2e",
         'content="#0D3B33"': 'content="#E9EEF5"'}


def recolour(text: str) -> str:
    import re

    def trip(h):
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    for old, new in PALETTE.items():
        text = re.sub("#" + old, "#" + new, text, flags=re.I)
        o, n = trip(old), trip(new)
        text = text.replace("rgb(%d %d %d" % o, "rgb(%d %d %d" % n)
        text = text.replace("rgba(%d,%d,%d," % o, "rgba(%d,%d,%d," % n)
    for old, new in EXTRA.items():
        text = text.replace(old, new)
    return text


dist = app / "frontend" / "dist"
marker = dist / ".recoloured"
if not marker.exists():
    css_files = list((dist / "assets").glob("*.css"))
    if not any("rgb(14 25 30" in f.read_text(encoding="utf-8") for f in css_files):
        raise SystemExit("PATCH FAILED: the packed stylesheet does not have the colours the recolour step expects")
    for f in css_files + list((dist / "assets").glob("*.js")) + [index]:
        f.write_text(recolour(f.read_text(encoding="utf-8")), encoding="utf-8")
    marker.write_text("gulf-morning", encoding="utf-8")

# 6) friendlier visitor limit: 120 per hour, the built-in example situations are free (their answers are cached),
#    and the message says when the visitor can try again
edit(server, '''RATE = int(os.getenv("PUBLIC_RATE_LIMIT", "30"))''', '''RATE = int(os.getenv("PUBLIC_RATE_LIMIT", "120"))''')
edit(server,
     '''def _rate_limit(request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "?").split(",")[0]
    q, now = _hits[ip], time.time()
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= RATE:
        raise HTTPException(429, "Hourly limit reached for this visitor. Please try again later.")
    q.append(now)''',
     '''_FREE_PLANS = {" ".join(str(s.get("plan", "")).split()).lower() for s in SCENARIOS}


def _rate_limit(request: Request, text: str = ""):
    if text and " ".join(text.split()).lower() in _FREE_PLANS:   # built-in examples are cached: no AI cost
        return
    ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "?").split(",")[0].strip()
    q, now = _hits[ip], time.time()
    while q and now - q[0] > 3600:
        q.popleft()
    if len(q) >= RATE:
        wait = max(1, int((3600 - (now - q[0])) // 60) + 1)
        raise HTTPException(429, f"You have used this hour's {RATE} free checks and questions. "
                                 f"You can run more in about {wait} minute{'s' if wait != 1 else ''}; "
                                 f"the built-in example situations still work now.")
    q.append(now)''')
edit(server, '''def check(body: CheckIn, request: Request):
    _rate_limit(request)''', '''def check(body: CheckIn, request: Request):
    _rate_limit(request, body.plan)''')

# 7) Businesses & alerts works for every visitor: adding a business is public (rate-limited, emails never shown),
#    a new business at once gets alerts for every rule already in force that affects it, and three demo
#    businesses are created on first start so the page is never empty
edit(server,
     '''@app.post("/api/companies")
def add_company(body: CompanyIn, x_admin_token: str | None = Header(None)):
    _admin(x_admin_token)
    if body.type not in config.COMPANY_TYPES:
        raise HTTPException(400, "Unknown business type")
    return {"id": store.add_company(body.name.strip(), body.type, body.activities.strip(), body.email.strip())}''',
     r'''def _backfill_alerts(company_id: int, ctype: str, name: str) -> int:
    """Alerts for the rules already in force that affect this type of business (no AI call needed)."""
    icons, n = {"high": "\U0001F534", "medium": "\U0001F7E1", "low": "\U0001F7E2"}, 0
    for d in store.list_documents(status="read"):
        todo = (d.get("affects") or {}).get(ctype)
        if not todo or "#rulewatch-essentials" in (d.get("url") or ""):
            continue
        store.add_alert(company_id, d["id"],
                        f"{icons.get(d.get('severity'), icons['medium'])} In force: {d['regulator']} rule: {d['title']}\n"
                        f"What it says: {d.get('summary_en') or ''}\n"
                        f"What {name} should do: {todo}\nOfficial source: {d['url']}")
        n += 1
    return n


DEMO_COMPANIES = [
    ("Marina Gate Realty (demo)", "Real estate agency / broker", "Sells and rents apartments in Dubai Marina, advertises on Instagram"),
    ("Creek Horizon Developments (demo)", "Developer", "Launching an off-plan tower in Dubai Creek Harbour"),
    ("Palm Stays Holiday Homes (demo)", "Holiday homes / short-term rental operator", "Runs 40 short-stay apartments on Airbnb"),
]


def seed_demo_companies():
    if store.list_companies():
        return
    for name, ctype, what in DEMO_COMPANIES:
        if ctype in config.COMPANY_TYPES:
            cid = store.add_company(name, ctype, what, "")
            _backfill_alerts(cid, ctype, name)


@app.post("/api/companies")
def add_company(body: CompanyIn, request: Request, x_admin_token: str | None = Header(None)):
    admin = bool(ADMIN_TOKEN) and x_admin_token == ADMIN_TOKEN
    if not admin:
        _rate_limit(request)
        if len(store.list_companies()) >= 300:
            raise HTTPException(429, "The demo list of businesses is full. Please try the plan checker instead.")
    if body.type not in config.COMPANY_TYPES:
        raise HTTPException(400, "Unknown business type")
    name = body.name.strip()[:120]
    cid = store.add_company(name, body.type, body.activities.strip()[:500], body.email.strip()[:200])
    return {"id": cid, "alerts": _backfill_alerts(cid, body.type, name)}''')
edit(server, '''@app.get("/api/companies")
def companies():
    return store.list_companies()''', '''@app.get("/api/companies")
def companies():
    seed_demo_companies()
    return [{**c, "email": ("set" if c.get("email") else "")} for c in store.list_companies()]   # never show emails''')
edit(server, '''@app.get("/api/alerts")
def alerts():
    return store.list_alerts()[:100]''', '''@app.get("/api/alerts")
def alerts():
    seed_demo_companies()
    return store.list_alerts()[:100]''')

# 8) the Coverage & quality page shows the last full quality test (26 situations on the live app, 14 Nov 2026)
#    until a newer test is run from the admin panel
shutil.copy(here / "eval_seed.json", app / "data" / "eval_seed.json")
edit(server, '''    last = store.last_eval()
    return {"coverage": coverage''', '''    last = store.last_eval()
    if not last:   # show the last full test run on the live app until a newer one is run
        seed = Path(__file__).parent / "data" / "eval_seed.json"
        if seed.exists():
            import json as _json
            last = _json.loads(seed.read_text(encoding="utf-8"))
    return {"coverage": coverage''')

print("RuleWatch patches applied.")
