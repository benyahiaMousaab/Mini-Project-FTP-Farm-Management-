"""app.py – FarmPro v3"""
from flask import Flask, render_template, request, jsonify, Response
from farm_manager import create_managers

app = Flask(__name__)
mgr = create_managers()
A=mgr["animals"]; F=mgr["feeds"]; H=mgr["health"]; C=mgr["crops"]
P=mgr["production"]; E=mgr["expenses"]; S=mgr["sales"]; R=mgr["report"]

# ── Dashboard ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    alerts = R.all_alerts()
    return render_template("index.html", kpis=R.dashboard_kpis(), alerts=alerts,
                           alert_count=R.total_alerts_count())

# ── Animals ───────────────────────────────────────────────────────────────
@app.route("/animals")
def animals():
    status=request.args.get("status"); atype=request.args.get("type")
    gender=request.args.get("gender"); source=request.args.get("source")
    search=request.args.get("search")
    filtered = A.get_all(status=status,animal_type=atype,gender=gender,source=source,search=search)
    return render_template("animals.html", animals=filtered,
                           filter_status=status, filter_type=atype,
                           filter_gender=gender, filter_source=source, search=search or "")

@app.route("/api/animals", methods=["GET"])
def api_animals(): return jsonify(A.get_all())
@app.route("/api/animals", methods=["POST"])
def api_add_animal(): return jsonify(A.add(request.get_json())), 201
@app.route("/api/animals/<int:aid>", methods=["DELETE"])
def api_del_animal(aid): return jsonify(A.delete(aid))
@app.route("/api/animals/<int:aid>", methods=["PUT"])
def api_update_animal(aid): return jsonify(A.update(aid, request.get_json()))
@app.route("/api/animals/<int:aid>/status", methods=["PATCH"])
def api_animal_status(aid): return jsonify(A.update_status(aid, request.get_json().get("status","alive")))
@app.route("/api/export/animals")
def export_animals():
    return Response(A.export_csv(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment;filename=animaux.csv"})

# ── Feeds ─────────────────────────────────────────────────────────────────
@app.route("/feeds")
def feeds():
    origin=request.args.get("origin"); ftype=request.args.get("feed_type")
    return render_template("feeds.html",
                           inventory=F.get_inventory(origin=origin,feed_type=ftype),
                           log=F.get_feeding_log()[:30],
                           low_stock=F.low_stock_alerts(),
                           filter_origin=origin, filter_type=ftype)

@app.route("/api/feeds", methods=["GET"])
def api_feeds(): return jsonify(F.get_inventory())
@app.route("/api/feeds", methods=["POST"])
def api_add_feed(): return jsonify(F.add_stock(request.get_json())), 201
@app.route("/api/feeds/<int:fid>", methods=["DELETE"])
def api_del_feed(fid): return jsonify(F.delete_stock(fid))
@app.route("/api/feeds/<int:fid>", methods=["PUT"])
def api_update_feed(fid): return jsonify(F.update_stock(fid, request.get_json()))
@app.route("/api/feeding-log", methods=["POST"])
def api_log_feeding(): return jsonify(F.log_feeding(request.get_json())), 201
@app.route("/api/export/feeds")
def export_feeds():
    return Response(F.export_csv(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment;filename=aliments.csv"})

# ── Health ────────────────────────────────────────────────────────────────
@app.route("/health")
def health():
    rtype=request.args.get("record_type"); atype=request.args.get("animal_type")
    return render_template("health.html",
                           records=H.get_records(record_type=rtype,animal_type=atype),
                           medicines=H.get_medicines(),
                           expiring=H.expiring_soon(90),
                           low_meds=H.low_stock_medicines(),
                           ongoing=H.ongoing_cases(),
                           filter_type=rtype, filter_animal=atype)

@app.route("/api/health", methods=["GET"])
def api_health(): return jsonify(H.get_records())
@app.route("/api/health", methods=["POST"])
def api_add_health(): return jsonify(H.add_record(request.get_json())), 201
@app.route("/api/health/<int:rid>", methods=["DELETE"])
def api_del_health(rid): return jsonify(H.delete_record(rid))
@app.route("/api/health/<int:rid>", methods=["PUT"])
def api_update_health(rid): return jsonify(H.update_record(rid, request.get_json()))
@app.route("/api/medicines", methods=["GET"])
def api_medicines(): return jsonify(H.get_medicines())
@app.route("/api/medicines", methods=["POST"])
def api_add_medicine(): return jsonify(H.add_medicine(request.get_json())), 201
@app.route("/api/medicines/<int:mid>", methods=["DELETE"])
def api_del_medicine(mid): return jsonify(H.delete_medicine(mid))
@app.route("/api/medicines/<int:mid>", methods=["PUT"])
def api_update_medicine(mid): return jsonify(H.update_medicine(mid, request.get_json()))

# ── Crops ─────────────────────────────────────────────────────────────────
@app.route("/crops")
def crops():
    status=request.args.get("status"); search=request.args.get("search")
    return render_template("crops.html", crops=C.get_all(status=status,search=search),
                           filter_status=status, search=search or "")

@app.route("/api/crops", methods=["GET"])
def api_crops(): return jsonify(C.get_all())
@app.route("/api/crops", methods=["POST"])
def api_add_crop(): return jsonify(C.add(request.get_json())), 201
@app.route("/api/crops/<int:cid>", methods=["DELETE"])
def api_del_crop(cid): return jsonify(C.delete(cid))
@app.route("/api/crops/<int:cid>", methods=["PUT"])
def api_update_crop(cid): return jsonify(C.update(cid, request.get_json()))
@app.route("/api/export/crops")
def export_crops():
    return Response(C.export_csv(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment;filename=cultures.csv"})

# ── Production ────────────────────────────────────────────────────────────
@app.route("/production")
def production():
    ptype=request.args.get("product_type"); atype=request.args.get("animal_type")
    return render_template("production.html", records=P.get_all(product_type=ptype,animal_type=atype)[:60],
                           filter_type=ptype, filter_animal=atype)

@app.route("/api/production", methods=["GET"])
def api_production(): return jsonify(P.get_all())
@app.route("/api/production", methods=["POST"])
def api_add_prod(): return jsonify(P.add_record(request.get_json())), 201
@app.route("/api/production/<int:rid>", methods=["DELETE"])
def api_del_prod(rid): return jsonify(P.delete_record(rid))
@app.route("/api/production/<int:rid>", methods=["PUT"])
def api_update_prod(rid): return jsonify(P.update_record(rid, request.get_json()))
@app.route("/api/export/production")
def export_production():
    return Response(P.export_csv(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment;filename=production.csv"})

# ── Expenses ──────────────────────────────────────────────────────────────
@app.route("/expenses")
def expenses():
    cat=request.args.get("category"); month=request.args.get("month"); search=request.args.get("search")
    return render_template("expenses.html",
                           expenses=E.get_all(category=cat,month=month,search=search),
                           categories=E.CATEGORIES,
                           filter_cat=cat, filter_month=month, search=search or "",
                           total=E.total_da(), transport_total=E.transport_total_da())

@app.route("/api/expenses", methods=["GET"])
def api_expenses(): return jsonify(E.get_all())
@app.route("/api/expenses", methods=["POST"])
def api_add_expense(): return jsonify(E.add(request.get_json())), 201
@app.route("/api/expenses/<int:eid>", methods=["DELETE"])
def api_del_expense(eid): return jsonify(E.delete(eid))
@app.route("/api/expenses/<int:eid>", methods=["PUT"])
def api_update_expense(eid): return jsonify(E.update(eid, request.get_json()))
@app.route("/api/export/expenses")
def export_expenses():
    return Response(E.export_csv(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment;filename=depenses.csv"})

# ── Sales ─────────────────────────────────────────────────────────────────
@app.route("/sales")
def sales():
    ttype=request.args.get("type")
    return render_template("sales.html", transactions=S.get_all(transaction_type=ttype),
                           pl=R.profit_loss(), filter_type=ttype)

@app.route("/api/sales", methods=["GET"])
def api_sales(): return jsonify(S.get_all())
@app.route("/api/sales", methods=["POST"])
def api_add_sale(): return jsonify(S.add_transaction(request.get_json())), 201
@app.route("/api/sales/<int:tid>", methods=["DELETE"])
def api_del_sale(tid): return jsonify(S.delete_transaction(tid))
@app.route("/api/sales/<int:tid>", methods=["PUT"])
def api_update_sale(tid): return jsonify(S.update_transaction(tid, request.get_json()))

# ── Analytics ─────────────────────────────────────────────────────────────
@app.route("/analytics")
def analytics(): return render_template("analytics.html")

@app.route("/api/analytics/animals-by-type")
def api_a_type(): return jsonify(A.by_type())
@app.route("/api/analytics/animals-by-status")
def api_a_status(): return jsonify(A.by_status())
@app.route("/api/analytics/feed-stock")
def api_feed_stock(): return jsonify(F.stock_by_type())
@app.route("/api/analytics/feed-origin")
def api_feed_origin(): return jsonify(F.stock_by_origin())
@app.route("/api/analytics/daily-milk")
def api_milk(): return jsonify(P.daily_milk())
@app.route("/api/analytics/revenue-by-product")
def api_rev(): return jsonify(P.revenue_by_product())
@app.route("/api/analytics/monthly-sales")
def api_msales(): return jsonify(S.monthly_sales())
@app.route("/api/analytics/health-records")
def api_hrec(): return jsonify(H.records_by_type())
@app.route("/api/analytics/health-cost")
def api_hcost(): return jsonify(H.monthly_health_cost())
@app.route("/api/analytics/monthly-overview")
def api_overview(): return jsonify(R.monthly_overview())
@app.route("/api/analytics/profit-loss")
def api_pl(): return jsonify(R.profit_loss())
@app.route("/api/analytics/expenses-by-category")
def api_exp_cat(): return jsonify(E.by_category())
@app.route("/api/analytics/monthly-expenses")
def api_exp_monthly(): return jsonify(E.monthly_expenses())
@app.route("/api/analytics/crop-yield")
def api_crop_yield(): return jsonify(C.yield_per_ha())
@app.route("/api/analytics/crop-profit")
def api_crop_profit(): return jsonify(C.profit_by_crop())
@app.route("/api/analytics/crop-area")
def api_crop_area(): return jsonify(C.area_by_status())

if __name__ == "__main__":
    app.run(debug=True, port=5000)
