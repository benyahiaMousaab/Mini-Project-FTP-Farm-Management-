"""
farm_manager.py  –  FarmPro v3
================================
Modules
-------
1. AnimalManager      – CRUD + name + gender + status + filters
2. FeedManager        – inventory (local/imported/farm) + alerts + transport
3. HealthManager      – disease records + medicines + expiry + stock alerts
4. CropManager        – planting, harvest, yield, costs, transport
5. ProductionManager  – milk, eggs, wool, honey, meat
6. ExpenseManager     – all categories incl. transport, salaries, repairs
7. SalesManager       – animal sales & purchases + transport cost
8. ReportManager      – KPIs, full P&L, all alerts aggregated

Currency : DA (Dinar Algérien)
"""

import json, csv, io, os
from datetime import date
from collections import defaultdict

DATA_DIR           = os.path.join(os.path.dirname(__file__), "data")
ANIMALS_FILE       = os.path.join(DATA_DIR, "animals.json")
FEEDS_FILE         = os.path.join(DATA_DIR, "feeds.json")
FEEDING_LOG_FILE   = os.path.join(DATA_DIR, "feeding_log.json")
HEALTH_REC_FILE    = os.path.join(DATA_DIR, "health_records.json")
MEDICINES_FILE     = os.path.join(DATA_DIR, "medicines.json")
CROPS_FILE         = os.path.join(DATA_DIR, "crops.json")
PRODUCTION_FILE    = os.path.join(DATA_DIR, "production.json")
EXPENSES_FILE      = os.path.join(DATA_DIR, "expenses.json")
SALES_FILE         = os.path.join(DATA_DIR, "sales.json")


def _load(p):
    try:
        with open(p,"r",encoding="utf-8") as f: return json.load(f)
    except: return []

def _save(p,d):
    with open(p,"w",encoding="utf-8") as f: json.dump(d,f,indent=2,ensure_ascii=False)

def _nid(col): return max((x["id"] for x in col),default=0)+1
def _today(): return date.today().isoformat()

def _days_until(s):
    try: return (date.fromisoformat(s)-date.today()).days
    except: return 9999


# ═══════════════════════════════════════════════════════════════════════════
# 1 · AnimalManager
# ═══════════════════════════════════════════════════════════════════════════
class AnimalManager:
    TYPES = ["Cattle","Sheep","Goat","Poultry","Camel","Horse","Donkey","Other"]

    def __init__(self):
        os.makedirs(DATA_DIR,exist_ok=True)
        self._seed(); self.data=_load(ANIMALS_FILE)

    def _seed(self):
        if os.path.exists(ANIMALS_FILE): return
        _save(ANIMALS_FILE,[
            {"id":1,"name":"Nour","type":"Cattle","breed":"Holstein","gender":"Female","birth_date":"2020-03-10","source":"purchase","purchase_price_da":144000,"transport_cost_da":3500,"weight_kg":480,"status":"alive","notes":"Vache laitière","added_date":"2023-01-15"},
            {"id":2,"name":"Atlas","type":"Cattle","breed":"Charolais","gender":"Male","birth_date":"2021-06-01","source":"birth","purchase_price_da":0,"transport_cost_da":0,"weight_kg":520,"status":"alive","notes":"","added_date":"2023-02-10"},
            {"id":3,"name":"Layla","type":"Sheep","breed":"Ouled Djellal","gender":"Female","birth_date":"2022-01-20","source":"purchase","purchase_price_da":36000,"transport_cost_da":1200,"weight_kg":65,"status":"alive","notes":"Bonne laine","added_date":"2023-03-05"},
            {"id":4,"name":"Badr","type":"Sheep","breed":"Hamra","gender":"Male","birth_date":"2022-04-15","source":"birth","purchase_price_da":0,"transport_cost_da":0,"weight_kg":80,"status":"alive","notes":"","added_date":"2023-03-05"},
            {"id":5,"name":"Nadia","type":"Poultry","breed":"Leghorn","gender":"Female","birth_date":"2023-02-01","source":"purchase","purchase_price_da":1800,"transport_cost_da":400,"weight_kg":2,"status":"alive","notes":"Poule pondeuse","added_date":"2023-04-01"},
            {"id":6,"name":"Zéphyr","type":"Goat","breed":"Alpine","gender":"Female","birth_date":"2021-09-12","source":"purchase","purchase_price_da":30000,"transport_cost_da":1500,"weight_kg":55,"status":"alive","notes":"Chèvre laitière","added_date":"2023-05-10"},
            {"id":7,"name":"Rached","type":"Cattle","breed":"Holstein","gender":"Female","birth_date":"2019-11-05","source":"purchase","purchase_price_da":132000,"transport_cost_da":3500,"weight_kg":510,"status":"dead","notes":"Vieillesse","added_date":"2022-06-01"},
        ])

    def get_all(self,status=None,animal_type=None,gender=None,source=None,search=None):
        r=self.data
        if status:      r=[a for a in r if a["status"]==status]
        if animal_type: r=[a for a in r if a["type"]==animal_type]
        if gender:      r=[a for a in r if a["gender"]==gender]
        if source:      r=[a for a in r if a["source"]==source]
        if search:
            s=search.lower()
            r=[a for a in r if s in a["name"].lower() or s in a["breed"].lower() or s in a["type"].lower()]
        return r

    def get_alive(self): return [a for a in self.data if a["status"]=="alive"]
    def get_by_id(self,aid): return next((a for a in self.data if a["id"]==aid),None)

    def add(self,d):
        a={"id":_nid(self.data),"name":d.get("name","Unnamed"),"type":d.get("type","Other"),
           "breed":d.get("breed","Unknown"),"gender":d.get("gender","Female"),
           "birth_date":d.get("birth_date",_today()),"source":d.get("source","purchase"),
           "purchase_price_da":float(d.get("purchase_price_da",0)),
           "transport_cost_da":float(d.get("transport_cost_da",0)),
           "weight_kg":float(d.get("weight_kg",0)),"status":"alive",
           "notes":d.get("notes",""),"added_date":_today()}
        self.data.append(a); _save(ANIMALS_FILE,self.data); return a

    def update(self,aid,d):
        for a in self.data:
            if a["id"]==aid:
                for k in ["name","type","breed","gender","birth_date","source",
                           "purchase_price_da","transport_cost_da","weight_kg","notes"]:
                    if k in d: a[k]=type(a[k])(d[k]) if isinstance(a[k],(int,float)) else d[k]
                _save(ANIMALS_FILE,self.data); return {"success":True,"animal":a}
        return {"success":False,"message":"Not found"}

    def update_status(self,aid,status):
        for a in self.data:
            if a["id"]==aid:
                a["status"]=status; _save(ANIMALS_FILE,self.data)
                return {"success":True,"animal":a}
        return {"success":False,"message":"Not found"}

    def delete(self,aid):
        before=len(self.data)
        self.data=[a for a in self.data if a["id"]!=aid]
        if len(self.data)<before: _save(ANIMALS_FILE,self.data); return {"success":True}
        return {"success":False,"message":"Not found"}

    def by_type(self):
        c=defaultdict(int)
        for a in self.get_alive(): c[a["type"]]+=1
        return {"labels":list(c.keys()),"values":list(c.values())}

    def by_status(self):
        c=defaultdict(int)
        for a in self.data: c[a["status"]]+=1
        return {"labels":list(c.keys()),"values":list(c.values())}

    def mortality_rate(self):
        if not self.data: return 0.0
        return round(sum(1 for a in self.data if a["status"]=="dead")/len(self.data)*100,1)

    def total_investment_da(self):
        return round(sum(a["purchase_price_da"]+a["transport_cost_da"] for a in self.data),2)

    def export_csv(self):
        buf=io.StringIO()
        if not self.data: return ""
        w=csv.DictWriter(buf,fieldnames=self.data[0].keys()); w.writeheader(); w.writerows(self.data)
        return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# 2 · FeedManager
