# 🔔 RuleWatch

**AI agents that watch Dubai real estate rules (DLD, RERA, VARA and Dubai law), and check a business's plans against the exact clause.**

Real estate rules in Dubai change often. Agencies, developers, landlords and proptech startups find out late and can get fined. RuleWatch fixes this:

- **Watches** official sources every day, by itself, and spots new and **updated** rules (PDFs and web pages).
- **Reads** each document from start to end and explains it in simple English and Arabic.
- **Alerts** each registered business only about the rules that affect it.
- **Checks a plan**: describe what you want to do, get a 🔴 / 🟡 / 🟢 verdict for each action with the official clause quoted.
- **Answers questions** using only the official documents, citing the source for every claim.

> RuleWatch gives early warnings, not legal advice.

## How it works: two multi-agent workflows (LangGraph)

```
Daily watch:   Watcher → Reader → Impact → Alert
Plan check:    Planner → Retriever → Checker → Verifier → Reporter
```

| Agent | Job |
|---|---|
| Watcher | Checks official pages and documents, finds new or changed rules, keeps only the newest version of each file |
| Reader | Reads whole documents part by part (a fast model pulls rules from each part, a larger model writes the summary in English and Arabic) |
| Impact | Decides which of 11 business types each rule affects, how serious it is, and what each must do |
| Alert | Notifies affected businesses in the app and by email |
| Planner | Splits a business plan into separate actions and search questions |
| Retriever | Hybrid search (multilingual meaning search + keywords), boosted by the topics that business type cares about |
| Checker | Gives each action a signal, citing rule passages |
| Verifier | Citation guard: removes any citation that doesn't match a real passage; an uncited red warning is downgraded, so the AI can't invent rules |
| Reporter | Writes the overall verdict in English or Arabic |

**Coverage:** 11 business types (agencies, developers, property managers, landlords, holiday-home operators, owners associations, tokenization startups, mortgage brokers and banks, valuation firms, facility management, tenants and buyers) across 14 topics.

**Official sources:** Dubai Legislation Portal (escrow law, off-plan register law, tenancy law, rent increase decree, jointly owned property law, holiday homes rules), DLD brokerage guide and legislation, and VARA laws and rulebooks for property tokenization.

**Production features:** automatic AI model fallback when a free-tier limit is reached, answer cache, per-visitor rate limit, admin lock for anything that changes data, live agent progress in the browser, quality test on 26 real-life situations, Arabic right-to-left interface.

**Tech:** Python, LangGraph, FastAPI, Groq (GPT-OSS 120B, GPT-OSS 20B and Qwen 3.8 with automatic fallback), fastembed multilingual embeddings, SQLite, React, TypeScript, Tailwind CSS, Docker.

---

## Run it on Windows

One time: double-click **setup.bat**. Then put your free Groq key (https://console.groq.com/keys) in the `.env` file:

```
LLM_PROVIDER=groq
LLM_API_KEY=your_key
ADMIN_TOKEN=choose_a_password
```

- **build_rules.bat**: loads the official rules (20–40 minutes the first time).
- **start_web.bat**: opens the RuleWatch website at http://localhost:8000.
- **run_daily_check.bat**: the daily check (add it to Windows Task Scheduler for 8:00 every morning).

## Put it online (free, Hugging Face Spaces)

1. Sign in at https://huggingface.co → **New Space** → name `rulewatch` → SDK **Docker** → **Blank** → Create.
2. **Files → Add file → Upload files**: drag in everything inside the `deploy` folder (made by `make_deploy.bat`). Commit.
3. **Settings → Variables and secrets → New secret**: `LLM_PROVIDER` = `groq`, `LLM_API_KEY` = your Groq key, `ADMIN_TOKEN` = a password you choose.
4. Wait for the build (about 5 minutes). Your site is live at `https://<your-name>-rulewatch.hf.space`.

The same Dockerfile works on Render, Railway or any Docker host (it listens on `$PORT`).

## Develop

```
pip install -r requirements.txt
uvicorn server:app --reload            # API + website on :8000
cd frontend && npm install && npm run dev   # live-reload website on :5173
python -m tests.test_pipeline          # end-to-end test, no API key needed
python -m rulewatch.evaluate           # quality test on the 26 situations
```
