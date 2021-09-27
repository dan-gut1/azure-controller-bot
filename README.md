# azure-controller-bot
Telegram bot to controll azure vm


Preface

In the organization IM currently work on \ with it takes months to provide permissions to azure resources, 
meanwhile I thought it will be good practice to develop a Telegram bot who recieve vm operation requests and operate the vms by the allowed users.

Currenly budget mode is enable by default and checks if users are currently using the vm in order to save money.

Configurations.
In order to use the bot you need to provide 2 files and token, 
1. allowed_users.json - in order to filter telegram messages from not authorized users.
2. azure_credential_param.json - which contain all the secrets for azure api.
3. and ofcurse telegram API token, and set it in telegramlib.

set the bot up.
1. boot up a small vm or any thing that can run pythons.
2. run: pip install -r requirements.txt
3. recommended: set the main.py as system service that startup on boot.
4. congratulations: you on the budget now.
