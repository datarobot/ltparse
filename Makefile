.PHONY: \
    test \
    lint \
    test-unit \
    test-end2end


include terraform.mk
include test.mk

layout ?= complex.yaml

## Install package in develop mode
develop:
	python setup.py develop

## Install it
install:
	python setup.py install

## Build it
build:
	python setup.py sdist

## Parse a layout file to terraform
create-json:
	ltparse tests/layouts/good/$(layout)
	@echo "Layout parsed"