# ═══════════════════════════════════════════════════════════════════════════
class FeedManager:
    FEED_TYPES=["Orge","Foin / Paille","Aliment composé","Ensilage","Son de blé","Maïs","Complément minéral","Autre"]
    ORIGINS   =["Local","Importé","Produit à la ferme"]

    def __init__(self):
        self._seed()
        self.inventory=_load(FEEDS_FILE)
        self.feeding_log=_load(FEEDING_LOG_FILE)

    def _seed(self):
        if not os.path.exists(FEEDS_FILE):
            _save(FEEDS_FILE,[
                {"id":1,"feed_type":"Orge","quantity_kg":500,"min_stock_kg":100,"origin":"Local","purchase_date":"2024-01-10","supplier":"Coopérative Béchar","cost_per_kg_da":54,"transport_cost_da":2000,"notes":"Stock hivernal"},
                {"id":2,"feed_type":"Foin / Paille","quantity_kg":1200,"min_stock_kg":200,"origin":"Produit à la ferme","purchase_date":"2024-01-15","supplier":"Propre ferme","cost_per_kg_da":20,"transport_cost_da":0,"notes":""},
                {"id":3,"feed_type":"Aliment composé","quantity_kg":300,"min_stock_kg":80,"origin":"Importé","purchase_date":"2024-02-01","supplier":"AgriPro Algérie","cost_per_kg_da":96,"transport_cost_da":3500,"notes":"Mélange volailles"},
                {"id":4,"feed_type":"Complément minéral","quantity_kg":80,"min_stock_kg":20,"origin":"Importé","purchase_date":"2024-02-10","supplier":"VetCo","cost_per_kg_da":300,"transport_cost_da":800,"notes":"Bovins"},
                {"id":5,"feed_type":"Son de blé","quantity_kg":60,"min_stock_kg":50,"origin":"Local","purchase_date":"2024-03-01","supplier":"Moulin local","cost_per_kg_da":30,"transport_cost_da":500,"notes":""},
            ])
        if not os.path.exists(FEEDING_LOG_FILE): _save(FEEDING_LOG_FILE,[])

    def get_inventory(self,origin=None,feed_type=None):
        r=self.inventory
        if origin:    r=[f for f in r if f["origin"]==origin]
        if feed_type: r=[f for f in r if f["feed_type"]==feed_type]
        return r

    def add_stock(self,d):
        item={"id":_nid(self.inventory),"feed_type":d.get("feed_type","Autre"),
              "quantity_kg":float(d.get("quantity_kg",0)),"min_stock_kg":float(d.get("min_stock_kg",50)),
              "origin":d.get("origin","Local"),"purchase_date":d.get("purchase_date",_today()),
              "supplier":d.get("supplier",""),"cost_per_kg_da":float(d.get("cost_per_kg_da",0)),
              "transport_cost_da":float(d.get("transport_cost_da",0)),"notes":d.get("notes","")}
        self.inventory.append(item); _save(FEEDS_FILE,self.inventory); return item

    def update_stock(self,fid,d):
        for f in self.inventory:
            if f["id"]==fid:
                for k in ["feed_type","quantity_kg","min_stock_kg","origin","purchase_date",
                           "supplier","cost_per_kg_da","transport_cost_da","notes"]:
                    if k in d: f[k]=float(d[k]) if isinstance(f[k],float) else d[k]
                _save(FEEDS_FILE,self.inventory); return {"success":True,"item":f}
        return {"success":False}

    def delete_stock(self,fid):
        before=len(self.inventory)
        self.inventory=[f for f in self.inventory if f["id"]!=fid]
        if len(self.inventory)<before: _save(FEEDS_FILE,self.inventory); return {"success":True}
        return {"success":False,"message":"Not found"}

    def log_feeding(self,d):
        qty=float(d.get("quantity_kg",0))
        entry={"id":_nid(self.feeding_log),"date":d.get("date",_today()),
               "feed_type":d.get("feed_type",""),"quantity_kg":qty,
               "animal_type":d.get("animal_type","All"),"notes":d.get("notes","")}
        for f in self.inventory:
            if f["feed_type"]==entry["feed_type"]:
                f["quantity_kg"]=max(0,f["quantity_kg"]-qty)
        self.feeding_log.append(entry)
        _save(FEEDING_LOG_FILE,self.feeding_log); _save(FEEDS_FILE,self.inventory)
        return entry

    def get_feeding_log(self):
        return sorted(self.feeding_log,key=lambda x:x["date"],reverse=True)

    def low_stock_alerts(self):
        return [f for f in self.inventory if f["quantity_kg"]<=f["min_stock_kg"]]

    def total_stock_value_da(self):
        return round(sum(f["quantity_kg"]*f["cost_per_kg_da"]+f["transport_cost_da"] for f in self.inventory),2)

    def stock_by_type(self):
        c=defaultdict(float)
        for f in self.inventory: c[f["feed_type"]]+=f["quantity_kg"]
        return {"labels":list(c.keys()),"values":[round(v,1) for v in c.values()]}

    def stock_by_origin(self):
        c=defaultdict(float)
        for f in self.inventory: c[f["origin"]]+=f["quantity_kg"]
        return {"labels":list(c.keys()),"values":[round(v,1) for v in c.values()]}

    def export_csv(self):
        buf=io.StringIO()
        if not self.inventory: return ""
        w=csv.DictWriter(buf,fieldnames=self.inventory[0].keys()); w.writeheader(); w.writerows(self.inventory)
        return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# 3 · HealthManager
