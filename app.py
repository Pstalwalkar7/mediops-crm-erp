
import sqlite3
from datetime import date, timedelta

import pandas as pd
import streamlit as st

DB_PATH = "mediops_demo.db"

st.set_page_config(
    page_title="MediOps CRM + ERP Demo",
    page_icon="🏥",
    layout="wide",
)

PIPELINE_STAGES = ["New Lead", "Qualified", "Demo Scheduled", "Proposal", "Negotiation", "Won", "Lost"]
STAGE_PROBABILITY = {
    "New Lead": 0.10,
    "Qualified": 0.25,
    "Demo Scheduled": 0.40,
    "Proposal": 0.60,
    "Negotiation": 0.80,
    "Won": 1.00,
    "Lost": 0.00,
}


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            account_type TEXT NOT NULL,
            city TEXT,
            state TEXT,
            contact_name TEXT,
            contact_email TEXT,
            status TEXT DEFAULT 'Active'
        );

        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            title TEXT NOT NULL,
            stage TEXT NOT NULL,
            value REAL NOT NULL,
            expected_close TEXT,
            owner TEXT,
            next_action TEXT,
            last_activity TEXT,
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            unit_price REAL NOT NULL,
            stock_qty INTEGER NOT NULL,
            reorder_level INTEGER NOT NULL,
            supplier TEXT
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            total REAL NOT NULL,
            payment_status TEXT NOT NULL,
            shipping_status TEXT NOT NULL,
            FOREIGN KEY(account_id) REFERENCES accounts(id)
        );

        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id INTEGER,
            activity_date TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY(opportunity_id) REFERENCES opportunities(id)
        );
        """
    )

    if cur.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0:
        accounts = [
            ("Desert Valley Pharmacy", "Pharmacy", "Phoenix", "AZ", "Lisa Morgan", "lisa@desertvalley.example", "Active"),
            ("Sunrise Surgical Center", "Surgical Center", "Scottsdale", "AZ", "Dr. Maya Chen", "maya@sunrise.example", "Active"),
            ("Mesa Community Hospital", "Hospital", "Mesa", "AZ", "James Patel", "james@mesa.example", "Active"),
            ("Southwest Infusion Clinic", "Clinic", "Tempe", "AZ", "Rachel Kim", "rachel@swic.example", "Prospect"),
            ("Canyon Health Network", "Health Network", "Chandler", "AZ", "Omar Wilson", "omar@canyon.example", "Active"),
            ("Copper State Pharmacy", "Pharmacy", "Gilbert", "AZ", "Anna Singh", "anna@copperstate.example", "Prospect"),
        ]
        cur.executemany(
            """INSERT INTO accounts
            (name, account_type, city, state, contact_name, contact_email, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            accounts,
        )

        today = date.today()
        opportunities = [
            (1, "IV Therapy Supply Expansion", "Proposal", 48000, str(today + timedelta(days=18)), "Alex Rivera", "Confirm purchasing committee review", str(today - timedelta(days=2))),
            (2, "Surgical Anesthesia Products", "Negotiation", 82000, str(today + timedelta(days=10)), "Priya Shah", "Send revised pricing", str(today - timedelta(days=1))),
            (3, "Hospital Formulary Pilot", "Demo Scheduled", 120000, str(today + timedelta(days=45)), "Alex Rivera", "Prepare product demo", str(today - timedelta(days=4))),
            (4, "Clinic Injectable Supply", "Qualified", 36000, str(today + timedelta(days=32)), "Jordan Lee", "Schedule discovery call", str(today - timedelta(days=8))),
            (5, "Network-Wide Distribution Agreement", "New Lead", 210000, str(today + timedelta(days=70)), "Priya Shah", "Identify decision makers", str(today - timedelta(days=12))),
            (6, "Generic Injectables Contract", "Qualified", 55000, str(today + timedelta(days=28)), "Jordan Lee", "Validate annual volume", str(today - timedelta(days=5))),
            (1, "Emergency Reorder Program", "Won", 65000, str(today - timedelta(days=12)), "Alex Rivera", "Handoff to operations", str(today - timedelta(days=10))),
            (3, "Legacy Product Replacement", "Lost", 43000, str(today - timedelta(days=30)), "Priya Shah", "Record loss reason", str(today - timedelta(days=29))),
        ]
        cur.executemany(
            """INSERT INTO opportunities
            (account_id, title, stage, value, expected_close, owner, next_action, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            opportunities,
        )

        products = [
            ("INJ-001", "Sterile Sodium Chloride Injection", "Injectables", 14.50, 420, 120, "MedCore Labs"),
            ("INJ-002", "Avastine Syringes", "Injectables", 18.75, 85, 100, "MedCore Labs"),
            ("ANES-010", "Lidocaine Injection", "Anesthesia", 26.00, 240, 80, "SterileRx"),
            ("ANES-011", "Bupivacaine Injection", "Anesthesia", 39.50, 62, 75, "SterileRx"),
            ("IV-100", "IV Administration Set", "Supplies", 4.75, 1250, 300, "CareSupply"),
            ("IV-101", "Safety Syringe Pack", "Supplies", 12.00, 190, 250, "CareSupply"),
        ]
        cur.executemany(
            """INSERT INTO products
            (sku, name, category, unit_price, stock_qty, reorder_level, supplier)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            products,
        )

        orders = [
            (1, str(today - timedelta(days=4)), "Confirmed", 18450, "Paid", "In Transit"),
            (2, str(today - timedelta(days=7)), "Processing", 26750, "Pending", "Preparing"),
            (3, str(today - timedelta(days=12)), "Delivered", 39200, "Paid", "Delivered"),
            (5, str(today - timedelta(days=15)), "Delivered", 14800, "Paid", "Delivered"),
            (1, str(today - timedelta(days=22)), "Delivered", 22100, "Paid", "Delivered"),
        ]
        cur.executemany(
            """INSERT INTO orders
            (account_id, order_date, status, total, payment_status, shipping_status)
            VALUES (?, ?, ?, ?, ?, ?)""",
            orders,
        )

        activities = [
            (1, str(today - timedelta(days=2)), "Email", "Sent product comparison and implementation timeline."),
            (2, str(today - timedelta(days=1)), "Call", "Customer requested revised volume pricing."),
            (3, str(today - timedelta(days=4)), "Meeting", "Demo scheduled with pharmacy and procurement teams."),
            (4, str(today - timedelta(days=8)), "Call", "Confirmed interest and basic qualification."),
        ]
        cur.executemany(
            """INSERT INTO activities
            (opportunity_id, activity_date, activity_type, notes)
            VALUES (?, ?, ?, ?)""",
            activities,
        )

    conn.commit()
    conn.close()


