# azure-controller-bot
Telegram bot to controll azure vm


Preface

In the organization IM currently work on \ with it takes months to provide perissions to azure resources, 
meanwhile I thought it will be good practice to develop a Telegram bot who recieve vm operation requests and operate the vms by the allowed users.

Currenly budget mode is enable by default and checks if users are currently using the vm in order to save money.


In order to use the bot you need to provide 2 files and token, 
1. allowed_users.json - in order to filter telegram messages from not authorized users.
2. azure_credential_param.json - which contain all the secrets for azure api.
3. and ofcurse telegram API token, and set it in telegramlib.
