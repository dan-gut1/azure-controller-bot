
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
import json
import os


# Azure Datacenter
LOCATION = 'eastus'

# Resource Group
GROUP_NAME = 'Validation'

# Network
VNET_NAME = 'azure-sample-vnet'
SUBNET_NAME = 'azure-sample-subnet'

# VM
OS_DISK_NAME = 'azure-sample-osdisk'
IP_CONFIG_NAME = 'azure-sample-ip-config'
NIC_NAME = 'azure-sample-nic'
USERNAME = 'userlogin'
PASSWORD = 'Pa$$w0rd91'
VM_NAME = 'gns'


class AzureHandler:

    def __init__(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.credential_param = self.load_credential_param()
        self.credential = ClientSecretCredential(tenant_id=self.credential_param["tenant_id"],
                                                 client_id=self.credential_param["client_id"],
                                                 client_secret=self.credential_param["client_secret"])
        self.compute_client = ComputeManagementClient(self.credential, self.credential_param["subscription_id"])
        self.users = {}

    def __enter__(self):
        self.azure = self.__init__()
        return self.azure

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def start_vm(self):
        async_vm_start = self.compute_client.virtual_machines.begin_start(
            GROUP_NAME, VM_NAME)
        async_vm_start.wait(async_vm_start.done())

    def stop_vm(self):
        async_vm_stop = self.compute_client.virtual_machines.begin_deallocate(
            GROUP_NAME, VM_NAME)
        async_vm_stop.wait(async_vm_stop.done())

    def reset_vm(self):
        async_vm_restart = self.compute_client.virtual_machines.begin_restart(
            GROUP_NAME, VM_NAME)
        async_vm_restart.wait(async_vm_restart.done())

    def vm_state(self):
        # vm_r_cmd = self.compute_client.virtual_machines.get(GROUP_NAME, VM_NAME).resources[1]
        return self.compute_client.virtual_machines.get(GROUP_NAME, VM_NAME, expand='instanceView')\
            .instance_view.statuses[1].display_status

    def load_credential_param(self):
        """in order to hide azure secretes load the secret from a local file"""
        with open(r"./azure_credential_param.json", "r") as credential_file:
            credential_param = json.load(credential_file)

        return credential_param

    def is_vm_running(self):
        """checks if vm is running and retuns True if running else False
        :rtype: bool
        """
        vm_state = self.compute_client.virtual_machines.get(GROUP_NAME, VM_NAME, expand='instanceView')\
            .instance_view.statuses[1].display_status

        if vm_state == "VM running":
            return True
        else:
            return False


def main():
    vm = AzureHandler()
    vm.vm_state()


if __name__ == '__main__':
    main()
