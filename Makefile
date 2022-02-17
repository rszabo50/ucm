
DIST_DIR =./dist

setup:
	python3 -m pip install --upgrade build twine

build: setup clean
	python3 -m build

deploy-testpypi: build
	python3 -m twine upload --repository testpypi dist/*

deploy: build
	python3 -m twine upload --repository pypi dist/*

.PHONY: clean

clean:
	rm -rf ${DIST_DIR} || true