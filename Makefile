SHELL := /bin/bash

clean:
	rm -f packaged.yaml
	rm -rf .aws-sam/build

.aws-sam/build: template.yaml sad/app.py
	sam build

packaged.yaml: .aws-sam/build
	sam package \
		--resolve-s3 \
		--output-template-file $@

publish: packaged.yaml
	sam publish --template packaged.yaml
