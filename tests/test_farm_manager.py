"""
tests/test_farm_manager.py  –  FarmPro v3
==========================================
Suite complète : 74 tests couvrant les 8 modules.
Lancer : pytest tests/ -v
"""
import sys, os, tempfile
import pytest

# ── Fixtures ────────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def managers():
    tmp = tempfile.mkdtemp()
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import farm_manager as fm
    fm.DATA_DIR          = tmp
    fm.ANIMALS_FILE      = os.path.join(tmp, "animals.json")
    fm.FEEDS_FILE        = os.path.join(tmp, "feeds.json")
    fm.FEEDING_LOG_FILE  = os.path.join(tmp, "feeding_log.json")
    fm.HEALTH_REC_FILE   = os.path.join(tmp, "health_records.json")
    fm.MEDICINES_FILE    = os.path.join(tmp, "medicines.json")
    fm.CROPS_FILE        = os.path.join(tmp, "crops.json")
    fm.PRODUCTION_FILE   = os.path.join(tmp, "production.json")
    fm.EXPENSES_FILE     = os.path.join(tmp, "expenses.json")
    fm.SALES_FILE        = os.path.join(tmp, "sales.json")
    return fm.create_managers()


# ═══════════════════════════════════════════════════════════
# 1 · AnimalManager  (15 tests)
# ═══════════════════════════════════════════════════════════
class TestAnimalManager:

    def test_seed_data_loaded(self, managers):
        assert len(managers["animals"].get_all()) > 0

    def test_animal_has_name_field(self, managers):
        a = managers["animals"].get_all()[0]
        assert "name" in a and a["name"] != ""

    def test_animal_has_transport_cost_da(self, managers):
        a = managers["animals"].get_all()[0]
        assert "transport_cost_da" in a

    def test_animal_has_purchase_price_da(self, managers):
        a = managers["animals"].get_all()[0]
        assert "purchase_price_da" in a

    def test_filter_status_alive(self, managers):
        result = managers["animals"].get_all(status="alive")
        assert all(a["status"] == "alive" for a in result)

    def test_filter_by_type_cattle(self, managers):
        result = managers["animals"].get_all(animal_type="Cattle")
        assert all(a["type"] == "Cattle" for a in result)

    def test_filter_by_gender_female(self, managers):
        result = managers["animals"].get_all(gender="Female")
        assert all(a["gender"] == "Female" for a in result)

    def test_filter_by_source_purchase(self, managers):
        result = managers["animals"].get_all(source="purchase")
        assert all(a["source"] == "purchase" for a in result)

    def test_search_by_name(self, managers):
        result = managers["animals"].get_all(search="nour")
        assert len(result) > 0

    def test_add_animal_with_transport(self, managers):
        a = managers["animals"].add({
            "name": "Bourak", "type": "Sheep", "breed": "Ouled Djellal",
            "purchase_price_da": 35000, "transport_cost_da": 1800
        })
        assert a["name"] == "Bourak"
        assert a["transport_cost_da"] == 1800.0
        assert a["status"] == "alive"

    def test_update_animal_fields(self, managers):
        A = managers["animals"]
        aid = A.get_all()[0]["id"]
        r = A.update(aid, {"name": "NomModifié", "weight_kg": 250})
        assert r["success"] is True
        assert r["animal"]["name"] == "NomModifié"

    def test_update_status_to_sold(self, managers):
        A = managers["animals"]
        a = A.add({"name": "AVendre", "type": "Goat"})
        r = A.update_status(a["id"], "sold")
        assert r["success"] is True
        assert r["animal"]["status"] == "sold"

    def test_delete_animal(self, managers):
        A = managers["animals"]
        a = A.add({"name": "ASuppr", "type": "Other"})
        r = A.delete(a["id"])
        assert r["success"] is True
        assert A.get_by_id(a["id"]) is None

    def test_mortality_rate_between_0_and_100(self, managers):
        rate = managers["animals"].mortality_rate()
        assert 0.0 <= rate <= 100.0

    def test_export_csv_has_transport_column(self, managers):
        assert "transport_cost_da" in managers["animals"].export_csv()


