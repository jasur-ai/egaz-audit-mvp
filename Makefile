.PHONY: install demo train test serve dashboard monitor clean docker

install:
	pip install -r requirements.txt

demo: train dashboard

train:
	python3 scripts/run_all.py

dashboard:
	python3 scripts/build_dashboard.py

test:
	python3 -m pytest -q tests/

monitor:
	python3 scripts/run_monitor.py

serve:
	uvicorn src.api.app:app --host 0.0.0.0 --port 8001

docker:
	docker compose up --build

clean:
	rm -rf data/*.gz models/*.joblib reports/figures/*.png web/dashboard.html
