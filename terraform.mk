.PHONY: \
    plan \
    get \
    remote-config \
    remote-pull \
    apply \
    destroy \
    plan-destroy \
    help

.DEFAULT_GOAL = help

run_id ?= terraform-1

# Change this bucket to one under your control
remote_state_bucket ?= datarobot-terraform-state

## See what Terraform would do
plan: get remote-pull create-json
	terraform plan -var "run_id=$(run_id)"

remote-config:
	terraform remote config \
	    -backend=s3 \
	    -backend-config="region=us-east-1" \
	    -backend-config="bucket=$(remote_state_bucket)" \
	    -backend-config="key=$(run_id).tfstate" \

remote-pull: remote-config
	terraform remote pull

get: remote-pull
	terraform get

## Apply your terraform configuration
apply: plan get remote-pull
	if ! terraform apply -var "run_id=$(run_id)"; then \
	    terraform remote push; \
	    echo "Apply failed :("; \
	    exit 1; \
	else \
	    terraform remote push; \
	fi

## Destroy all resources managed in the current state
destroy: remote-pull
	if ! terraform destroy -var "run_id=$(run_id)" -force; then \
	    terraform remote push; \
	    echo "Destroy failed :("; \
	    exit 1; \
	else \
	    terraform remote push; \
	fi

## make plan-destroy. Only for supervillains
plan-destroy: remote-pull
	terraform plan -destroy -var "run_id=$(run_id)"

all: help

## Show help screen.
help:
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
                helpMessage = match(lastLine, /^## (.*)/); \
                if (helpMessage) { \
                        helpCommand = substr($$1, 0, index($$1, ":")); \
                        helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
                        printf "%-30s %s\n", helpCommand, helpMessage; \
                } \
        } \
        { lastLine = $$0 }' $(MAKEFILE_LIST)
