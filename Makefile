# Detect operating system
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
else
    DETECTED_OS := $(shell uname -s)
endif

VENV_DIR := MyVrEnv
APP_NAME := main.py
TEST := test.py
LAMBDA_FUNCTION_NAME := add_stocks_history

# Set paths based on operating system
ifeq ($(DETECTED_OS),Windows)
    PYTHON := $(VENV_DIR)/Scripts/python.exe
    PIP := $(VENV_DIR)/Scripts/pip.exe
    PYTHON_CMD := python
    RM_CMD := if exist $(VENV_DIR) rmdir /s /q $(VENV_DIR)
    ZIP_CMD := powershell -Command "Remove-Item -Force lambda_function.zip -ErrorAction SilentlyContinue" && powershell -Command "Compress-Archive -Path lambda_function.py -DestinationPath lambda_function.zip -Force"
else
    PYTHON := $(VENV_DIR)/bin/python
    PIP := $(VENV_DIR)/bin/pip
    PYTHON_CMD := python3
    RM_CMD := rm -rf $(VENV_DIR)
    ZIP_CMD := rm -f lambda_function.zip && zip lambda_function.zip lambda_function.py
endif

install:
	$(PYTHON_CMD) -m venv $(VENV_DIR)
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
	$(RM_CMD)

lambda-update:
	cd lambda_package && \
	$(ZIP_CMD) && \
	aws lambda update-function-code --function-name $(LAMBDA_FUNCTION_NAME) --zip-file fileb://lambda_function.zip --region eu-west-1 --output text --query 'FunctionName' && \
	echo "Lambda function $(LAMBDA_FUNCTION_NAME) updated successfully!"

.PHONY: install run test clean terraform-init terraform-plan terraform-apply terraform-destroy lambda-update