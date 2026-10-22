terraform {
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.0" }
  }
}

provider "azurerm" {
  features {}
}

variable "resource_group_name" {
  default = "genai-support-rg"
}

variable "location" {
  default = "eastus"
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_postgresql_flexible_server" "kb" {
  name                   = "genai-support-kb-db"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "16"
  administrator_login    = "ragadmin"
  administrator_password = var.db_admin_password
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
}

variable "db_admin_password" {
  sensitive = true
}

resource "azurerm_service_plan" "backend" {
  name                = "genai-support-plan"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "backend" {
  name                = "genai-support-backend"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  service_plan_id     = azurerm_service_plan.backend.id

  site_config {
    application_stack {
      docker_image_name = "genai-support-backend:latest"
    }
  }

  app_settings = {
    DATABASE_URL           = "postgresql://ragadmin@${azurerm_postgresql_flexible_server.kb.fqdn}:5432/support_kb"
    AZURE_OPENAI_ENDPOINT  = var.azure_openai_endpoint
  }
}

variable "azure_openai_endpoint" {
  default = ""
}