# ═══════════════════════════════════════════════════════════════════════════
class HealthManager:
    def __init__(self):
        self._seed()
        self.records=_load(HEALTH_REC_FILE)
        self.medicines=_load(MEDICINES_FILE)

    def _seed(self):
        if not os.path.exists(HEALTH_REC_FILE):
            _save(HEALTH_REC_FILE,[
                {"id":1,"animal_id":1,"animal_name":"Nour","animal_type":"Cattle","record_type":"vaccination","disease":"Vaccin FMDV","treatment":"Vaccination annuelle","vet_name":"Dr. Ahmed","date":"2024-01-20","cost_da":3000,"notes":"","resolved":True},
                {"id":2,"animal_id":3,"animal_name":"Layla","animal_type":"Sheep","record_type":"disease","disease":"Pneumonie","treatment":"Antibiotiques 5j","vet_name":"Dr. Ahmed","date":"2024-02-14","cost_da":7200,"notes":"Guérie","resolved":True},
                {"id":3,"animal_id":6,"animal_name":"Zéphyr","animal_type":"Goat","record_type":"checkup","disease":"","treatment":"Contrôle de routine","vet_name":"Dr. Sara","date":"2024-03-01","cost_da":1800,"notes":"Saine","resolved":True},
            ])
        if not os.path.exists(MEDICINES_FILE):
            _save(MEDICINES_FILE,[
                {"id":1,"name":"Pénicilline G","category":"antibiotic","quantity":50,"min_quantity":10,"unit":"ampoules","expiry_date":"2025-06-01","supplier":"VetCo","cost_per_unit_da":420},
                {"id":2,"name":"Vaccin FMDV","category":"vaccine","quantity":4,"min_quantity":5,"unit":"doses","expiry_date":"2024-12-01","supplier":"AgriPharm","cost_per_unit_da":1440},
                {"id":3,"name":"Ivermectine","category":"antiparasitic","quantity":30,"min_quantity":8,"unit":"ml","expiry_date":"2025-03-15","supplier":"VetCo","cost_per_unit_da":600},
                {"id":4,"name":"Oxytétracycline","category":"antibiotic","quantity":40,"min_quantity":10,"unit":"ampoules","expiry_date":"2025-09-01","supplier":"AgriPharm","cost_per_unit_da":480},
            ])

    def get_records(self,record_type=None,resolved=None,animal_type=None):
        r=sorted(self.records,key=lambda x:x["date"],reverse=True)
        if record_type: r=[x for x in r if x["record_type"]==record_type]
        if resolved is not None: r=[x for x in r if x["resolved"]==resolved]
        if animal_type: r=[x for x in r if x["animal_type"]==animal_type]
        return r

    def add_record(self,d):
        rec={"id":_nid(self.records),"animal_id":int(d.get("animal_id",0)),
             "animal_name":d.get("animal_name",""),"animal_type":d.get("animal_type",""),
             "record_type":d.get("record_type","checkup"),"disease":d.get("disease",""),
             "treatment":d.get("treatment",""),"vet_name":d.get("vet_name",""),
             "date":d.get("date",_today()),"cost_da":float(d.get("cost_da",0)),
             "notes":d.get("notes",""),"resolved":bool(d.get("resolved",False))}
        self.records.append(rec); _save(HEALTH_REC_FILE,self.records); return rec

    def update_record(self,rid,d):
        for r in self.records:
            if r["id"]==rid:
                for k,v in d.items():
                    if k=="id": continue
                    if k=="cost_da": r[k]=float(v)
                    elif k=="animal_id": r[k]=int(v)
                    elif k=="resolved": r[k]=bool(v)
                    else: r[k]=v
                _save(HEALTH_REC_FILE,self.records); return {"success":True,"record":r}
        return {"success":False}

    def delete_record(self,rid):
        before=len(self.records)
        self.records=[r for r in self.records if r["id"]!=rid]
        if len(self.records)<before: _save(HEALTH_REC_FILE,self.records); return {"success":True}
        return {"success":False}

    def get_medicines(self): return self.medicines

    def add_medicine(self,d):
        med={"id":_nid(self.medicines),"name":d.get("name",""),
             "category":d.get("category","other"),"quantity":int(d.get("quantity",0)),
             "min_quantity":int(d.get("min_quantity",5)),"unit":d.get("unit","unités"),
             "expiry_date":d.get("expiry_date",""),"supplier":d.get("supplier",""),
             "cost_per_unit_da":float(d.get("cost_per_unit_da",0))}
        self.medicines.append(med); _save(MEDICINES_FILE,self.medicines); return med

    def update_medicine(self,mid,d):
        for m in self.medicines:
            if m["id"]==mid:
                for k,v in d.items():
                    if k=="id": continue
                    if k in ["quantity","min_quantity"]: m[k]=int(v)
                    elif k=="cost_per_unit_da": m[k]=float(v)
                    else: m[k]=v
                _save(MEDICINES_FILE,self.medicines); return {"success":True,"medicine":m}
        return {"success":False}

    def delete_medicine(self,mid):
        before=len(self.medicines)
        self.medicines=[m for m in self.medicines if m["id"]!=mid]
        if len(self.medicines)<before: _save(MEDICINES_FILE,self.medicines); return {"success":True}
        return {"success":False}

    def expiring_soon(self,days=90):
        return [m for m in self.medicines if _days_until(m.get("expiry_date",""))<=days]

    def low_stock_medicines(self):
        return [m for m in self.medicines if m["quantity"]<=m["min_quantity"]]

    def ongoing_cases(self):
        return [r for r in self.records if not r["resolved"]]

    def records_by_type(self):
        c=defaultdict(int)
        for r in self.records: c[r["record_type"]]+=1
        return {"labels":list(c.keys()),"values":list(c.values())}

    def monthly_health_cost(self):
        c=defaultdict(float)
        for r in self.records: c[r["date"][:7]]+=r["cost_da"]
        months=sorted(c)[-12:]
        return {"months":months,"values":[round(c[m],2) for m in months]}

    def total_health_cost_da(self):
        return round(sum(r["cost_da"] for r in self.records),2)


