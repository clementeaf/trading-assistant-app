.PHONY: install build test deploy clean

install:
	pip install -r requirements-lambda.txt

build:
	sam build

test:
	pytest tests/ -v

deploy:
	sam deploy --guided

deploy-prod:
	sam deploy --parameter-overrides Stage=prod EconomicCalendarProvider=tradingeconomics

clean:
	rm -rf .aws-sam/ dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

