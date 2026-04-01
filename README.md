# FarmPro – Farm Management System
Team : -BENYAHIA Mousaab -FILALI Hicham -TEDJINI Ahmed -MESSAOUD Imadeeddine-LAMMARI Oussama
## Installation
```bash
pip install flask pytest flake8
python app.py
```
Open http://localhost:5000

## Tests
```bash
pytest tests/ -v
```

## Code Quality
```bash
flake8 farm_manager.py app.py --max-line-length=120
```

## Structure
- `farm_manager.py` — 8 classes, 96 functions, business logic
- `app.py`          — 64 Flask routes (GET/POST/PUT/DELETE)
- `templates/`      — 10 Jinja2 HTML pages
- `tests/`          — 80 pytest tests
- `data/`           — JSON persistence (auto-created)
