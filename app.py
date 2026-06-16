"""
SmartLink CRM v1.00 — Streamlit Web Demo
Run with: streamlit run app.py
"""

import streamlit as st
import sqlite3
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SmartLink CRM v1.00",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme colours ─────────────────────────────────────────────────────────────
CYAN    = "#00E5FF"
NAVY    = "#0D1F2D"
GREEN   = "#7DC142"
AMB     = "#FF8C42"
PURP    = "#A78BFA"
RED     = "#DC2626"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0A1929 !important;
}
[data-testid="stSidebar"] * { color: #99AABB !important; }
[data-testid="stSidebar"] .stRadio label { color: #99AABB !important; font-size: 14px; }

/* Metric cards */
div[data-testid="metric-container"] {
    background: #fff;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 14px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
div[data-testid="metric-container"] label { color: #64748B !important; font-size: 11px !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: .5px; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 700 !important; color: #0D1F2D !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* Buttons */
.stButton button {
    background: #00E5FF !important;
    color: #0D1F2D !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    padding: 6px 18px !important;
}
.stButton button:hover { background: #00C8E0 !important; }

/* Input fields */
.stTextInput input, .stSelectbox select, .stTextArea textarea {
    border-radius: 7px !important;
    border: 1px solid #E2E8F0 !important;
    font-size: 13px !important;
}

/* Status pills */
.pill-open     { background:#EFF6FF; color:#1D4ED8; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; }
.pill-progress { background:#FFFBEB; color:#92400E; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; }
.pill-done     { background:#F0FDF4; color:#166534; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; }
.pill-overdue  { background:#FEE2E2; color:#991B1B; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; }
.pill-paid     { background:#F0FDF4; color:#166534; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; }
.pill-sent     { background:#EFF6FF; color:#1D4ED8; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; }
.pill-due      { background:#FFFBEB; color:#92400E; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; }
.pill-ok       { background:#F0FDF4; color:#166534; padding:3px 10px; border-radius:4px; font-size:11px; font-weight:600; }

/* Section header */
.sec-header {
    background: #0D1F2D;
    color: #fff;
    font-weight: 600;
    font-size: 13px;
    padding: 9px 16px;
    border-radius: 8px 8px 0 0;
    margin-bottom: 0;
}

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Database ───────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def seed_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS tbl_customers (
        Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        "Company Name" TEXT, "Customer Name" TEXT,
        Address TEXT, Address1 TEXT,
        "Contact Number" TEXT, Phone TEXT, Email TEXT)""")
    if c.execute("SELECT COUNT(*) FROM tbl_customers").fetchone()[0] == 0:
        c.executemany("""INSERT INTO tbl_customers
            ("Company Name","Customer Name",Address,Address1,"Contact Number",Phone,Email)
            VALUES (?,?,?,?,?,?,?)""", [
            ("Riverside Events","Riverside Events Pty Ltd","12 River Rd, Brisbane","12 River Rd","07 3100 1111","07 3100 1111","info@riverside.com.au"),
            ("Clarke Industries","Clarke Industries Ltd","88 Clarke St, Sydney","88 Clarke St","02 9200 2222","02 9200 2222","contact@clarke.com.au"),
            ("Northgate Shopping","Northgate Shopping Centre","5 Mall Dr, Northgate","5 Mall Dr","07 3200 3333","07 3200 3333","ops@northgate.com.au"),
            ("Eastgate Mall","Eastgate Mall Management","99 East Ave, Eastgate","99 East Ave","07 3300 4444","07 3300 4444","admin@eastgate.com.au"),
            ("Summit Audio","Summit Audio Solutions","22 Tech Park, Milton","22 Tech Park","07 3400 5555","07 3400 5555","hello@summitaudio.com.au"),
            ("Greenfield Hotels","Greenfield Hotels Group","1 Hotel Blvd, Gold Coast","1 Hotel Blvd","07 5500 6666","07 5500 6666","bookings@greenfield.com.au"),
            ("Metro Conference","Metro Conference Centre","300 George St, Brisbane","300 George St","07 3600 7777","07 3600 7777","events@metroconf.com.au"),
        ])

    c.execute("""CREATE TABLE IF NOT EXISTS tbl_machine (
        "Machine ID" INTEGER PRIMARY KEY AUTOINCREMENT,
        "Model Number" TEXT, Type TEXT, Manufacturer TEXT, Supplier TEXT,
        "Expiry of Warranty" TEXT, "Customer ID" INTEGER,
        "Last Service" TEXT, "Not In Service" INTEGER DEFAULT 0, Firmware_Ver TEXT)""")
    if c.execute("SELECT COUNT(*) FROM tbl_machine").fetchone()[0] == 0:
        c.executemany("""INSERT INTO tbl_machine
            ("Model Number",Type,Manufacturer,Supplier,"Expiry of Warranty","Customer ID","Last Service","Not In Service",Firmware_Ver)
            VALUES (?,?,?,?,?,?,?,?,?)""", [
            ("RCF HDL 6-A","Line Array","RCF","Jands","2026-06-01",1,"2024-10-15",0,"v2.1.4"),
            ("QSC K12.2","Powered Speaker","QSC","NAS","2025-12-01",1,"2024-09-01",0,"v1.9.0"),
            ("Yamaha QL5","Digital Mixer","Yamaha","Yamaha","2027-01-01",2,"2024-11-01",0,"v4.5.1"),
            ("Crown XTi 4002","Amplifier","Crown","Jands","2025-08-01",3,"2024-08-20",0,"v3.0.0"),
            ("Shure QLXD4","Wireless Rcvr","Shure","Shure","2026-03-01",3,"2024-07-10",0,"v2.0.0"),
            ("Allen Heath SQ5","Digital Mixer","A&H","NAS","2027-06-01",4,"2024-12-01",0,"v1.5.2"),
            ("Lab Gruppen C88","Amplifier","Lab Gru","Jands","2026-09-01",5,"2024-10-05",0,"v4.1.0"),
            ("d&b Y8","Line Array","d&b","d&b","2028-01-01",6,"2025-01-10",0,"v5.0.1"),
        ])

    c.execute("""CREATE TABLE IF NOT EXISTS tbl_product_list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Product_code TEXT, product_number TEXT, product_name TEXT,
        Product_Description TEXT, description TEXT, quantity INTEGER DEFAULT 0)""")
    if c.execute("SELECT COUNT(*) FROM tbl_product_list").fetchone()[0] == 0:
        c.executemany("""INSERT INTO tbl_product_list
            (Product_code,product_number,product_name,Product_Description,description,quantity)
            VALUES (?,?,?,?,?,?)""", [
            ("XLR-3M-5","XLR-3M-5","XLR Cable 5m","XLR 3-pin Cable 5m","XLR 5m",42),
            ("XLR-3M-10","XLR-3M-10","XLR Cable 10m","XLR 3-pin Cable 10m","XLR 10m",28),
            ("SPEAKON-4","SPEAKON-4","Speakon Cable 4m","4-pole Speakon Cable 4m","Speakon 4m",35),
            ("IEC-C13","IEC-C13","IEC Power Cable","IEC C13 Mains Cable 2m","IEC 2m",60),
            ("RJ45-CAT6","RJ45-CAT6","CAT6 Cable 10m","CAT6 Patch Cable 10m","CAT6 10m",55),
            ("FUZE-20A","FUZE-20A","Fuse 20A","20A Glass Fuse 5x20mm","Fuse 20A",200),
            ("FUZE-10A","FUZE-10A","Fuse 10A","10A Glass Fuse 5x20mm","Fuse 10A",180),
            ("RACK-NUT-M6","RACK-NUT-M6","Rack Nut M6","M6 Rack Cage Nuts x50","Rack Nuts",12),
            ("VELCRO-5M","VELCRO-5M","Velcro Roll 5m","Velcro Cable Tie Roll 5m","Velcro",20),
            ("PANEL-BLANK","PANEL-BLANK","Blank Panel 1U","1U Vented Blank Panel","Blank Panel",8),
            ("SD-CARD-32","SD-CARD-32","SD Card 32GB","32GB Class 10 SD Card","SD Card",18),
            ("USB-A-B-3M","USB-A-B-3M","USB A-B Cable 3m","USB Type-A to B Cable 3m","USB Cable",22),
        ])

    c.execute("""CREATE TABLE IF NOT EXISTS tbl_work_orders (
        Work_Order_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        work_order TEXT, customer_name TEXT, contact_name TEXT,
        address TEXT, status TEXT DEFAULT 'Open', tech_name TEXT,
        travel_time REAL DEFAULT 0, labour_time REAL DEFAULT 0,
        completion_date TEXT, notes TEXT,
        created_at TEXT DEFAULT (date('now')))""")
    if c.execute("SELECT COUNT(*) FROM tbl_work_orders").fetchone()[0] == 0:
        data = []
        custs = ["Riverside Events","Clarke Industries","Northgate Shopping","Eastgate Mall","Summit Audio","Greenfield Hotels","Metro Conference"]
        contacts = ["John Smith","Mary Clarke","Pete North","Sue East","Al Summit","Greta Green","Matt Metro"]
        addrs = ["12 River Rd","88 Clarke St","5 Mall Dr","99 East Ave","22 Tech Park","1 Hotel Blvd","300 George St"]
        techs = ["Jeffrey Lo","Mike Chen","Sarah Johnson","Tom Williams"]
        job_types = ["PA check","Mixer service","Speaker swap","Amp install","DSP update","Room service","Network fault"]
        months = [(1,28),(2,34),(3,41),(4,38)]
        idx = 1
        for (month, count) in months:
            for i in range(count):
                if month < 4:
                    status = "Completed"
                elif i < 28:
                    status = "Completed"
                elif i < 32:
                    status = "In Progress"
                else:
                    status = "Open"
                data.append((
                    f"WO-2025-{idx:03d}",
                    custs[i%7], contacts[i%7], addrs[i%7],
                    status, techs[i%4],
                    round(0.5+0.5*(i%3),1), round(1.5+0.5*(i%5),1),
                    f"2025-{month:02d}-{10+i%20:02d}",
                    job_types[i%7],
                    f"2025-{month:02d}-{3+i%25:02d}",
                ))
                idx += 1
        c.executemany("""INSERT INTO tbl_work_orders
            (work_order,customer_name,contact_name,address,status,tech_name,
             travel_time,labour_time,completion_date,notes,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""", data)

    c.execute("""CREATE TABLE IF NOT EXISTS tbl_regular_service_months (
        id INTEGER PRIMARY KEY AUTOINCREMENT, "Machine ID" INTEGER,
        January TEXT DEFAULT 'No', February TEXT DEFAULT 'No',
        March TEXT DEFAULT 'No', April TEXT DEFAULT 'Yes',
        May TEXT DEFAULT 'No', June TEXT DEFAULT 'No',
        July TEXT DEFAULT 'No', August TEXT DEFAULT 'Yes',
        September TEXT DEFAULT 'No', October TEXT DEFAULT 'Yes',
        November TEXT DEFAULT 'No', December TEXT DEFAULT 'No')""")
    if c.execute("SELECT COUNT(*) FROM tbl_regular_service_months").fetchone()[0] == 0:
        for mid in range(1, 9):
            c.execute('INSERT INTO tbl_regular_service_months ("Machine ID") VALUES (?)', (mid,))

    conn.commit()
    conn.close()

seed_db()

# ── Session state for invoices & todos ────────────────────────────────────────
if "invoices" not in st.session_state:
    st.session_state.invoices = [
        {"id":1047,"customer":"Clarke Industries","date":"2026-04-10","due":"2026-04-24","amount":1280.0,"status":"Overdue","lines":[{"desc":"PA system service call","qty":1,"price":800},{"desc":"Cable replacement kit","qty":2,"price":240}],"notes":"Payment by EFT."},
        {"id":1046,"customer":"Northgate Shopping","date":"2026-04-05","due":"2026-04-19","amount":2400.0,"status":"Paid","lines":[{"desc":"Full PA system hire 2 days","qty":2,"price":900},{"desc":"Crew 8hr","qty":8,"price":75}],"notes":""},
        {"id":1045,"customer":"Riverside Events","date":"2026-04-01","due":"2026-04-15","amount":1045.0,"status":"Sent","lines":[{"desc":"Sound system consultation","qty":1,"price":950}],"notes":""},
        {"id":1044,"customer":"Eastgate Mall","date":"2026-03-28","due":"2026-04-11","amount":4180.0,"status":"Paid","lines":[{"desc":"Line array install 8x speakers","qty":8,"price":320},{"desc":"Cabling & rack build","qty":1,"price":1240}],"notes":""},
        {"id":1043,"customer":"Summit Audio","date":"2026-03-20","due":"2026-04-03","amount":682.0,"status":"Paid","lines":[{"desc":"PA system hire Sunday service","qty":1,"price":620}],"notes":""},
    ]
    st.session_state.next_inv_id = 1048

if "todos" not in st.session_state:
    st.session_state.todos = [
        {"text":"Follow up Clarke — invoice #1047","done":False,"pri":"High"},
        {"text":"Northgate quarterly PA service","done":False,"pri":"High"},
        {"text":"Reorder XLR connectors (low stock)","done":False,"pri":"Med"},
        {"text":"Send quote to Riverside Events","done":True,"pri":"Done"},
        {"text":"Update firmware — 3x amp units","done":False,"pri":"Med"},
    ]

# ── Sidebar navigation ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:14px 0 10px 0;border-bottom:1px solid #1E3A50;margin-bottom:10px'>
        <span style='color:#00E5FF;font-size:20px'>⬤</span>
        <span style='color:#fff;font-size:15px;font-weight:700;margin-left:6px'>SmartLink</span>
        <div style='color:#667799;font-size:11px;margin-left:26px;margin-top:2px'>CRM  v1.00  —  Demo Mode</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("", [
        "📊  Dashboard",
        "📋  PA Work Orders",
        "👥  Customers",
        "📦  Inventory",
        "🧾  Invoices",
        "🔧  Regular Service",
    ], label_visibility="collapsed")

    st.markdown("""
    <div style='position:fixed;bottom:20px;left:0;width:210px;padding:12px 16px;border-top:1px solid #1E3A50'>
        <div style='color:#99AABB;font-size:11px'>👤 Admin User</div>
        <div style='color:#556677;font-size:10px;margin-top:3px'>📅 14 Jun 2026</div>
        <div style='color:#7DC142;font-size:10px;margin-top:3px'>● Online</div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════════════════════════
if "Dashboard" in page:
    st.markdown("## 📊 Dashboard Overview")

    conn = get_conn()
    c = conn.cursor()
    open_wo = c.execute("SELECT COUNT(*) FROM tbl_work_orders WHERE status IN ('Open','In Progress')").fetchone()[0]
    active_cust = c.execute("SELECT COUNT(*) FROM tbl_customers").fetchone()[0]
    inv_pending = c.execute("SELECT COUNT(*) FROM tbl_work_orders WHERE status='Open'").fetchone()[0]
    svc_due = c.execute("SELECT COUNT(*) FROM tbl_work_orders WHERE status='In Progress'").fetchone()[0]

    wo_by_month = []
    rev_by_month = []
    for m in range(1, 9):
        n = c.execute("SELECT COUNT(*) FROM tbl_work_orders WHERE strftime('%m',created_at)=?", (f"{m:02d}",)).fetchone()[0]
        wo_by_month.append(n)
        r = c.execute("SELECT COALESCE(SUM(labour_time*120+travel_time*60),0) FROM tbl_work_orders WHERE strftime('%m',created_at)=?", (f"{m:02d}",)).fetchone()[0]
        rev_by_month.append(round(r/1000, 1))

    statuses_raw = c.execute("SELECT status, COUNT(*) as n FROM tbl_work_orders GROUP BY status").fetchall()
    conn.close()

    # Stat cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Open Work Orders", open_wo, "Active jobs")
    col2.metric("Active Customers", active_cust, "In system")
    col3.metric("Invoices Pending", inv_pending, "Awaiting close")
    col4.metric("Services Due", svc_due, "In progress")

    st.markdown("---")

    # Charts row
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug"]
    col_chart, col_todo = st.columns([2, 1])

    with col_chart:
        st.markdown('<div class="sec-header">Monthly Work Orders — Jan–Aug 2025</div>', unsafe_allow_html=True)
        colors = [GREEN if v == max(wo_by_month) else CYAN for v in wo_by_month]
        fig = go.Figure(go.Bar(
            x=months, y=wo_by_month,
            marker_color=colors,
            text=wo_by_month, textposition="outside",
        ))
        fig.update_layout(
            height=260, margin=dict(l=10,r=10,t=10,b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#F1F5F9", showgrid=True),
            xaxis=dict(showgrid=False),
            font=dict(family="Inter", size=11, color="#0D1F2D"),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_todo:
        st.markdown('<div class="sec-header">Things To Do</div>', unsafe_allow_html=True)
        with st.container():
            new_task = st.text_input("", placeholder="Add a task…", key="new_todo", label_visibility="collapsed")
            if st.button("+ Add Task") and new_task.strip():
                st.session_state.todos.insert(0, {"text": new_task.strip(), "done": False, "pri": "Med"})
                st.rerun()

            pri_colors = {"High":"🔴","Med":"🟡","Done":"🟢","Low":"🔵"}
            for i, todo in enumerate(st.session_state.todos):
                cols = st.columns([0.08, 0.72, 0.12, 0.08])
                chk = cols[0].checkbox("", value=todo["done"], key=f"todo_{i}", label_visibility="collapsed")
                if chk != todo["done"]:
                    st.session_state.todos[i]["done"] = chk
                    st.session_state.todos[i]["pri"] = "Done" if chk else "Med"
                    st.rerun()
                text_style = "text-decoration:line-through;color:#94A3B8;" if todo["done"] else "color:#0D1F2D;"
                cols[1].markdown(f"<span style='{text_style}font-size:12px'>{todo['text']}</span>", unsafe_allow_html=True)
                cols[2].markdown(f"<span style='font-size:11px'>{pri_colors.get(todo['pri'],'🟡')} {todo['pri']}</span>", unsafe_allow_html=True)
                if cols[3].button("✕", key=f"del_todo_{i}"):
                    st.session_state.todos.pop(i)
                    st.rerun()

    st.markdown("---")

    col_line, col_donut = st.columns(2)

    with col_line:
        st.markdown('<div class="sec-header">Revenue Trend — Monthly ($000s)</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Scatter(
            x=months, y=rev_by_month,
            mode="lines+markers+text",
            line=dict(color=CYAN, width=2.5),
            marker=dict(size=7, color="white", line=dict(color=CYAN, width=2)),
            text=[f"${v}k" for v in rev_by_month],
            textposition="top center",
            fill="tozeroy", fillcolor=f"rgba(0,229,255,0.08)",
        ))
        fig2.update_layout(
            height=240, margin=dict(l=10,r=10,t=10,b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(gridcolor="#F1F5F9"), xaxis=dict(showgrid=False),
            font=dict(family="Inter", size=11, color="#0D1F2D"),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_donut:
        st.markdown('<div class="sec-header">Service Breakdown — Work Order Status</div>', unsafe_allow_html=True)
        d_labels = [r[0] for r in statuses_raw]
        d_vals   = [r[1] for r in statuses_raw]
        fig3 = go.Figure(go.Pie(
            labels=d_labels, values=d_vals,
            hole=0.55,
            marker=dict(colors=[CYAN, GREEN, PURP, AMB][:len(d_vals)],
                        line=dict(color="white", width=2)),
        ))
        fig3.update_layout(
            height=240, margin=dict(l=10,r=10,t=10,b=10),
            paper_bgcolor="white",
            font=dict(family="Inter", size=11),
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, x=0.1),
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ── Bottom row: Overdue Work Orders + Job Service History ─────────────────
    st.markdown("---")
    bot_col1, bot_col2 = st.columns(2)

    with bot_col1:
        st.markdown('<div class="sec-header">🔴 Overdue / Open Work Orders</div>', unsafe_allow_html=True)
        conn2 = get_conn()
        overdue_rows = [dict(r) for r in conn2.execute("""
            SELECT work_order, customer_name, tech_name, labour_time, created_at, status
            FROM tbl_work_orders
            WHERE status IN ('Open', 'In Progress')
            ORDER BY created_at ASC
            LIMIT 10
        """).fetchall()]
        conn2.close()

        if overdue_rows:
            from datetime import datetime as _dt2
            ov_table = []
            for r in overdue_rows:
                try:
                    days_open = (_dt2.today() - _dt2.strptime(r["created_at"], "%Y-%m-%d")).days
                except Exception:
                    days_open = 0
                ov_table.append({
                    "Job #":      r["work_order"],
                    "Customer":   r["customer_name"],
                    "Tech":       r.get("tech_name") or "Unassigned",
                    "Labour":     f"{r['labour_time']}h",
                    "Days Open":  days_open,
                    "Status":     r["status"],
                })
            st.dataframe(pd.DataFrame(ov_table), use_container_width=True, hide_index=True,
                column_config={"Days Open": st.column_config.NumberColumn("Days Open", format="%d days")})
            critical = sum(1 for r in ov_table if isinstance(r["Days Open"], int) and r["Days Open"] > 30)
            st.caption(f"**{len(ov_table)}** open jobs · **{critical}** critical (>30 days)")
        else:
            st.success("✅ No overdue work orders!")

    with bot_col2:
        st.markdown('<div class="sec-header">📅 Recent Job History</div>', unsafe_allow_html=True)
        conn3 = get_conn()
        history_rows = [dict(r) for r in conn3.execute("""
            SELECT work_order, customer_name, tech_name, labour_time,
                   completion_date, notes
            FROM tbl_work_orders
            WHERE status = 'Completed'
            ORDER BY completion_date DESC
            LIMIT 10
        """).fetchall()]
        conn3.close()

        if history_rows:
            hist_table = [{
                "Job #":      r["work_order"],
                "Customer":   r["customer_name"],
                "Tech":       r.get("tech_name") or "—",
                "Labour":     f"{r['labour_time']}h",
                "Completed":  r.get("completion_date") or "—",
                "Notes":      (r.get("notes") or "")[:35],
            } for r in history_rows]
            st.dataframe(pd.DataFrame(hist_table), use_container_width=True, hide_index=True)
            total_hrs = sum(r["labour_time"] for r in history_rows)
            st.caption(f"**{len(hist_table)}** recent jobs shown · **{total_hrs:.1f}h** total labour")
        else:
            st.info("No completed jobs yet.")


# ════════════════════════════════════════════════════════════════════
# WORK ORDERS
# ════════════════════════════════════════════════════════════════════
elif "Work Orders" in page:
    st.markdown("## 📋 PA Work Orders")

    conn = get_conn()
    c = conn.cursor()
    rows = c.execute("SELECT * FROM tbl_work_orders ORDER BY Work_Order_ID DESC").fetchall()
    conn.close()
    all_rows = [dict(r) for r in rows]

    open_c = sum(1 for r in all_rows if r["status"] == "Open")
    prog_c = sum(1 for r in all_rows if r["status"] == "In Progress")
    done_c = sum(1 for r in all_rows if r["status"] == "Completed")

    col1, col2, col3 = st.columns(3)
    col1.metric("Open", open_c)
    col2.metric("In Progress", prog_c)
    col3.metric("Completed", done_c)

    st.markdown("---")

    tcol1, tcol2, tcol3 = st.columns([2, 2, 1])
    search = tcol1.text_input("🔍 Search", placeholder="Customer, job #, type…", label_visibility="collapsed")
    status_filter = tcol2.selectbox("Status", ["All","Open","In Progress","Completed"], label_visibility="collapsed")

    with tcol3:
        new_job = st.button("+ New Job")

    if new_job:
        with st.form("new_job_form"):
            st.markdown("### Create New Job")
            fc1, fc2 = st.columns(2)
            nj_wo   = fc1.text_input("Work Order #")
            nj_cust = fc2.text_input("Customer Name")
            nj_tech = fc1.text_input("Technician")
            nj_stat = fc2.selectbox("Status", ["Open","In Progress","Completed"])
            nj_travel = fc1.number_input("Travel Time (h)", 0.0, step=0.5)
            nj_labour = fc2.number_input("Labour Time (h)", 1.0, step=0.5)
            nj_notes = st.text_area("Notes")
            submitted = st.form_submit_button("✔ Save Job")
            if submitted and nj_wo and nj_cust:
                conn2 = get_conn()
                conn2.execute("""INSERT INTO tbl_work_orders
                    (work_order,customer_name,status,tech_name,travel_time,labour_time,notes,created_at)
                    VALUES (?,?,?,?,?,?,?,?)""",
                    (nj_wo, nj_cust, nj_stat, nj_tech, nj_travel, nj_labour, nj_notes, str(date.today())))
                conn2.commit(); conn2.close()
                st.success(f"Job {nj_wo} created!")
                st.rerun()

    filtered = [r for r in all_rows
                if (status_filter == "All" or r["status"] == status_filter)
                and (not search or search.lower() in r["work_order"].lower() or search.lower() in r["customer_name"].lower())]

    st.markdown('<div class="sec-header">Work Orders</div>', unsafe_allow_html=True)

    status_emoji = {"Open":"🔵","In Progress":"🟡","Completed":"🟢"}
    df = pd.DataFrame([{
        "Job #": r["work_order"],
        "Customer": r["customer_name"],
        "Tech": r["tech_name"] or "—",
        "Labour": f"{r['labour_time']}h",
        "Status": f"{status_emoji.get(r['status'],'⚪')} {r['status']}",
        "Date": r["created_at"] or "—",
    } for r in filtered[:100]])

    if not df.empty:
        selected = st.dataframe(df, use_container_width=True, hide_index=True,
                                on_select="rerun", selection_mode="single-row")
        sel_rows = selected.selection.rows if selected else []
        if sel_rows:
            r = filtered[sel_rows[0]]
            with st.expander(f"📄 Detail — {r['work_order']}", expanded=True):
                dc1, dc2, dc3 = st.columns(3)
                dc1.write(f"**Customer:** {r['customer_name']}")
                dc1.write(f"**Contact:** {r.get('contact_name') or '—'}")
                dc2.write(f"**Technician:** {r.get('tech_name') or '—'}")
                dc2.write(f"**Status:** {r['status']}")
                dc3.write(f"**Labour:** {r['labour_time']}h")
                dc3.write(f"**Travel:** {r['travel_time']}h")
                if r.get("notes"):
                    st.write(f"**Notes:** {r['notes']}")
    else:
        st.info("No work orders match your filter.")

    # ── Bottom tables: Overdue Jobs + Job History ─────────────────────────────
    st.markdown("---")
    bot1, bot2 = st.columns(2)

    with bot1:
        st.markdown('<div class="sec-header">🔴 Overdue / Open Jobs</div>', unsafe_allow_html=True)
        conn_ov = get_conn()
        overdue_data = [dict(r) for r in conn_ov.execute("""
            SELECT work_order, customer_name, tech_name,
                   travel_time, labour_time, created_at, notes
            FROM tbl_work_orders
            WHERE status IN ('Open', 'In Progress')
            ORDER BY created_at ASC
        """).fetchall()]
        conn_ov.close()

        if overdue_data:
            from datetime import datetime as _dt
            ov_rows = []
            for r in overdue_data:
                try:
                    days_open = (_dt.today() - _dt.strptime(r["created_at"], "%Y-%m-%d")).days
                except Exception:
                    days_open = 0
                urgency = "🔴 Critical" if days_open > 30 else ("🟠 High" if days_open > 14 else "🟡 Normal")
                ov_rows.append({
                    "Job #":        r["work_order"],
                    "Customer":     r["customer_name"],
                    "Technician":   r.get("tech_name") or "Unassigned",
                    "Labour (h)":   r["labour_time"],
                    "Days Open":    days_open,
                    "Urgency":      urgency,
                    "Notes":        (r.get("notes") or "")[:40],
                })
            ov_df = pd.DataFrame(ov_rows)
            st.dataframe(
                ov_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Days Open": st.column_config.NumberColumn("Days Open", format="%d days"),
                    "Labour (h)": st.column_config.NumberColumn("Labour (h)", format="%.1f h"),
                },
            )
            total_overdue = len(ov_rows)
            critical = sum(1 for r in ov_rows if "Critical" in r["Urgency"])
            st.caption(f"**{total_overdue}** open jobs · **{critical}** critical (>30 days)")
        else:
            st.success("✅ No open or overdue jobs!")

    with bot2:
        st.markdown('<div class="sec-header">📅 Job History — Completed Jobs</div>', unsafe_allow_html=True)
        conn_hi = get_conn()
        history_data = [dict(r) for r in conn_hi.execute("""
            SELECT work_order, customer_name, tech_name,
                   travel_time, labour_time, completion_date, notes
            FROM tbl_work_orders
            WHERE status = 'Completed'
            ORDER BY completion_date DESC
            LIMIT 50
        """).fetchall()]
        conn_hi.close()

        if history_data:
            # Search/filter bar for history
            hist_search = st.text_input(
                "🔍 Filter history", placeholder="Customer or job #…",
                key="hist_search", label_visibility="collapsed"
            )
            if hist_search:
                history_data = [
                    r for r in history_data
                    if hist_search.lower() in r["customer_name"].lower()
                    or hist_search.lower() in r["work_order"].lower()
                ]

            hist_rows = [{
                "Job #":           r["work_order"],
                "Customer":        r["customer_name"],
                "Technician":      r.get("tech_name") or "—",
                "Travel (h)":      r["travel_time"],
                "Labour (h)":      r["labour_time"],
                "Completed":       r.get("completion_date") or "—",
                "Notes":           (r.get("notes") or "")[:40],
            } for r in history_data]

            hist_df = pd.DataFrame(hist_rows)
            st.dataframe(
                hist_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Travel (h)":  st.column_config.NumberColumn("Travel (h)",  format="%.1f h"),
                    "Labour (h)":  st.column_config.NumberColumn("Labour (h)",  format="%.1f h"),
                    "Completed":   st.column_config.TextColumn("Completed"),
                },
            )
            total_hrs = sum(r["Labour (h)"] for r in hist_rows)
            st.caption(f"**{len(hist_rows)}** completed jobs · **{total_hrs:.1f}h** total labour")
        else:
            st.info("No completed jobs yet.")


# ════════════════════════════════════════════════════════════════════
# CUSTOMERS
# ════════════════════════════════════════════════════════════════════
elif "Customers" in page:
    st.markdown("## 👥 Customer Management")

    conn = get_conn()
    rows = [dict(r) for r in conn.execute("SELECT * FROM tbl_customers ORDER BY Customer_ID").fetchall()]
    conn.close()

    cc1, cc2 = st.columns([3, 1])
    search = cc1.text_input("🔍 Search", placeholder="Company, contact, email…", label_visibility="collapsed")
    new_cust = cc2.button("+ Add Customer")

    if new_cust:
        with st.form("new_cust_form"):
            st.markdown("### New Customer")
            nc1, nc2 = st.columns(2)
            nc_co    = nc1.text_input("Company Name")
            nc_name  = nc2.text_input("Customer Name")
            nc_addr  = nc1.text_input("Address")
            nc_phone = nc2.text_input("Phone")
            nc_email = nc1.text_input("Email")
            nc_cont  = nc2.text_input("Contact Number")
            sub = st.form_submit_button("✔ Save Customer")
            if sub and nc_co:
                conn2 = get_conn()
                conn2.execute("""INSERT INTO tbl_customers
                    ("Company Name","Customer Name",Address,Address1,"Contact Number",Phone,Email)
                    VALUES (?,?,?,?,?,?,?)""",
                    (nc_co, nc_name, nc_addr, nc_addr, nc_cont, nc_phone, nc_email))
                conn2.commit(); conn2.close()
                st.success("Customer saved!"); st.rerun()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", len(rows))
    col2.metric("Active Accounts", len(rows))
    col3.metric("Locations", len(set(r.get("Address","").split(",")[-1].strip() for r in rows if r.get("Address"))))

    filtered = [r for r in rows if not search or
                search.lower() in (r.get("Company Name","") or "").lower() or
                search.lower() in (r.get("Customer Name","") or "").lower() or
                search.lower() in (r.get("Email","") or "").lower()]

    st.markdown('<div class="sec-header">Customer Accounts</div>', unsafe_allow_html=True)
    df = pd.DataFrame([{
        "ID": r["Customer_ID"],
        "Company": r.get("Company Name",""),
        "Contact": r.get("Customer Name",""),
        "Phone": r.get("Phone",""),
        "Email": r.get("Email",""),
        "Address": r.get("Address",""),
    } for r in filtered])
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No customers found.")


# ════════════════════════════════════════════════════════════════════
# INVENTORY
# ════════════════════════════════════════════════════════════════════
elif "Inventory" in page:
    st.markdown("## 📦 Inventory Management")

    conn = get_conn()
    rows = [dict(r) for r in conn.execute("SELECT * FROM tbl_product_list ORDER BY Product_code").fetchall()]
    conn.close()

    low_stock = [r for r in rows if r.get("quantity", 0) < 10]

    ic1, ic2, ic3 = st.columns(3)
    ic1.metric("Total SKUs", len(rows))
    ic2.metric("Low Stock (<10)", len(low_stock))
    ic3.metric("Est. Value", "$12,450")

    st.markdown("---")

    tcol1, tcol2, tcol3 = st.columns([2, 1, 1])
    search = tcol1.text_input("🔍 Search", placeholder="Product name, code…", label_visibility="collapsed")
    low_only = tcol2.checkbox("Low stock only")
    add_item = tcol3.button("+ Add Item")

    if add_item:
        with st.form("add_inv"):
            st.markdown("### Add Inventory Item")
            ai1, ai2 = st.columns(2)
            ai_code = ai1.text_input("Part Code")
            ai_desc = ai2.text_input("Description")
            ai_qty  = ai1.number_input("Quantity", 1, step=1)
            sub = st.form_submit_button("✔ Save")
            if sub and ai_code:
                conn2 = get_conn()
                ex = conn2.execute("SELECT id,quantity FROM tbl_product_list WHERE Product_code=?", (ai_code,)).fetchone()
                if ex:
                    conn2.execute("UPDATE tbl_product_list SET quantity=quantity+? WHERE id=?", (ai_qty, ex[0]))
                    st.success(f"Added {ai_qty} to existing {ai_code}.")
                else:
                    conn2.execute("""INSERT INTO tbl_product_list
                        (Product_code,product_number,product_name,Product_Description,description,quantity)
                        VALUES (?,?,?,?,?,?)""", (ai_code,ai_code,ai_desc,ai_desc,ai_desc,ai_qty))
                    st.success(f"New item {ai_code} added.")
                conn2.commit(); conn2.close(); st.rerun()

    filtered = [r for r in rows if not search or
                search.lower() in r.get("Product_code","").lower() or
                search.lower() in r.get("Product_Description","").lower()]
    if low_only:
        filtered = [r for r in filtered if r.get("quantity",0) < 10]

    st.markdown('<div class="sec-header">Product Inventory</div>', unsafe_allow_html=True)
    df = pd.DataFrame([{
        "Code": r["Product_code"],
        "Product Name": r.get("product_name",""),
        "Description": r.get("Product_Description",""),
        "Qty": r.get("quantity",0),
        "Stock Status": "⚠️ Low" if r.get("quantity",0) < 10 else "✅ OK",
    } for r in filtered])
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No products found.")

    # Adjust stock
    st.markdown("---")
    st.markdown("**Adjust Stock**")
    acol1, acol2, acol3 = st.columns([2, 1, 1])
    codes = [r["Product_code"] for r in rows]
    sel_code = acol1.selectbox("Select product", codes, label_visibility="collapsed")
    adj_qty = acol2.number_input("Qty", 1, step=1, label_visibility="collapsed")
    acol3a, acol3b = acol3.columns(2)
    if acol3a.button("+ Add"):
        conn2 = get_conn()
        conn2.execute("UPDATE tbl_product_list SET quantity=quantity+? WHERE Product_code=?", (adj_qty, sel_code))
        conn2.commit(); conn2.close()
        st.success(f"Added {adj_qty} to {sel_code}"); st.rerun()
    if acol3b.button("- Remove"):
        conn2 = get_conn()
        cur = conn2.execute("SELECT quantity FROM tbl_product_list WHERE Product_code=?", (sel_code,)).fetchone()
        if cur and cur[0] >= adj_qty:
            conn2.execute("UPDATE tbl_product_list SET quantity=quantity-? WHERE Product_code=?", (adj_qty, sel_code))
            conn2.commit()
            st.success(f"Removed {adj_qty} from {sel_code}")
        else:
            st.error("Insufficient stock.")
        conn2.close(); st.rerun()


# ════════════════════════════════════════════════════════════════════
# INVOICES
# ════════════════════════════════════════════════════════════════════
elif "Invoices" in page:
    st.markdown("## 🧾 Invoices")

    invs = st.session_state.invoices
    total = sum(i["amount"] for i in invs)
    paid  = sum(i["amount"] for i in invs if i["status"] == "Paid")
    over  = sum(i["amount"] for i in invs if i["status"] == "Overdue")

    ic1, ic2, ic3 = st.columns(3)
    ic1.metric("Total Invoiced", f"${total:,.0f}")
    ic2.metric("Paid", f"${paid:,.0f}")
    ic3.metric("Overdue", f"${over:,.0f}")

    st.markdown("---")

    fcol1, fcol2, fcol3 = st.columns([2, 2, 1])
    search = fcol1.text_input("🔍 Search", placeholder="Customer, invoice #…", label_visibility="collapsed")
    status_f = fcol2.selectbox("Filter", ["All","Draft","Sent","Paid","Overdue"], label_visibility="collapsed")
    new_inv = fcol3.button("+ New Invoice")

    if new_inv:
        with st.form("new_inv_form"):
            st.markdown("### New Invoice")
            nif1, nif2 = st.columns(2)
            ni_cust = nif1.text_input("Customer")
            ni_date = nif2.text_input("Invoice Date", str(date.today()))
            ni_due  = nif1.text_input("Due Date", "")
            ni_stat = nif2.selectbox("Status", ["Draft","Sent","Paid"])
            st.markdown("**Line Items**")
            lc1, lc2, lc3 = st.columns([3,1,1])
            l_desc  = lc1.text_input("Description")
            l_qty   = lc2.number_input("Qty", 1, step=1)
            l_price = lc3.number_input("Unit Price $", 0.0, step=10.0)
            ni_notes = st.text_input("Notes")
            sub = st.form_submit_button("✔ Save Invoice")
            if sub and ni_cust and l_desc:
                amt = l_qty * l_price * 1.1
                st.session_state.invoices.insert(0, {
                    "id": st.session_state.next_inv_id,
                    "customer": ni_cust, "date": ni_date, "due": ni_due,
                    "amount": amt, "status": ni_stat,
                    "lines": [{"desc": l_desc, "qty": l_qty, "price": l_price}],
                    "notes": ni_notes,
                })
                st.session_state.next_inv_id += 1
                st.success(f"Invoice #{st.session_state.next_inv_id-1} created!"); st.rerun()

    filtered = [i for i in invs
                if (status_f == "All" or i["status"] == status_f)
                and (not search or search.lower() in i["customer"].lower() or search in str(i["id"]))]

    st.markdown('<div class="sec-header">Invoice Log</div>', unsafe_allow_html=True)
    status_emoji_inv = {"Paid":"🟢","Overdue":"🔴","Sent":"🔵","Draft":"⚪"}
    df = pd.DataFrame([{
        "Invoice #": f"#{i['id']}",
        "Customer": i["customer"],
        "Date": i["date"],
        "Due": i["due"],
        "Amount": f"${i['amount']:,.2f}",
        "Status": f"{status_emoji_inv.get(i['status'],'⚪')} {i['status']}",
    } for i in filtered])

    if not df.empty:
        selected = st.dataframe(df, use_container_width=True, hide_index=True,
                                on_select="rerun", selection_mode="single-row")
        sel_rows = selected.selection.rows if selected else []
        if sel_rows:
            inv = filtered[sel_rows[0]]
            with st.expander(f"📄 Invoice #{inv['id']} — {inv['customer']}", expanded=True):
                vc1, vc2 = st.columns(2)
                vc1.write(f"**Date:** {inv['date']}  |  **Due:** {inv['due']}")
                vc2.write(f"**Status:** {inv['status']}")
                st.markdown("---")
                sub_total = 0
                for line in inv.get("lines",[]):
                    amt = line["qty"] * line["price"]
                    sub_total += amt
                    st.write(f"- {line['desc']} × {line['qty']} @ ${line['price']:,.2f} = **${amt:,.2f}**")
                st.markdown("---")
                st.write(f"Subtotal: ${sub_total:,.2f}  |  GST (10%): ${sub_total*.1:,.2f}  |  **Total: ${sub_total*1.1:,.2f}**")
                if inv.get("notes"):
                    st.write(f"*Note: {inv['notes']}*")
                if inv["status"] != "Paid":
                    if st.button("✓ Mark as Paid", key=f"pay_{inv['id']}"):
                        for i in st.session_state.invoices:
                            if i["id"] == inv["id"]:
                                i["status"] = "Paid"
                        st.success("Marked as Paid!"); st.rerun()
    else:
        st.info("No invoices found.")


# ════════════════════════════════════════════════════════════════════
# REGULAR SERVICE
# ════════════════════════════════════════════════════════════════════
elif "Service" in page:
    st.markdown("## 🔧 Regular Service")

    conn = get_conn()
    machines = [dict(r) for r in conn.execute("""
        SELECT m."Machine ID", m."Model Number", m.Type, m.Manufacturer,
               c."Company Name", s.*
        FROM tbl_machine m
        LEFT JOIN tbl_customers c ON m."Customer ID" = c.Customer_ID
        LEFT JOIN tbl_regular_service_months s ON m."Machine ID" = s."Machine ID"
        ORDER BY m."Machine ID"
    """).fetchall()]
    conn.close()

    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Machines Tracked", len(machines))
    sc2.metric("Services Due", 3)
    sc3.metric("Overdue", 1)

    st.markdown("---")

    tcol1, tcol2 = st.columns([4,1])
    tcol1.markdown("### PM Schedule — Machine × Month")
    sched_svc = tcol2.button("+ Schedule Service")

    if sched_svc:
        with st.form("sched_form"):
            st.markdown("### Schedule New Service")
            sc_cust  = st.text_input("Customer")
            sc_equip = st.text_input("Equipment")
            sc_int   = st.selectbox("Interval", ["Monthly","Quarterly","6-monthly","Yearly"])
            sc_last  = st.text_input("Last Service Date", str(date.today()))
            sub = st.form_submit_button("✔ Schedule")
            if sub and sc_cust and sc_equip:
                st.success(f"Service scheduled — {sc_cust} / {sc_equip} ({sc_int})"); st.rerun()

    # PM Grid
    st.markdown('<div class="sec-header">Preventive Maintenance Schedule</div>', unsafe_allow_html=True)
    MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    MONTHS_S = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    pm_data = []
    for m in machines:
        row = {"Machine": m.get("Model Number",""), "Customer": m.get("Company Name",""), "Type": m.get("Type","")}
        for mn, ms in zip(MONTHS_S, MONTHS):
            val = str(m.get(ms,"No")).strip().lower()
            row[mn] = "✓" if val in ("yes","1","true") else "·"
        pm_data.append(row)

    pm_df = pd.DataFrame(pm_data)
    st.dataframe(pm_df, use_container_width=True, hide_index=True)

    # Service log
    st.markdown("---")
    st.markdown('<div class="sec-header">Service Job Log</div>', unsafe_allow_html=True)
    svc_log = [
        {"Customer":"Northgate Events","Equipment":"PA System x2","Interval":"Quarterly","Last Service":"2026-01-15","Status":"🟡 Due"},
        {"Customer":"Bayview Hall","Equipment":"Amp rack","Interval":"6-monthly","Last Service":"2025-10-01","Status":"🟡 Due"},
        {"Customer":"Metro Church","Equipment":"Mixer + mics","Interval":"Yearly","Last Service":"2025-03-20","Status":"🔴 Overdue"},
        {"Customer":"Clarke Industries","Equipment":"Line array","Interval":"6-monthly","Last Service":"2026-02-10","Status":"🟢 OK"},
        {"Customer":"Riverside Events","Equipment":"Stage monitors","Interval":"Yearly","Last Service":"2025-11-05","Status":"🟢 OK"},
        {"Customer":"Greenfield Hotels","Equipment":"Ballroom PA","Interval":"Quarterly","Last Service":"2026-01-20","Status":"🟡 Due"},
    ]
    st.dataframe(pd.DataFrame(svc_log), use_container_width=True, hide_index=True)