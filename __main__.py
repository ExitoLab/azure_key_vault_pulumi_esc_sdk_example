import pulumi
import pulumi_azure_native as azure_native
import pulumi_azure as azure
import pulumi_esc_sdk as esc
import os

from pulumi import Config, export
from pulumi_azure_native.resources import ResourceGroup, get_resource_group

# === Load configuration ===
config = Config()
env = pulumi.get_stack()
appname = pulumi.get_project()
project_name = appname  # for ESC

location = config.require("location")
key_vault_name = config.require("key_vault_name")
subscription_id = config.require("subscription_id")
resource_group_name = config.require("resource_group_name")
vm_publisher = config.require("vm_publisher")
vm_offer = config.require("vm_offer")
vm_sku = config.require("vm_sku")
vm_version = config.require("vm_version")
vm_name = config.require("vm_name")
org_name = config.require("org_name")

# === Set up Pulumi ESC client ===
access_token = os.getenv("PULUMI_ACCESS_TOKEN")
if not access_token:
    raise Exception("PULUMI_ACCESS_TOKEN environment variable is not set.")

esc_env_name = f"{appname}-{env}-secrets"
client = esc.EscClient(esc.Configuration(access_token=access_token))

# === Create or Get Resource Group ===
def create_or_get_rg(name):
    try:
        existing_rg = get_resource_group(resource_group_name=name)
        return ResourceGroup.get("existingResourceGroup", id=existing_rg.id)
    except Exception:
        return ResourceGroup("resourceGroup",
            location=location,
            resource_group_name=name
        )

resource_group = create_or_get_rg(resource_group_name)

# === Create or Update ESC environment ===
env_def = esc.EnvironmentDefinition(
    values=esc.EnvironmentDefinitionValues(
        additional_properties={}  # initialized empty; will update later
    )
)

# Try to create the ESC environment, fallback to update if it exists
try:
    client.create_environment(org_name, project_name, esc_env_name)
    print(f"ESC environment '{esc_env_name}' created.")
except esc.ApiException as e:
    if e.status == 409:
        print(f"ESC environment '{esc_env_name}' already exists. Updating...")
    else:
        raise

# === Get secrets from Azure Key Vault ===
key_vault_id = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.KeyVault/vaults/{key_vault_name}"

admin_username_secret = azure.keyvault.get_secret(name="adminUsername", key_vault_id=key_vault_id)
admin_password_secret = azure.keyvault.get_secret(name="adminPassword", key_vault_id=key_vault_id)

admin_username = admin_username_secret.value
admin_password = admin_password_secret.value

# === Upload secrets to ESC ===
env_def.values.additional_properties = {
    "adminUsername": {"fn::secret": admin_username},
    "adminPassword": {"fn::secret": admin_password},
}

client.update_environment(org_name, project_name, esc_env_name, env_def)

# === Create Networking ===
virtual_network = azure_native.network.VirtualNetwork("virtualNetwork",
    address_space={"addressPrefixes": ["10.0.0.0/16"]},
    location=location,
    resource_group_name=resource_group.name,
    virtual_network_name=f"{appname}-{env}-vn"
)

subnet = azure_native.network.Subnet("subnet",
    address_prefix="10.0.0.0/16",
    resource_group_name=resource_group.name,
    subnet_name=f"{appname}-{env}-sn",
    virtual_network_name=virtual_network.name
)

public_ip = azure_native.network.PublicIPAddress(f"publicIP-{env}",
    resource_group_name=resource_group.name,
    location=location,
    public_ip_allocation_method="Dynamic"
)

network_interface = azure_native.network.NetworkInterface("networkInterface-" + env,
    resource_group_name=resource_group.name,
    location=location,
    ip_configurations=[{
        "name": "ipconfig1",
        "subnet": azure_native.network.SubnetArgs(id=subnet.id),
        "public_ip_address": azure_native.network.PublicIPAddressArgs(id=public_ip.id),
    }]
)

# === Create VM ===
vm = azure.compute.LinuxVirtualMachine(f"{vm_name}-{env}",
    resource_group_name=resource_group.name,
    location=location,
    network_interface_ids=[network_interface.id],
    size="Standard_B1ms",
    disable_password_authentication=False,
    admin_username=admin_username,
    admin_password=admin_password,
    os_disk=azure.compute.LinuxVirtualMachineOsDiskArgs(
        storage_account_type="Standard_LRS",
        caching="ReadWrite",
        disk_size_gb=30,
    ),
    source_image_reference=azure.compute.LinuxVirtualMachineSourceImageReferenceArgs(
        publisher=vm_publisher,
        offer=vm_offer,
        sku=vm_sku,
        version=vm_version,
    ),
    tags={"Environment": env}
)

# === Export Outputs ===
public_ip_address = public_ip.ip_address.apply(lambda ip: ip)  # This resolves the IP address value

export("resource_group_name", resource_group.name)
export("vm_name", vm.name)
export("vm_ip_address", public_ip_address)  # Correct export of IP address
