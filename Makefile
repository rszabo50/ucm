
DIST_DIR =./dist

setup:
	python3 -m pip install --upgrade build twine

build: setup clean
	version=`cat version.txt` && sed -i "s/PROGRAM_VERSION = '0.0.0'/PROGRAM_VERSION = '$$version'/g" src/ucm/constants.py
	python3 -m build

deploy: build
	python3 -m twine upload --repository testpypi dist/*

.PHONY: clean

clean:
	rm -rf ${DIST_DIR} || true