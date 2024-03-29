
import os
import json
from time import sleep
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

class AzureHandler:

    def __init__(self, vm_name: str):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        self.credential_param = self.load_credential_param()
        if vm_name not in self.credential_param.keys():
            raise KeyError(f"Can't find Azure VM or account called: {vm_name} in azure_param file")
        self.param_key = vm_name
        self.vm_name = self.credential_param[self.param_key]["vm_name"]
        self.locataion = self.credential_param[self.param_key]["location"]
        self.resource_group_name = self.credential_param[self.param_key]["group_name"]
        self.credential = ClientSecretCredential(tenant_id=self.credential_param[self.param_key]["tenant_id"],
                                                 client_id=self.credential_param[self.param_key]["client_id"],
                                                 client_secret=self.credential_param[self.param_key]["client_secret"])
        self.compute_client = ComputeManagementClient(self.credential, self.credential_param[self.param_key]["subscription_id"])


    def __enter__(self):
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        self.compute_client.close()


    def start_vm(self):
        async_vm_start = self.compute_client.virtual_machines.begin_start(self.resource_group_name, self.vm_name)
        async_vm_start.wait(async_vm_start.done())


    def stop_vm(self):
        async_vm_stop = self.compute_client.virtual_machines.begin_deallocate(self.resource_group_name, self.vm_name)
        async_vm_stop.wait(async_vm_stop.done())


    def reset_vm(self):
        async_vm_restart = self.compute_client.virtual_machines.begin_restart(self.resource_group_name, self.vm_name)
        async_vm_restart.wait(async_vm_restart.done())


    def vm_state(self):
        # vm_r_cmd = self.compute_client.virtual_machines.get(GROUP_NAME, VM_NAME).resources[1]
        return self.compute_client.virtual_machines.get(self.resource_group_name, self.vm_name, expand='instanceView')\
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
        vm_state = self.compute_client.virtual_machines.get(self.resource_group_name, self.vm_name, expand='instanceView')\
            .instance_view.statuses[1].display_status

        return vm_state == "VM running"
            

    def close(self):
        exit()


def main():
    # main func for functinality testing.
    with AzureHandler("gns") as vm: 
        vm.stop_vm()
        sleep(5)
        print(f"{vm.vm_state()}")
        vm.reset_vm()
        print(f"{vm.vm_state()}")



if __name__ == '__main__':
    main()
