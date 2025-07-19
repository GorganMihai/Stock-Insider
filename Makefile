VENV_DIR := MyVrEnv
PYTHON := $(VENV_DIR)/Scripts/python.exe
APP_NAME := main.py
TEST := test.py
LAMBDA_FUNCTION_NAME := add_stocks_history

install:
	python -m venv $(VENV_DIR)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(APP_NAME)

test:
	$(PYTHON) $(TEST)

terraform-init:
	cd Terraform && terraform init

terraform-plan:
	cd Terraform && terraform plan

terraform-apply:
	cd Terraform && terraform apply -auto-approve

terraform-destroy:
	cd Terraform && terraform destroy -auto-approve

clean:
	if exist $(VENV_DIR) rmdir /s /q $(VENV_DIR)

lambda-update:
	cd lambda_package && \
	powershell -Command "Remove-Item -Force lambda_function.zip -ErrorAction SilentlyContinue" && \
	powershell -Command "Compress-Archive -Path lambda_function.py -DestinationPath lambda_function.zip -Force" && \
	aws lambda update-function-code --function-name $(LAMBDA_FUNCTION_NAME) --zip-file fileb://lambda_function.zip --region eu-west-1 --output text --query 'FunctionName' && \
	@echo Lambda function $(LAMBDA_FUNCTION_NAME) updated successfully!

.PHONY: install run test clean terraform-init terraform-plan terraform-apply terraform-destroy lambda-update
