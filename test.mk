.PHONY: \
    test \
    quicktest \
    lint \
    test-unit \
    test-end2end


## Run all tests
test: lint test-unit test-end2end

## Run lint and unit tests
quicktest: lint test-unit

## Lint your code with pep8
lint:
	python setup.py pep8

## Run unit tests
test-unit:
	python setup.py test

## Run parser on test layouts and terraform plan the output
test-end2end: develop
	for layout in `ls tests/layouts/good/*.yaml`; do \
	    run_id=functest layout=$$(basename $$layout) make plan || exit 1; \
	done
	rm -f parsed.tf.json
	@echo "End to end tests passed"