# ═══════════════════════════════════════════════════════════════════════════
# 4 · CropManager
# ═══════════════════════════════════════════════════════════════════════════
class CropManager:
    STATUSES=["Planté","En croissance","Récolté","Échoué"]

    def __init__(self):
        self._seed(); self.data=_load(CROPS_FILE)

    def _seed(self):
        if os.path.exists(CROPS_FILE): return
        _save(CROPS_FILE,[
            {"id":1,"name":"Blé dur","variety":"Bidi 17","area_ha":10.5,"planted_date":"2023-10-01","expected_harvest_date":"2024-06-15","actual_harvest_date":"2024-06-20","yield_ton":35.0,"status":"Récolté","irrigation_mm":450,"seed_cost_da":42000,"fertilizer_cost_da":28000,"transport_cost_da":8000,"sale_price_da_per_ton":5200,"notes":"Bonne récolte"},
            {"id":2,"name":"Maïs","variety":"Hybride","area_ha":8.0,"planted_date":"2024-04-01","expected_harvest_date":"2024-09-01","actual_harvest_date":"","yield_ton":0,"status":"En croissance","irrigation_mm":600,"seed_cost_da":32000,"fertilizer_cost_da":22000,"transport_cost_da":0,"sale_price_da_per_ton":4800,"notes":""},
            {"id":3,"name":"Tomates","variety":"Heinz","area_ha":3.5,"planted_date":"2024-03-15","expected_harvest_date":"2024-08-01","actual_harvest_date":"","yield_ton":0,"status":"En croissance","irrigation_mm":380,"seed_cost_da":18000,"fertilizer_cost_da":15000,"transport_cost_da":0,"sale_price_da_per_ton":8000,"notes":""},
            {"id":4,"name":"Orge","variety":"Saida","area_ha":7.5,"planted_date":"2023-09-15","expected_harvest_date":"2024-06-30","actual_harvest_date":"2024-07-02","yield_ton":28.5,"status":"Récolté","irrigation_mm":400,"seed_cost_da":30000,"fertilizer_cost_da":20000,"transport_cost_da":6500,"sale_price_da_per_ton":4500,"notes":""},
            {"id":5,"name":"Tournesol","variety":"Helianthus","area_ha":5.0,"planted_date":"2024-04-20","expected_harvest_date":"2024-09-15","actual_harvest_date":"","yield_ton":0,"status":"Planté","irrigation_mm":350,"seed_cost_da":20000,"fertilizer_cost_da":12000,"transport_cost_da":0,"sale_price_da_per_ton":6500,"notes":""},
        ])

    def get_all(self,status=None,search=None):
        r=self.data
        if status: r=[c for c in r if c["status"]==status]
        if search:
            s=search.lower()
            r=[c for c in r if s in c["name"].lower() or s in c["variety"].lower()]
        return r

    def add(self,d):
        crop={"id":_nid(self.data),"name":d.get("name",""),"variety":d.get("variety",""),
              "area_ha":float(d.get("area_ha",0)),"planted_date":d.get("planted_date",_today()),
              "expected_harvest_date":d.get("expected_harvest_date",""),
              "actual_harvest_date":d.get("actual_harvest_date",""),
              "yield_ton":float(d.get("yield_ton",0)),"status":d.get("status","Planté"),
              "irrigation_mm":float(d.get("irrigation_mm",0)),
              "seed_cost_da":float(d.get("seed_cost_da",0)),
              "fertilizer_cost_da":float(d.get("fertilizer_cost_da",0)),
              "transport_cost_da":float(d.get("transport_cost_da",0)),
              "sale_price_da_per_ton":float(d.get("sale_price_da_per_ton",0)),
              "notes":d.get("notes","")}
        self.data.append(crop); _save(CROPS_FILE,self.data); return crop

    def update(self,cid,d):
        for c in self.data:
            if c["id"]==cid:
                float_keys={"area_ha","yield_ton","irrigation_mm","seed_cost_da","fertilizer_cost_da","transport_cost_da","sale_price_da_per_ton"}
                for k,v in d.items():
                    if k=="id": continue
                    c[k]=float(v) if k in float_keys else v
                _save(CROPS_FILE,self.data); return {"success":True,"crop":c}
        return {"success":False}

    def delete(self,cid):
        before=len(self.data)
        self.data=[c for c in self.data if c["id"]!=cid]
        if len(self.data)<before: _save(CROPS_FILE,self.data); return {"success":True}
        return {"success":False}

    def yield_per_ha(self):
        h=[c for c in self.data if c["status"]=="Récolté" and c["area_ha"]>0]
        return {"labels":[c["name"] for c in h],"values":[round(c["yield_ton"]/c["area_ha"],2) for c in h]}

    def total_revenue_da(self):
        return round(sum(c["yield_ton"]*c["sale_price_da_per_ton"] for c in self.data if c["status"]=="Récolté"),2)

    def total_costs_da(self):
        return round(sum(c["seed_cost_da"]+c["fertilizer_cost_da"]+c["transport_cost_da"] for c in self.data),2)

    def profit_by_crop(self):
        h=[c for c in self.data if c["status"]=="Récolté"]
        return {"labels":[c["name"] for c in h],
                "values":[round(c["yield_ton"]*c["sale_price_da_per_ton"]-c["seed_cost_da"]-c["fertilizer_cost_da"]-c["transport_cost_da"],2) for c in h]}

    def area_by_status(self):
        c=defaultdict(float)
        for crop in self.data: c[crop["status"]]+=crop["area_ha"]
        return {"labels":list(c.keys()),"values":[round(v,2) for v in c.values()]}

    def export_csv(self):
        buf=io.StringIO()
        if not self.data: return ""
        w=csv.DictWriter(buf,fieldnames=self.data[0].keys()); w.writeheader(); w.writerows(self.data)
        return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# 5 · ProductionManager
