-- =====================================================================
-- VIEW ALL TABLES IN A CLEAN FORMAT (SQL*Plus, fits a 120-character window)
-- Run:  @C:\path\to\view_tables.sql
-- =====================================================================
SET LINESIZE 120
SET PAGESIZE 60
SET FEEDBACK ON
SET HEADING ON
SET TRIMOUT ON
SET WRAP OFF

-- ---------- CUSTOMERS ----------
COLUMN cust_id  FORMAT 9999999
COLUMN name     FORMAT A18
COLUMN phone    FORMAT A10
COLUMN email    FORMAT A26
COLUMN address  FORMAT A22
PROMPT
PROMPT ===== CUSTOMERS =====
SELECT * FROM customers ORDER BY cust_id;

-- ---------- VEHICLES ----------
COLUMN vehicle_id FORMAT 9999999999
COLUMN reg_no     FORMAT A12
COLUMN make       FORMAT A9
COLUMN model      FORMAT A10
COLUMN mfg_year   FORMAT 99999999
COLUMN fuel_type  FORMAT A9
PROMPT
PROMPT ===== VEHICLES =====
SELECT * FROM vehicles ORDER BY vehicle_id;

-- ---------- MECHANICS ----------
COLUMN mech_id        FORMAT 9999999
COLUMN specialization FORMAT A14
COLUMN experience_yrs FORMAT 99999999999999
COLUMN status         FORMAT A12
PROMPT
PROMPT ===== MECHANICS =====
SELECT * FROM mechanics ORDER BY mech_id;

-- ---------- SERVICES ----------
COLUMN service_id    FORMAT 9999999999
COLUMN service_name  FORMAT A24
COLUMN labour_charge FORMAT 9999999999.99
PROMPT
PROMPT ===== SERVICES =====
SELECT * FROM services ORDER BY service_id;

-- ---------- SPARE_PARTS ----------
COLUMN part_id       FORMAT 9999999
COLUMN part_name     FORMAT A16
COLUMN unit_price    FORMAT 9999999.99
COLUMN stock_qty     FORMAT 999999999
COLUMN reorder_level FORMAT 9999999999999
PROMPT
PROMPT ===== SPARE_PARTS =====
SELECT * FROM spare_parts ORDER BY part_id;

-- ---------- SERVICE_ORDERS ----------
COLUMN order_id   FORMAT 99999999
COLUMN order_date FORMAT A10
COLUMN remarks    FORMAT A28
PROMPT
PROMPT ===== SERVICE_ORDERS =====
SELECT * FROM service_orders ORDER BY order_id;

-- ---------- ORDER_PARTS ----------
COLUMN op_id FORMAT 99999
COLUMN qty   FORMAT 999
PROMPT
PROMPT ===== ORDER_PARTS =====
SELECT * FROM order_parts ORDER BY op_id;

-- ---------- BILLING ----------
COLUMN bill_id        FORMAT 9999999
COLUMN labour_cost    FORMAT 99999999.99
COLUMN parts_cost     FORMAT 9999999.99
COLUMN gst_amount     FORMAT 9999999.99
COLUMN total_amount   FORMAT 999999999.99
COLUMN payment_mode   FORMAT A12
COLUMN payment_status FORMAT A14
PROMPT
PROMPT ===== BILLING =====
SELECT * FROM billing ORDER BY bill_id;