# ═══════════════════════════════════════════════════════════
# 2 · FeedManager  (11 tests)
# ═══════════════════════════════════════════════════════════
class TestFeedManager:

    def test_seed_data_loaded(self, managers):
        assert len(managers["feeds"].get_inventory()) > 0

    def test_origin_field_valid_values(self, managers):
        valid = {"Local", "Importé", "Produit à la ferme"}
        for f in managers["feeds"].get_inventory():
            assert f["origin"] in valid

    def test_transport_cost_field_exists(self, managers):
        assert "transport_cost_da" in managers["feeds"].get_inventory()[0]

    def test_min_stock_kg_field_exists(self, managers):
        assert "min_stock_kg" in managers["feeds"].get_inventory()[0]

    def test_filter_by_origin_local(self, managers):
        result = managers["feeds"].get_inventory(origin="Local")
        assert all(f["origin"] == "Local" for f in result)

    def test_filter_by_feed_type(self, managers):
        result = managers["feeds"].get_inventory(feed_type="Orge")
        assert all(f["feed_type"] == "Orge" for f in result)

    def test_add_stock_with_all_fields(self, managers):
        item = managers["feeds"].add_stock({
            "feed_type": "Son de blé", "quantity_kg": 150,
            "min_stock_kg": 30, "origin": "Importé",
            "cost_per_kg_da": 35, "transport_cost_da": 1500
        })
        assert item["origin"] == "Importé"
        assert item["transport_cost_da"] == 1500.0

    def test_update_stock(self, managers):
        F = managers["feeds"]
        fid = F.get_inventory()[0]["id"]
        r = F.update_stock(fid, {"quantity_kg": 888})
        assert r["success"] is True
        assert r["item"]["quantity_kg"] == 888.0

    def test_low_stock_alert_logic(self, managers):
        alerts = managers["feeds"].low_stock_alerts()
        for f in alerts:
            assert f["quantity_kg"] <= f["min_stock_kg"]

    def test_stock_by_origin_returns_chart_data(self, managers):
        d = managers["feeds"].stock_by_origin()
        assert "labels" in d and "values" in d

    def test_export_csv_has_origin_column(self, managers):
        assert "origin" in managers["feeds"].export_csv()


# ═══════════════════════════════════════════════════════════
# 3 · HealthManager  (12 tests)
# ═══════════════════════════════════════════════════════════
class TestHealthManager:

    def test_records_seed_loaded(self, managers):
        assert len(managers["health"].get_records()) > 0

    def test_record_has_animal_name(self, managers):
        assert "animal_name" in managers["health"].get_records()[0]

    def test_record_has_cost_da(self, managers):
        assert "cost_da" in managers["health"].get_records()[0]

    def test_filter_records_by_type(self, managers):
        recs = managers["health"].get_records(record_type="vaccination")
        assert all(r["record_type"] == "vaccination" for r in recs)

    def test_add_record_with_cost_da(self, managers):
        r = managers["health"].add_record({
            "animal_id": 1, "animal_name": "Nour", "animal_type": "Cattle",
            "record_type": "disease", "disease": "Grippe bovine",
            "cost_da": 5500, "resolved": False
        })
        assert r["cost_da"] == 5500.0
        assert r["resolved"] is False

    def test_update_record_resolved(self, managers):
        H = managers["health"]
        rid = H.get_records()[0]["id"]
        r = H.update_record(rid, {"resolved": True, "cost_da": 9999})
        assert r["success"] is True
        assert r["record"]["cost_da"] == 9999.0

    def test_ongoing_cases_all_unresolved(self, managers):
        ongoing = managers["health"].ongoing_cases()
        assert all(not r["resolved"] for r in ongoing)

    def test_medicines_seed_loaded(self, managers):
        assert len(managers["health"].get_medicines()) > 0

    def test_medicine_has_min_quantity(self, managers):
        assert "min_quantity" in managers["health"].get_medicines()[0]

    def test_low_stock_medicines_logic(self, managers):
        low = managers["health"].low_stock_medicines()
        for m in low:
            assert m["quantity"] <= m["min_quantity"]

    def test_low_stock_medicines_detects_seed(self, managers):
        """Vaccin FMDV (qty=4) < min_quantity(5) → détecté"""
        low = managers["health"].low_stock_medicines()
        names = [m["name"] for m in low]
        assert any("FMDV" in n or "Vaccin" in n for n in names)

    def test_update_medicine(self, managers):
        H = managers["health"]
        mid = H.get_medicines()[0]["id"]
        r = H.update_medicine(mid, {"quantity": 99})
        assert r["success"] is True
        assert r["medicine"]["quantity"] == 99

    def test_expiring_soon_returns_all_when_9999_days(self, managers):
        exp = managers["health"].expiring_soon(days=9999)
        total = len(managers["health"].get_medicines())
        assert len(exp) == total


