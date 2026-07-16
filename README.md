
# MediOps CRM + ERP Demo

A compact healthcare-focused CRM/ERP prototype for exploring sales, operations, inventory, and workflow automation in one place.

## What it demonstrates

### CRM
- Healthcare accounts and contacts
- Opportunity pipeline and stage updates
- Revenue forecasting
- Sales ownership and next actions
- Stale-opportunity alerts

### ERP
- Sales order creation
- Payment and shipping status
- Inventory levels
- Reorder thresholds
- Basic operational reporting

### Automation / AI concepts
- Low-stock alerts
- Stale-lead follow-up recommendations
- Won-deal handoff workflow
- Forecast prioritization
- Human-reviewed AI recommendations

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create a virtual environment:

```bash
python -m venv .venv
```

4. Activate it.

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

6. Start the app:

```bash
streamlit run app.py
```

The first run automatically creates `mediops_demo.db` and inserts sample data.

## Reset the sample database

Delete `mediops_demo.db`, then restart the application.

## Suggested walkthrough

1. Start on the Dashboard and explain the unified sales and operations view.
2. Open CRM Pipeline and move an opportunity to the next stage.
3. Add a new opportunity.
4. Open Inventory and show low-stock alerts.
5. Adjust inventory and explain the reorder workflow.
6. Open Workflow Automation and simulate a rules run.
7. Finish on Architecture and describe how you would productionize the system.

## Motivation

I built a lightweight healthcare CRM and ERP prototype to understand the complete operational flow. The CRM side tracks organizations, opportunities, pipeline stages, owners, expected revenue, and follow-up actions. The ERP side tracks orders, payments, shipping, products, and inventory. I also added workflow concepts for stale opportunities and low inventory. The prototype uses Streamlit and SQLite for speed, but I included a production architecture using APIs, PostgreSQL, role-based access, background jobs, integrations, audit logs, and monitoring.

## What this is:

- A workflow prototype
- A product and systems-thinking exercise
- A demonstration of CRM/ERP concepts
- A basis for discussing data, automation, integrations, permissions, and AI



# More About Each Screen

## Dashboard
This page gives leadership a combined view of open pipeline, probability-weighted forecast, order revenue, and inventory risk.

## CRM
An account is the organization we sell to. An opportunity is a potential deal with that account. The stage captures where the deal is in the sales process, while the owner and next action make accountability clear.

## ERP
Once a deal becomes an actual order, operations needs payment, shipping, product, and inventory information. That is where the ERP side begins.

## Automation
Rules handle deterministic tasks. For example, if no activity occurs for seven days, the system can create a follow-up task. If inventory falls below the reorder threshold, it can create a purchasing request.

## AI (To Do)
AI should assist rather than silently make high-risk changes. It can summarize account history, recommend a next action, flag anomalies, and answer natural-language questions. Important actions should remain reviewable and auditable.

## Productionization
For production I would separate the frontend, API, database, and background workers; use PostgreSQL; add role-based access; validation; audit logs; observability; testing; and secure integrations.
