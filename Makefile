PORT ?= auto

# --- Development: mount src/ so imports resolve without deploying ---
run:
	mpremote mount src/ run src/main.py

# --- Deploy all src/ files to device, then run ---
deploy:
	mpremote fs mkdir :/drivers 2>/dev/null || true
	mpremote fs mkdir :/drivers/display 2>/dev/null || true
	mpremote fs cp src/main.py             :/main.py
	mpremote fs cp src/webpage.py          :/webpage.py
	mpremote fs cp src/statehandler.py     :/statehandler.py
	mpremote fs cp src/drivers/display/robot_face.py :/drivers/display/robot_face.py

run-deployed:
	mpremote run src/main.py

.PHONY: run deploy run-deployed