# ═══════════════════════════════════════════════════════════════════════════
class ProductionManager:
    PRODUCTS={"milk":{"unit":"L","icon":"🥛"},"eggs":{"unit":"pièces","icon":"🥚"},
              "wool":{"unit":"kg","icon":"🧶"},"honey":{"unit":"kg","icon":"🍯"},"meat":{"unit":"kg","icon":"🥩"}}

    def __init__(self):
        self._seed(); self.data=_load(PRODUCTION_FILE)

    def _seed(self):
        if os.path.exists(PRODUCTION_FILE): return
        import random; random.seed(42)
        seed=[]; pid=1
        for i in range(60):
            m="03" if i<31 else "04"; d=f"2024-{m}-{(i%28)+1:02d}"
            seed.append({"id":pid,"date":d,"product_type":"milk","quantity":round(random.uniform(40,70),1),"unit":"L","animal_type":"Cattle","animal_name":"Nour","price_per_unit_da":96,"notes":""}); pid+=1
            seed.append({"id":pid,"date":d,"product_type":"eggs","quantity":random.randint(18,35),"unit":"pièces","animal_type":"Poultry","animal_name":"Nadia","price_per_unit_da":30,"notes":""}); pid+=1
        for i in range(3):
            seed.append({"id":pid,"date":f"2024-04-{10+i*5:02d}","product_type":"wool","quantity":round(random.uniform(2,4),1),"unit":"kg","animal_type":"Sheep","animal_name":"Layla","price_per_unit_da":1800,"notes":"Tonte"}); pid+=1
        _save(PRODUCTION_FILE,seed)

    def get_all(self,product_type=None,animal_type=None):
        r=sorted(self.data,key=lambda x:x["date"],reverse=True)
        if product_type: r=[x for x in r if x["product_type"]==product_type]
        if animal_type:  r=[x for x in r if x["animal_type"]==animal_type]
        return r

    def add_record(self,d):
        pt=d.get("product_type","milk")
        rec={"id":_nid(self.data),"date":d.get("date",_today()),"product_type":pt,
             "quantity":float(d.get("quantity",0)),"unit":self.PRODUCTS.get(pt,{}).get("unit","unit"),
             "animal_type":d.get("animal_type",""),"animal_name":d.get("animal_name",""),
             "price_per_unit_da":float(d.get("price_per_unit_da",0)),"notes":d.get("notes","")}
        self.data.append(rec); _save(PRODUCTION_FILE,self.data); return rec

    def update_record(self,rid,d):
        for r in self.data:
            if r["id"]==rid:
                for k,v in d.items():
                    if k=="id": continue
                    r[k]=float(v) if k in {"quantity","price_per_unit_da"} else v
                _save(PRODUCTION_FILE,self.data); return {"success":True,"record":r}
        return {"success":False}

    def delete_record(self,rid):
        before=len(self.data)
        self.data=[r for r in self.data if r["id"]!=rid]
        if len(self.data)<before: _save(PRODUCTION_FILE,self.data); return {"success":True}
        return {"success":False}

    def daily_milk(self):
        t=defaultdict(float)
        for r in self.data:
            if r["product_type"]=="milk": t[r["date"]]+=r["quantity"]
        days=sorted(t)[-30:]
        return {"dates":days,"values":[round(t[d],1) for d in days]}

    def revenue_by_product(self):
        t=defaultdict(float)
        for r in self.data: t[r["product_type"]]+=r["quantity"]*r["price_per_unit_da"]
        return {"labels":list(t.keys()),"values":[round(v,2) for v in t.values()]}

    def total_revenue_da(self):
        return round(sum(r["quantity"]*r["price_per_unit_da"] for r in self.data),2)

    def export_csv(self):
        buf=io.StringIO()
        if not self.data: return ""
        w=csv.DictWriter(buf,fieldnames=self.data[0].keys()); w.writeheader(); w.writerows(self.data)
        return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# 6 · ExpenseManager