# ═══════════════════════════════════════════════════════════
# 4 · CropManager  (9 tests)
# ═══════════════════════════════════════════════════════════
class TestCropManager:

    def test_seed_data_loaded(self, managers):
        assert len(managers["crops"].get_all()) > 0

    def test_transport_cost_field_exists(self, managers):
        assert "transport_cost_da" in managers["crops"].get_all()[0]

    def test_filter_by_status_recolte(self, managers):
        result = managers["crops"].get_all(status="Récolté")
        assert all(c["status"] == "Récolté" for c in result)

    def test_search_by_name(self, managers):
        result = managers["crops"].get_all(search="blé")
        assert len(result) > 0

    def test_add_crop_with_transport(self, managers):
        c = managers["crops"].add({
            "name": "Lentilles", "variety": "Verte", "area_ha": 2.5,
            "status": "Planté", "seed_cost_da": 12000,
            "transport_cost_da": 3500, "sale_price_da_per_ton": 7000
        })
        assert c["transport_cost_da"] == 3500.0

    def test_update_crop_yield_and_status(self, managers):
        C = managers["crops"]
        cid = C.get_all()[0]["id"]
        r = C.update(cid, {"yield_ton": 45.0, "status": "Récolté"})
        assert r["success"] is True
        assert r["crop"]["yield_ton"] == 45.0

    def test_total_revenue_da_positive(self, managers):
        assert managers["crops"].total_revenue_da() > 0

    def test_profit_by_crop_chart_data(self, managers):
        d = managers["crops"].profit_by_crop()
        assert "labels" in d and "values" in d

    def test_export_csv_has_transport_and_revenue(self, managers):
        csv = managers["crops"].export_csv()
        assert "transport_cost_da" in csv
        assert "sale_price_da_per_ton" in csv


# ═══════════════════════════════════════════════════════════
# 5 · ProductionManager  (8 tests)
# ═══════════════════════════════════════════════════════════
class TestProductionManager:

    def test_seed_data_loaded(self, managers):
        assert len(managers["production"].get_all()) > 0

    def test_record_has_animal_name(self, managers):
        assert "animal_name" in managers["production"].get_all()[0]

    def test_record_price_in_da(self, managers):
        assert "price_per_unit_da" in managers["production"].get_all()[0]

    def test_filter_by_product_type_milk(self, managers):
        milk = managers["production"].get_all(product_type="milk")
        assert all(r["product_type"] == "milk" for r in milk)

    def test_filter_by_animal_type(self, managers):
        cattle = managers["production"].get_all(animal_type="Cattle")
        assert all(r["animal_type"] == "Cattle" for r in cattle)

    def test_add_record_with_da_price(self, managers):
        r = managers["production"].add_record({
            "product_type": "eggs", "quantity": 30, "price_per_unit_da": 30,
            "animal_type": "Poultry", "animal_name": "Nadia"
        })
        assert r["price_per_unit_da"] == 30.0
        assert r["animal_name"] == "Nadia"

    def test_update_record(self, managers):
        P = managers["production"]
        rid = P.get_all()[0]["id"]
        r = P.update_record(rid, {"quantity": 88.0})
        assert r["success"] is True

    def test_export_csv_has_animal_name(self, managers):
        assert "animal_name" in managers["production"].export_csv()


# ═══════════════════════════════════════════════════════════
# 6 · ExpenseManager  (10 tests)
# ═══════════════════════════════════════════════════════════
class TestExpenseManager:

    def test_seed_data_loaded(self, managers):
        assert len(managers["expenses"].get_all()) > 0

    def test_transport_category_present_in_seed(self, managers):
        transport = managers["expenses"].get_all(category="transport")
        assert len(transport) > 0

    def test_filter_by_category(self, managers):
        feed = managers["expenses"].get_all(category="feed")
        assert all(e["category"] == "feed" for e in feed)

    def test_filter_by_month(self, managers):
        result = managers["expenses"].get_all(month="2024-01")
        assert all(e["date"].startswith("2024-01") for e in result)

    def test_filter_by_search_text(self, managers):
        result = managers["expenses"].get_all(search="salaire")
        assert len(result) > 0

    def test_add_expense_with_all_fields(self, managers):
        e = managers["expenses"].add({
            "date": "2024-05-10", "category": "transport",
            "sub_category": "Transport récolte",
            "description": "Transport orge au silo", "amount_da": 9500,
            "payment_method": "espèces"
        })
        assert e["amount_da"] == 9500.0
        assert e["category"] == "transport"

    def test_update_expense(self, managers):
        E = managers["expenses"]
        eid = E.get_all()[0]["id"]
        r = E.update(eid, {"amount_da": 77777})
        assert r["success"] is True
        assert r["expense"]["amount_da"] == 77777.0

    def test_transport_total_da_positive(self, managers):
        total = managers["expenses"].transport_total_da()
        assert total > 0

    def test_by_category_chart_data(self, managers):
        d = managers["expenses"].by_category()
        assert "labels" in d and "values" in d and "keys" in d

    def test_export_csv_has_amount_da(self, managers):
        assert "amount_da" in managers["expenses"].export_csv()


