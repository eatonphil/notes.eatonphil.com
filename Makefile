.PHONY: docs

docs:
	rm -rf docs && mkdir -p docs
	echo "notes.eatonphil.com" > docs/CNAME
	python3 -m venv .env
	.env/bin/pip install mistune feedgen
	.env/bin/python ./scripts/build.py