# ═══════════════════════════════════════════════════════════════════════════
class ExpenseManager:
    CATEGORIES={
        "feed":"🌾 Alimentation","veterinary":"💊 Vétérinaire","transport":"🚛 Transport",
        "salaries":"👷 Salaires","equipment":"🚜 Équipement",
        "seeds_fertilizers":"🌱 Semences & Engrais","irrigation":"💧 Irrigation",
        "maintenance":"🔧 Maintenance","other":"📦 Autre"
    }

    def __init__(self):
        self._seed(); self.data=_load(EXPENSES_FILE)

    def _seed(self):
        if os.path.exists(EXPENSES_FILE): return
        _save(EXPENSES_FILE,[
            {"id":1,"date":"2024-01-10","category":"feed","sub_category":"Orge","description":"Achat orge 500kg","amount_da":27000,"payment_method":"espèces","reference":"","notes":""},
            {"id":2,"date":"2024-01-15","category":"transport","sub_category":"Livraison aliments","description":"Transport foin Béchar","amount_da":2000,"payment_method":"espèces","reference":"","notes":""},
            {"id":3,"date":"2024-01-20","category":"veterinary","sub_category":"Vaccination","description":"Vaccination FMDV bovins","amount_da":3000,"payment_method":"espèces","reference":"","notes":""},
            {"id":4,"date":"2024-02-01","category":"salaries","sub_category":"Ouvrier","description":"Salaire Janvier","amount_da":22000,"payment_method":"virement","reference":"VIR-001","notes":""},
            {"id":5,"date":"2024-02-10","category":"transport","sub_category":"Transport animaux","description":"Transport bétail marché","amount_da":4500,"payment_method":"espèces","reference":"","notes":""},
            {"id":6,"date":"2024-02-15","category":"equipment","sub_category":"Réparation","description":"Réparation tracteur","amount_da":15000,"payment_method":"espèces","reference":"","notes":""},
            {"id":7,"date":"2024-03-01","category":"seeds_fertilizers","sub_category":"Semences","description":"Semences tomates","amount_da":18000,"payment_method":"virement","reference":"BON-045","notes":""},
            {"id":8,"date":"2024-03-10","category":"irrigation","sub_category":"Électricité","description":"Facture électricité pompe","amount_da":8500,"payment_method":"virement","reference":"","notes":""},
            {"id":9,"date":"2024-03-15","category":"maintenance","sub_category":"Infrastructure","description":"Réparation clôture","amount_da":5000,"payment_method":"espèces","reference":"","notes":""},
            {"id":10,"date":"2024-04-01","category":"salaries","sub_category":"Ouvrier","description":"Salaire Mars","amount_da":22000,"payment_method":"virement","reference":"VIR-002","notes":""},
            {"id":11,"date":"2024-04-05","category":"transport","sub_category":"Transport récolte","description":"Transport blé au silo","amount_da":8000,"payment_method":"espèces","reference":"","notes":""},
            {"id":12,"date":"2024-04-10","category":"feed","sub_category":"Aliment composé","description":"Aliment volaille 300kg","amount_da":28800,"payment_method":"espèces","reference":"","notes":""},
        ])

    def get_all(self,category=None,month=None,search=None):
        r=sorted(self.data,key=lambda x:x["date"],reverse=True)
        if category: r=[x for x in r if x["category"]==category]
        if month:    r=[x for x in r if x["date"].startswith(month)]
        if search:
            s=search.lower()
            r=[x for x in r if s in x["description"].lower() or s in x["sub_category"].lower()]
        return r

    def add(self,d):
        exp={"id":_nid(self.data),"date":d.get("date",_today()),
             "category":d.get("category","other"),"sub_category":d.get("sub_category",""),
             "description":d.get("description",""),"amount_da":float(d.get("amount_da",0)),
             "payment_method":d.get("payment_method","espèces"),
             "reference":d.get("reference",""),"notes":d.get("notes","")}
        self.data.append(exp); _save(EXPENSES_FILE,self.data); return exp

    def update(self,eid,d):
        for e in self.data:
            if e["id"]==eid:
                for k,v in d.items():
                    if k=="id": continue
                    e[k]=float(v) if k=="amount_da" else v
                _save(EXPENSES_FILE,self.data); return {"success":True,"expense":e}
        return {"success":False}

    def delete(self,eid):
        before=len(self.data)
        self.data=[e for e in self.data if e["id"]!=eid]
        if len(self.data)<before: _save(EXPENSES_FILE,self.data); return {"success":True}
        return {"success":False}

    def total_da(self): return round(sum(e["amount_da"] for e in self.data),2)

    def by_category(self):
        c=defaultdict(float)
        for e in self.data: c[e["category"]]+=e["amount_da"]
        return {"labels":[self.CATEGORIES.get(k,k) for k in c],"keys":list(c.keys()),"values":[round(v,2) for v in c.values()]}

    def monthly_expenses(self):
        c=defaultdict(float)
        for e in self.data: c[e["date"][:7]]+=e["amount_da"]
        months=sorted(c)[-12:]
        return {"months":months,"values":[round(c[m],2) for m in months]}

    def transport_total_da(self):
        return round(sum(e["amount_da"] for e in self.data if e["category"]=="transport"),2)

    def export_csv(self):
        buf=io.StringIO()
        if not self.data: return ""
        w=csv.DictWriter(buf,fieldnames=self.data[0].keys()); w.writeheader(); w.writerows(self.data)
        return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
