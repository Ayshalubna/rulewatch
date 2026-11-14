"""Applies the RuleWatch source patches on top of the packed app (run once during the Docker build).

    python patch/apply.py /app

- rulewatch/knowledge.py          essentials briefs (plain-English reference notes, loaded at start-up)
- rulewatch/agents/ask_agent.py   the improved answer agent for the Ask tab
- rulewatch/web_lookup.py         live web lookup (official UAE sources first) for questions the library lacks
- frontend/dist/enhance.js/.css   the daylight interface layer (3D showcase, buttons) and the rule calculators
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
        raise SystemExit(f"PATCH FAILED: expected text not found in {path}")
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

print("RuleWatch patches applied.")