# ═══════════════════════════════════════════════════════════
# 7 · SalesManager  (7 tests)
# ═══════════════════════════════════════════════════════════
class TestSalesManager:

    def test_seed_data_loaded(self, managers):
        assert len(managers["sales"].get_all()) > 0

    def test_transaction_has_animal_name(self, managers):
        assert "animal_name" in managers["sales"].get_all()[0]

    def test_transaction_has_transport_cost(self, managers):
        assert "transport_cost_da" in managers["sales"].get_all()[0]

    def test_filter_by_transaction_type(self, managers):
        sales = managers["sales"].get_all(transaction_type="sale")
        assert all(t["transaction_type"] == "sale" for t in sales)

    def test_add_transaction_total_da_calculated(self, managers):
        """total_da = quantity × prix/tête + transport"""
        t = managers["sales"].add_transaction({
            "transaction_type": "sale", "animal_name": "Lot agneaux",
            "animal_type": "Sheep", "quantity": 4,
            "price_per_head_da": 38000, "transport_cost_da": 3000
        })
        assert t["total_da"] == 4 * 38000 + 3000

    def test_update_transaction_recalculates_total(self, managers):
        S = managers["sales"]
        t = S.add_transaction({
            "transaction_type": "sale", "animal_name": "TestUpdate",
            "animal_type": "Cattle", "quantity": 1,
            "price_per_head_da": 100000, "transport_cost_da": 0
        })
        r = S.update_transaction(t["id"], {
            "quantity": 1, "price_per_head_da": 50000, "transport_cost_da": 2500
        })
        assert r["success"] is True
        assert r["transaction"]["total_da"] == 52500.0

    def test_total_income_da_positive(self, managers):
        assert managers["sales"].total_income_da() > 0


# ═══════════════════════════════════════════════════════════
# 8 · ReportManager  (7 tests)
# ═══════════════════════════════════════════════════════════
class TestReportManager:

    def test_dashboard_kpis_all_keys_present(self, managers):
        kpis = managers["report"].dashboard_kpis()
        required = [
            "total_animals", "alive", "sold", "dead", "mortality_rate",
            "feed_stock_da", "production_rev_da", "sales_income_da",
            "total_expenses_da", "crop_revenue_da",
            "active_crops", "total_area_ha", "transport_total_da"
        ]
        for k in required:
            assert k in kpis, f"KPI manquant : {k}"

    def test_kpis_transport_total_da_positive(self, managers):
        kpis = managers["report"].dashboard_kpis()
        assert kpis["transport_total_da"] > 0

    def test_all_alerts_structure(self, managers):
        alerts = managers["report"].all_alerts()
        for key in ["low_feed", "expiring_meds", "low_meds", "ongoing_health"]:
            assert key in alerts
            assert isinstance(alerts[key], list)

    def test_total_alerts_count_is_int(self, managers):
        count = managers["report"].total_alerts_count()
        assert isinstance(count, int) and count >= 0

    def test_profit_loss_net_equals_income_minus_expenses(self, managers):
        pl = managers["report"].profit_loss()
        expected_net = round(pl["income"] - pl["expenses"], 2)
        assert pl["net"] == expected_net

    def test_profit_loss_includes_crop_revenue(self, managers):
        pl = managers["report"].profit_loss()
        assert "crop_revenue" in pl
        assert pl["crop_revenue"] >= 0

    def test_monthly_overview_consistent_lengths(self, managers):
        ov = managers["report"].monthly_overview()
        assert "months" in ov and "sales" in ov and "expenses" in ov
        assert len(ov["months"]) == len(ov["sales"]) == len(ov["expenses"])
