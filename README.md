# azure-controller-bot
telegram bot to controll azure vm

Little prefetch
in the ornganization im currently work on\with it takes months to provide premistions to azure resources, 
meanwhile I thougth it will be good practice to develop a python bot who recive vm operation requests and operate the vms by the allowed users.

currenly budget mode is enable by default and checks if users are currently using the vm in order to save monney.

In order to use the bot you need to provide 2 files, 
1. allowed_users.json - in order to filter telegram messages from not authorized users.
2. azure_credential_param.json - which contain all the secrets for azure api.
3. and ofcurse telegram api token.
