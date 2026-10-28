"""Car Service Center website - Flask + Oracle XE 11.2.
Run: set DB_USER/DB_PASS (and ORACLE_CLIENT if needed), then  python app.py"""
import os, oracledb
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__); app.secret_key = "car-service-center"
CFG = dict(user=os.getenv("DB_USER", "system"), password=os.getenv("DB_PASS", "oracle"),
           dsn=os.getenv("DB_DSN", "localhost/XE"))
try:  # Oracle 11g needs thick mode (Oracle client libraries)
    oracledb.init_oracle_client(lib_dir=os.getenv("ORACLE_CLIENT") or None)
except Exception as e:
    print("thick mode note:", e)

def query(sql):
    with oracledb.connect(**CFG) as c:
        cur = c.cursor(); cur.execute(sql)
        return [d[0] for d in cur.description], cur.fetchall()

def run(fn):
    with oracledb.connect(**CFG) as c:
        cur = c.cursor(); msg = fn(cur); c.commit(); return msg

LISTS = {
 "customers": "SELECT cust_id, name, phone, email, address FROM customers ORDER BY 1",
 "vehicles": "SELECT v.vehicle_id, c.name customer, v.reg_no, v.make||' '||v.model car, v.fuel_type FROM vehicles v JOIN customers c ON c.cust_id=v.cust_id ORDER BY 1",
 "orders": "SELECT o.order_id, v.reg_no, s.service_name, m.name mechanic, o.status, TO_CHAR(o.order_date,'DD-Mon-YYYY') order_date FROM service_orders o JOIN vehicles v ON v.vehicle_id=o.vehicle_id JOIN services s ON s.service_id=o.service_id LEFT JOIN mechanics m ON m.mech_id=o.mech_id ORDER BY 1 DESC",
 "parts": "SELECT part_id, part_name, unit_price, stock_qty, reorder_level FROM spare_parts ORDER BY 1",
 "billing": "SELECT bill_id, order_id, labour_cost, parts_cost, gst_amount, total_amount, payment_mode FROM billing ORDER BY 1 DESC",
}
F = lambda *a: list(a)
FORMS = {
 "customers": [("add_customer", "Register customer", [F("name","Name","text"),F("phone","Phone (10 digits)","text"),F("email","Email","text"),F("address","Address","text")])],
 "vehicles": [("add_vehicle", "Register vehicle", [F("cust_id","Customer ID","number"),F("reg_no","Reg. number","text"),F("make","Make","text"),F("model","Model","text"),F("year","Year","number"),F("fuel","Fuel","select:Petrol,Diesel,Electric,CNG")])],
 "orders": [("new_order", "New service order (auto-assigns mechanic)", [F("vehicle_id","Vehicle ID","number"),F("service_id","Service ID (1-10)","number"),F("remarks","Remarks","text")]),
            ("add_part", "Add spare part", [F("order_id","Order ID","number"),F("part_id","Part ID","number"),F("qty","Quantity","number")]),
            ("complete", "Complete order", [F("order_id","Order ID","number")]),
            ("bill", "Generate bill", [F("order_id","Order ID","number"),F("mode","Payment","select:Cash,Card,UPI")]),
            ("bill_all", "Bill all completed orders (cursor)", [])],
 "parts": [("restock", "Restock part", [F("part_id","Part ID","number"),F("qty","Quantity to add","number")])],
}
def i(f, k): return int(f[k])
ACTIONS = {
 "add_customer": lambda c, f: c.execute("INSERT INTO customers (cust_id,name,phone,email,address) VALUES (seq_customers.NEXTVAL,:1,:2,:3,:4)", [f["name"], f["phone"], f["email"] or None, f["address"] or None]) or "Customer registered",
 "add_vehicle": lambda c, f: c.execute("INSERT INTO vehicles (vehicle_id,cust_id,reg_no,make,model,mfg_year,fuel_type) VALUES (seq_vehicles.NEXTVAL,:1,:2,:3,:4,:5,:6)", [i(f,"cust_id"), f["reg_no"].upper(), f["make"], f["model"], i(f,"year"), f["fuel"]]) or "Vehicle registered",
 "add_part": lambda c, f: c.callproc("add_part_to_order", [i(f,"order_id"), i(f,"part_id"), i(f,"qty")]) or "Part added - stock reduced by trigger",
 "complete": lambda c, f: c.callproc("complete_order", [i(f,"order_id")]) or "Order completed - mechanic is free again",
 "bill": lambda c, f: c.callproc("generate_bill", [i(f,"order_id"), f["mode"]]) or "Bill generated - order marked Billed",
 "bill_all": lambda c, f: c.callproc("bill_all_completed", ["Cash"]) or "All completed orders billed",
 "restock": lambda c, f: c.execute("UPDATE spare_parts SET stock_qty=stock_qty+:1 WHERE part_id=:2", [i(f,"qty"), i(f,"part_id")]) or "Stock updated",
}
def new_order(c, f):
    out = c.var(int); c.callproc("create_service_order", [i(f,"vehicle_id"), i(f,"service_id"), f["remarks"] or None, out])
    return f"Order {out.getvalue()} created and mechanic assigned"
ACTIONS["new_order"] = new_order
NAV = ["dashboard", "customers", "vehicles", "orders", "parts", "billing"]

@app.route("/")
def dashboard():
    try:
        _, r = query("SELECT (SELECT COUNT(*) FROM customers),(SELECT COUNT(*) FROM service_orders WHERE status IN ('Open','In Progress')),(SELECT COUNT(*) FROM spare_parts WHERE stock_qty<=reorder_level),(SELECT NVL(SUM(total_amount),0) FROM billing) FROM dual")
        stats = [("Customers", r[0][0]), ("Active jobs", r[0][1]), ("Low-stock parts", r[0][2]), ("Revenue (Rs.)", f"{r[0][3]:,.0f}")]
        cols, rows = query(LISTS["orders"])
    except oracledb.Error as e:
        flash(str(e).split("\n")[0], "err"); stats, cols, rows = [], [], []
    return render_template("page.html", page="dashboard", nav=NAV, stats=stats, forms=[], cols=cols, rows=rows[:8])

@app.route("/<page>")
def show(page):
    if page not in LISTS: return redirect(url_for("dashboard"))
    try: cols, rows = query(LISTS[page])
    except oracledb.Error as e: flash(str(e).split("\n")[0], "err"); cols, rows = [], []
    return render_template("page.html", page=page, nav=NAV, stats=[], forms=FORMS.get(page, []), cols=cols, rows=rows)

@app.route("/do/<action>/<page>", methods=["POST"])
def do(action, page):
    try: flash(run(lambda c: ACTIONS[action](c, request.form)), "ok")
    except (oracledb.Error, ValueError) as e: flash("Error: " + str(e).split("\n")[0], "err")
    return redirect(url_for("show", page=page))

if __name__ == "__main__":
    app.run(debug=True)