# 7 · SalesManager
# ═══════════════════════════════════════════════════════════════════════════
class SalesManager:
    def __init__(self):
        self._seed(); self.data=_load(SALES_FILE)

    def _seed(self):
        if os.path.exists(SALES_FILE): return
        _save(SALES_FILE,[
            {"id":1,"animal_id":5,"animal_name":"Lot poulets","animal_type":"Poultry","breed":"Broiler","transaction_type":"sale","quantity":50,"price_per_head_da":2160,"transport_cost_da":3000,"total_da":111000,"date":"2024-03-15","buyer_seller":"Marché El-Bayadh","notes":""},
            {"id":2,"animal_id":1,"animal_name":"Nour","animal_type":"Cattle","breed":"Holstein","transaction_type":"purchase","quantity":1,"price_per_head_da":144000,"transport_cost_da":3500,"total_da":147500,"date":"2023-01-15","buyer_seller":"Ferme Hassan","notes":""},
            {"id":3,"animal_id":3,"animal_name":"Layla","animal_type":"Sheep","breed":"Ouled Djellal","transaction_type":"sale","quantity":2,"price_per_head_da":42000,"transport_cost_da":1500,"total_da":85500,"date":"2024-02-28","buyer_seller":"Marché local","notes":""},
        ])

    def get_all(self,transaction_type=None):
        r=sorted(self.data,key=lambda x:x["date"],reverse=True)
        if transaction_type: r=[x for x in r if x["transaction_type"]==transaction_type]
        return r

    def add_transaction(self,d):
        qty=float(d.get("quantity",1)); price=float(d.get("price_per_head_da",0)); trans=float(d.get("transport_cost_da",0))
        txn={"id":_nid(self.data),"animal_id":int(d.get("animal_id",0)),
             "animal_name":d.get("animal_name",""),"animal_type":d.get("animal_type",""),
             "breed":d.get("breed",""),"transaction_type":d.get("transaction_type","sale"),
             "quantity":qty,"price_per_head_da":price,"transport_cost_da":trans,
             "total_da":round(qty*price+trans,2),"date":d.get("date",_today()),
             "buyer_seller":d.get("buyer_seller",""),"notes":d.get("notes","")}
        self.data.append(txn); _save(SALES_FILE,self.data); return txn

    def update_transaction(self,tid,d):
        for t in self.data:
            if t["id"]==tid:
                float_keys={"quantity","price_per_head_da","transport_cost_da","total_da"}
                for k,v in d.items():
                    if k=="id": continue
                    t[k]=float(v) if k in float_keys else v
                t["total_da"]=round(t["quantity"]*t["price_per_head_da"]+t["transport_cost_da"],2)
                _save(SALES_FILE,self.data); return {"success":True,"transaction":t}
        return {"success":False}

    def delete_transaction(self,tid):
        before=len(self.data)
        self.data=[t for t in self.data if t["id"]!=tid]
        if len(self.data)<before: _save(SALES_FILE,self.data); return {"success":True}
        return {"success":False}

    def total_income_da(self):
        return round(sum(t["total_da"] for t in self.data if t["transaction_type"]=="sale"),2)

    def total_purchases_da(self):
        return round(sum(t["total_da"] for t in self.data if t["transaction_type"]=="purchase"),2)

    def monthly_sales(self):
        c=defaultdict(float)
        for t in self.data:
            if t["transaction_type"]=="sale": c[t["date"][:7]]+=t["total_da"]
        months=sorted(c)[-12:]
        return {"months":months,"values":[round(c[m],2) for m in months]}