def query_df(sql, params=()):
    conn = get_connection()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def execute(sql, params=()):
    conn = get_connection()
    conn.execute(sql, params)
    conn.commit()
    conn.close()


def money(value):
    return f"${value:,.0f}"


def dashboard():
    st.title("Executive Dashboard")
    st.caption("Primary User: Sales Manager / Operations Manager / Executives")
    st.caption("Goal: Monitor business health, revenue forecast, and operational risks.")
    st.caption("A unified view, bird's eye view on the business status.")

    opportunities = query_df(
        """
        SELECT o.*, a.name AS account_name
        FROM opportunities o
        JOIN accounts a ON a.id = o.account_id
        """
    )
    orders = query_df("SELECT * FROM orders")
    products = query_df("SELECT * FROM products")

    open_opps = opportunities[~opportunities["stage"].isin(["Won", "Lost"])].copy()
    open_opps["weighted_value"] = open_opps.apply(
        lambda row: row["value"] * STAGE_PROBABILITY[row["stage"]], axis=1
    )

    total_pipeline = open_opps["value"].sum()
    weighted_pipeline = open_opps["weighted_value"].sum()
    monthly_sales = orders["total"].sum()
    low_stock_count = int((products["stock_qty"] <= products["reorder_level"]).sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Pipeline", money(total_pipeline), f"{len(open_opps)} opportunities")
    c2.metric("Weighted Forecast", money(weighted_pipeline), "Probability-adjusted")
    c3.metric("Total Order Revenue", money(monthly_sales), f"{len(orders)} orders")
    c4.metric("Inventory Alerts", low_stock_count, "At or below reorder level")

    left, right = st.columns([1.3, 1])

    with left:
        st.subheader("Sales Pipeline")
        stage_summary = (
            open_opps.groupby("stage", as_index=False)
            .agg(Opportunities=("id", "count"), Value=("value", "sum"))
        )
        stage_summary["stage_order"] = stage_summary["stage"].apply(PIPELINE_STAGES.index)
        stage_summary = stage_summary.sort_values("stage_order")
        st.bar_chart(stage_summary.set_index("stage")["Value"])

        st.dataframe(
            open_opps[
                ["account_name", "title", "stage", "value", "owner", "expected_close"]
            ].rename(
                columns={
                    "account_name": "Account",
                    "title": "Opportunity",
                    "stage": "Stage",
                    "value": "Value",
                    "owner": "Owner",
                    "expected_close": "Expected Close",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

    with right:
        st.subheader("Smart Action Center")
        stale = open_opps[
            pd.to_datetime(open_opps["last_activity"]) < pd.Timestamp(date.today() - timedelta(days=7))
        ]
        low_stock = products[products["stock_qty"] <= products["reorder_level"]]

        if not stale.empty:
            for _, row in stale.iterrows():
                st.warning(
                    f"Follow up with **{row['account_name']}**. "
                    f"The opportunity has had no activity since {row['last_activity']}."
                )
        if not low_stock.empty:
            for _, row in low_stock.iterrows():
                shortage = int(row["reorder_level"] - row["stock_qty"])
                st.error(
                    f"Reorder **{row['name']}**. Current stock is {row['stock_qty']}; "
                    f"reorder level is {row['reorder_level']}."
                )
        st.info(
            "Forecast insight: prioritize Negotiation and Proposal opportunities because "
            "they combine high close probability with near-term expected close dates."
        )

        st.subheader("Order Status")
        status_counts = orders["shipping_status"].value_counts()
        st.bar_chart(status_counts)


def crm_pipeline():
    st.title("CRM: Accounts & Opportunities")
    st.caption("Primary User: Sales Representatives")
    st.caption("Goals: 1. 'Pipeline' Tab: Track opportunities, manage pipeline, and plan follow-up actions.")
    st.caption("Goals: 2. 'Add Opportunity' Tab: Create a new potential sale and assign ownership.")
    st.caption("Goals: 3. 'Accounts' Tab: Manage customer organizations, contacts, and sales relationships. Can be done by customer success teams too.")
    tab1, tab2, tab3 = st.tabs(["Pipeline", "Add Opportunity", "Accounts"])

    with tab1:
        opps = query_df(
            """
            SELECT o.id, a.name AS account, o.title, o.stage, o.value,
                   o.expected_close, o.owner, o.next_action, o.last_activity
            FROM opportunities o
            JOIN accounts a ON a.id = o.account_id
            ORDER BY o.id DESC
            """
        )

        owner_filter = st.multiselect(
            "Filter by owner",
            sorted(opps["owner"].dropna().unique()),
        )
        stage_filter = st.multiselect("Filter by stage", PIPELINE_STAGES)

        filtered = opps.copy()
        if owner_filter:
            filtered = filtered[filtered["owner"].isin(owner_filter)]
        if stage_filter:
            filtered = filtered[filtered["stage"].isin(stage_filter)]

        st.dataframe(filtered, use_container_width=True, hide_index=True)

        st.subheader("Update Opportunity")
        if not opps.empty:
            labels = {
                int(row["id"]): f"#{row['id']} · {row['account']} · {row['title']}"
                for _, row in opps.iterrows()
            }
            selected_id = st.selectbox(
                "Opportunity",
                options=list(labels),
                format_func=lambda x: labels[x],
            )
            current = opps[opps["id"] == selected_id].iloc[0]
            c1, c2 = st.columns(2)
            new_stage = c1.selectbox(
                "Stage",
                PIPELINE_STAGES,
                index=PIPELINE_STAGES.index(current["stage"]),
            )
            next_action = c2.text_input("Next action", current["next_action"] or "")
            if st.button("Save opportunity changes", type="primary"):
                execute(
                    """
                    UPDATE opportunities
                    SET stage = ?, next_action = ?, last_activity = ?
                    WHERE id = ?
                    """,
                    (new_stage, next_action, str(date.today()), int(selected_id)),
                )
                st.success("Opportunity updated.")
                st.rerun()

    with tab2:
        accounts = query_df("SELECT id, name FROM accounts ORDER BY name")
        with st.form("new_opportunity"):
            account_name = st.selectbox("Account", accounts["name"].tolist())
            title = st.text_input("Opportunity name")
            stage = st.selectbox("Stage", PIPELINE_STAGES)
            value = st.number_input("Estimated value", min_value=0.0, step=1000.0)
            close_date = st.date_input("Expected close date", date.today() + timedelta(days=30))
            owner = st.selectbox("Owner", ["Alex Rivera", "Priya Shah", "Jordan Lee"])
            next_action = st.text_input("Next action")
            submitted = st.form_submit_button("Create opportunity", type="primary")

        if submitted:
            account_id = int(accounts.loc[accounts["name"] == account_name, "id"].iloc[0])
            execute(
                """
                INSERT INTO opportunities
                (account_id, title, stage, value, expected_close, owner, next_action, last_activity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    title,
                    stage,
                    value,
                    str(close_date),
                    owner,
                    next_action,
                    str(date.today()),
                ),
            )
            st.success("Opportunity created.")

    with tab3:
        accounts = query_df("SELECT * FROM accounts ORDER BY name")
        st.dataframe(accounts, use_container_width=True, hide_index=True)

        with st.expander("Add account"):
            with st.form("new_account"):
                name = st.text_input("Organization name")
                account_type = st.selectbox(
                    "Type", ["Hospital", "Pharmacy", "Clinic", "Surgical Center", "Health Network"]
                )
                city = st.text_input("City")
                state = st.text_input("State", "AZ")
                contact_name = st.text_input("Primary contact")
                contact_email = st.text_input("Contact email")
                submitted_account = st.form_submit_button("Create account")
            if submitted_account:
                execute(
                    """
                    INSERT INTO accounts
                    (name, account_type, city, state, contact_name, contact_email, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Prospect')
                    """,
                    (name, account_type, city, state, contact_name, contact_email),
                )
                st.success("Account created.")


def order_management():
    st.title("ERP: Order Management")
    st.caption("Primary User: Operations & Customer Service")
    st.caption("Goal: Manage customer orders after a deal is won.")
    orders = query_df(
        """
        SELECT o.id, a.name AS account, o.order_date, o.status,
               o.total, o.payment_status, o.shipping_status
        FROM orders o
        JOIN accounts a ON a.id = o.account_id
        ORDER BY o.order_date DESC
        """
    )
    st.dataframe(orders, use_container_width=True, hide_index=True)

    st.subheader("Create Sales Order")
    accounts = query_df("SELECT id, name FROM accounts ORDER BY name")
    with st.form("new_order"):
        account_name = st.selectbox("Customer", accounts["name"].tolist())
        order_total = st.number_input("Order total", min_value=0.0, step=500.0)
        payment_status = st.selectbox("Payment status", ["Pending", "Paid", "Overdue"])
        shipping_status = st.selectbox("Shipping status", ["Preparing", "In Transit", "Delivered"])
        submit_order = st.form_submit_button("Create order", type="primary")

    if submit_order:
        account_id = int(accounts.loc[accounts["name"] == account_name, "id"].iloc[0])
        execute(
            """
            INSERT INTO orders
            (account_id, order_date, status, total, payment_status, shipping_status)
            VALUES (?, ?, 'Confirmed', ?, ?, ?)
            """,
            (
                account_id,
                str(date.today()),
                order_total,
                payment_status,
                shipping_status,
            ),
        )
        st.success("Order created.")
        st.rerun()


def inventory():
    st.title("ERP: Inventory")
    st.caption("Primary User: Warehouse & Procurement")
    st.caption("Goal: Track stock levels and prevent inventory shortages.")
    products = query_df("SELECT * FROM products ORDER BY category, name")
    products["inventory_status"] = products.apply(
        lambda row: "Reorder" if row["stock_qty"] <= row["reorder_level"] else "Healthy",
        axis=1,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Products", len(products))
    c2.metric("Units in Stock", int(products["stock_qty"].sum()))
    c3.metric("Items to Reorder", int((products["inventory_status"] == "Reorder").sum()))

    st.dataframe(products, use_container_width=True, hide_index=True)

    st.subheader("Adjust Stock")
    product_map = {
        int(row["id"]): f"{row['sku']} · {row['name']}"
        for _, row in products.iterrows()
    }
    selected_product = st.selectbox(
        "Product",
        options=list(product_map),
        format_func=lambda x: product_map[x],
    )
    adjustment = st.number_input(
        "Quantity adjustment",
        step=1,
        help="Use a positive number for received stock and a negative number for consumed stock.",
    )
    if st.button("Apply stock adjustment", type="primary"):
        execute(
            "UPDATE products SET stock_qty = MAX(0, stock_qty + ?) WHERE id = ?",
            (int(adjustment), int(selected_product)),
        )
        st.success("Inventory updated.")
        st.rerun()


def process_automation():
    st.title("Workflow Automation")
    st.caption("Examples of rule-based automations an enterprise platform analyst might configure.")
    st.caption("Primary User: CRM / ERP Platform Analyst")
    st.caption("Goal: Configure business rules, notifications, and process automation.")
    

    rules = [
        {
            "Rule": "Stale Opportunity Alert",
            "Trigger": "No activity for 7 days",
            "Action": "Create follow-up task and notify opportunity owner",
            "Status": "Active",
        },
        {
            "Rule": "Inventory Reorder Alert",
            "Trigger": "Stock <= reorder level",
            "Action": "Create purchasing request",
            "Status": "Active",
        },
        {
            "Rule": "Won Deal Handoff",
            "Trigger": "Opportunity stage changes to Won",
            "Action": "Create customer onboarding checklist",
            "Status": "Active",
        },
        {
            "Rule": "Overdue Payment Escalation",
            "Trigger": "Payment remains overdue for 5 days",
            "Action": "Notify finance and account owner",
            "Status": "Draft",
        },
    ]
    st.dataframe(pd.DataFrame(rules), use_container_width=True, hide_index=True)

    st.subheader("Automation Run Preview")
    stale_count = query_df(
        """
        SELECT COUNT(*) AS count
        FROM opportunities
        WHERE stage NOT IN ('Won', 'Lost')
          AND date(last_activity) < date('now', '-7 day')
        """
    ).iloc[0]["count"]
    reorder_count = query_df(
        "SELECT COUNT(*) AS count FROM products WHERE stock_qty <= reorder_level"
    ).iloc[0]["count"]

    st.write(f"**{stale_count}** stale opportunity alert(s) would be generated.")
    st.write(f"**{reorder_count}** inventory reorder request(s) would be generated.")

    if st.button("Simulate automation run", type="primary"):
        st.success(
            f"Simulation completed: {stale_count + reorder_count} workflow action(s) generated."
        )


def architecture():
    st.title("System Design")
    st.caption("Primary User: Developers & Solution Architects")
    st.caption("Goal: Explain how the production system would be designed and integrated.")
    st.markdown(
        """
### Project overview
This application brings the main parts of a healthcare sales operation into one place:
accounts, opportunities, orders, inventory, and workflow alerts. The goal is to show how a
CRM and ERP can share context so sales, finance, operations, and procurement are working from
the same operational picture.

### Application flow
The Dashboard is the starting point. It summarizes open pipeline, weighted forecast, recent
order revenue, and inventory alerts, then highlights follow-up and reorder items that need
attention.

The CRM Pipeline screen manages the customer-facing side of the process. Teams can review
accounts, create opportunities, update deal stages, assign owners, and keep the next action
visible. Those fields become the source for forecasting and stale-opportunity alerts.

Order Management begins once customer demand becomes operational work. Orders connect back
to accounts and track payment and shipping status, which gives the business a bridge between
the sales pipeline and fulfillment activity.

Inventory tracks products, stock levels, reorder thresholds, suppliers, and stock adjustments.
Low-stock products feed the dashboard and automation preview so procurement issues are visible
before they interrupt order fulfillment.

Workflow Automation shows how repeatable business rules can monitor the data. Stale
opportunities can create follow-up tasks, low inventory can create purchasing requests, and
won deals can trigger an onboarding handoff.

### Data model
- Accounts represent healthcare organizations and primary contacts.
- Opportunities represent potential revenue tied to an account.
- Orders represent confirmed customer purchases.
- Products represent sellable inventory and replenishment thresholds.
- Activities represent sales touchpoints that keep opportunities current.

### Architecture path
This version uses Streamlit for the interface and SQLite for local transactional data, which
keeps the prototype simple to run and easy to inspect. In a production environment, the same
flow would typically move to a separate frontend, API layer, PostgreSQL database, background
workers for scheduled automation, role-based permissions, integrations with email and ERP
systems, audit logs, monitoring, backups, validation, and encryption.

### AI and automation approach
Automation should handle deterministic events such as stale opportunities, reorder thresholds,
handoffs, and payment escalations. AI can assist with summaries, prioritization, anomaly
detection, and next-action recommendations. Any high-impact action should stay reviewable,
traceable, and permission-aware.
        """
    )


def main():
    initialize_database()

    st.sidebar.title("MediOps Demo")
    st.sidebar.caption("Healthcare CRM + ERP Prototype")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "CRM Pipeline",
            "Order Management",
            "Inventory",
            "Workflow Automation",
            "Architecture",
        ],
    )

    st.sidebar.divider()
    st.sidebar.markdown(
        "**Operational focus:** CRM, ERP, automation, reporting, and data quality."
    )

    if page == "Dashboard":
        dashboard()
    elif page == "CRM Pipeline":
        crm_pipeline()
    elif page == "Order Management":
        order_management()
    elif page == "Inventory":
        inventory()
    elif page == "Workflow Automation":
        process_automation()
    else:
        architecture()


if __name__ == "__main__":
    main()
