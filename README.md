# Azure Pulumi Project using Azure Key Vault and Pulumi ESC

This project provisions infrastructure on **Azure** using **Pulumi**. It creates a **Resource Group**, **Virtual Network**, **VM**, and uploads secrets from an **Azure Key Vault** to an **ESC environment**. To set up and run the project on your local machine, follow the steps below.

## Prerequisites

Before running the project, make sure you have the following installed on your machine:

- **Pulumi**: [Installation Guide](https://www.pulumi.com/docs/get-started/)
- **Azure CLI**: [Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Python 3.7+**: [Installation Guide](https://www.python.org/downloads/)
- **pip**: [Installation Guide](https://pip.pypa.io/en/stable/installation/)
- Create a Token from Pulumi and export the it with this command `export PULUMI_ACCESS_TOKEN=your_access_token_created_from_pulumi`

Additionally, ensure you have an **Azure subscription** and that you are logged in with the Azure CLI using:

```bash
az login
```

## Setup 

### 1. Clone the repository
First, clone the repository to your local machine:

```bash
git clone https://github.com/ExitoLab/azure_key_vault_pulumi_esc_sdk_example.git
cd azure_key_vault_pulumi_esc_sdk_example
```

## 2. Install Python Dependencies
The project uses some Python dependencies. Install them by running the following command:

```bash
pip install -r requirements.txt
```

You can also use python virtual environments 
```bash
python3 -m venv path/to/venv
source path/to/venv/bin/activate
python3 -m pip install -r requirements.txt 
```

## 3. Azure Key Vault Setup
Make sure you have an Azure Key Vault in your Azure environment within the same Resource Group. The secrets will be stored in the Key Vault, and they will be retrieved to set up the VM during infrastructure provisioning.

Create the following secrets in your Key Vault:

- adminUsername
- adminPassword

You can create secrets in Azure Key Vault using the Azure CLI or Azure Portal.

To create secrets via Azure CLI:

```bash
az keyvault secret set --vault-name demo-key-vault-pulumi --name "adminUsername" --value "<your_admin_username>"
az keyvault secret set --vault-name demo-key-vault-pulumi --name "adminPassword" --value "<your_admin_password>"
```

## 4. Configuration
The Config class is used to retrieve the required configuration values. These values must be provided in the pulumi.Config() object. You can set them either via environment variables or in the Pulumi.<stack_name>.yaml file.

The following configuration variables are required:

- `location`: Azure location where resources will be provisioned (e.g., eastus).
- `key_vault_name`: Name of the Azure Key Vault containing your secrets.
- `subscription_id`: Your Azure subscription ID.
- `resource_group_name`: Name of the resource group.
- `vm_publisher`, `vm_offer`, `vm_sku`, `vm_version`: Details of the virtual machine.
- `vm_name`: Name of the virtual machine.
- `org_name`: Organization name for ESC environment.

## 5. Set Up Azure Login
To ensure the Pulumi project can interact with your Azure subscription, make sure you are logged into your Azure account using the Azure CLI:

```bash
az login
```
This will authenticate your local machine with your Azure account.

## 6. Running the Pulumi Project
Once the prerequisites are met and the configuration is set, you can run the Pulumi project with the following command:

```
pulumi up
```

This will spin up the infrastructure, which includes:

- A Resource Group in Azure.
- A Virtual Network and Subnet.
- A Public IP Address and a Network Interface for the VM.
- A Linux Virtual Machine.
- Secrets pulled from Azure Key Vault and updated in the ESC environment.

Follow the prompts to confirm and complete the deployment.

## 7. Verify the Deployment
Once the deployment is complete, you should see the following outputs:

- `Resource Group Name`: The name of the Azure Resource Group created.
- `VM Name`: The name of the virtual machine.
- `VM IP Address`: The public IP address of the virtual machine.
- You can verify the creation of resources in the Azure Portal or by using the Azure CLI.