# ═══════════════════════════════════════════════════════════════════════════
# 8 · ReportManager
# ═══════════════════════════════════════════════════════════════════════════
class ReportManager:
    def __init__(self,A,F,H,C,P,E,S):
        self.A=A;self.F=F;self.H=H;self.C=C;self.P=P;self.E=E;self.S=S

    def dashboard_kpis(self):
        return {
            "total_animals":    len(self.A.data),
            "alive":            sum(1 for a in self.A.data if a["status"]=="alive"),
            "sold":             sum(1 for a in self.A.data if a["status"]=="sold"),
            "dead":             sum(1 for a in self.A.data if a["status"]=="dead"),
            "mortality_rate":   self.A.mortality_rate(),
            "feed_stock_da":    self.F.total_stock_value_da(),
            "production_rev_da":self.P.total_revenue_da(),
            "sales_income_da":  self.S.total_income_da(),
            "total_expenses_da":self.E.total_da(),
            "crop_revenue_da":  self.C.total_revenue_da(),
            "active_crops":     sum(1 for c in self.C.data if c["status"] in ["Planté","En croissance"]),
            "total_area_ha":    round(sum(c["area_ha"] for c in self.C.data),1),
            "transport_total_da":self.E.transport_total_da(),
        }

    def all_alerts(self):
        return {
            "low_feed":       self.F.low_stock_alerts(),
            "expiring_meds":  self.H.expiring_soon(90),
            "low_meds":       self.H.low_stock_medicines(),
            "ongoing_health": self.H.ongoing_cases(),
        }

    def total_alerts_count(self):
        a=self.all_alerts()
        return sum(len(v) for v in a.values())

    def profit_loss(self):
        income  =self.P.total_revenue_da()+self.S.total_income_da()+self.C.total_revenue_da()
        expenses=self.E.total_da()+self.S.total_purchases_da()
        return {"production_rev":self.P.total_revenue_da(),"sales_income":self.S.total_income_da(),
                "crop_revenue":self.C.total_revenue_da(),"income":round(income,2),
                "expenses":round(expenses,2),"net":round(income-expenses,2)}

    def monthly_overview(self):
        sales=self.S.monthly_sales(); exp=self.E.monthly_expenses()
        all_months=sorted(set(sales["months"]+exp["months"]))
        sm=dict(zip(sales["months"],sales["values"])); em=dict(zip(exp["months"],exp["values"]))
        return {"months":all_months,"sales":[sm.get(m,0) for m in all_months],"expenses":[em.get(m,0) for m in all_months]}


def create_managers():
    A=AnimalManager(); F=FeedManager(); H=HealthManager()
    C=CropManager();   P=ProductionManager(); E=ExpenseManager(); S=SalesManager()
    R=ReportManager(A,F,H,C,P,E,S)
    return {"animals":A,"feeds":F,"health":H,"crops":C,"production":P,"expenses":E,"sales":S,"report":R}
