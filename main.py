# #!/usr/bin/python

import os
import json
import time

from azurelib import AzureHandler
from telegramlib import TelegramBot
from telegram.ext import Updater, CommandHandler, Filters, CallbackContext, Job

USER_IS_AFK = 1800  # 30 minutes in seconds
SEND_RENEW_REG = 1500  # 25 minutes in seconds
LAST_JOB_RUN = 9999999999  # the last time job should run, needs to be infinite.


def help(update: Updater, context: CallbackContext):
    """help command to explain how the bot works
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to Azure controller.\n"
                                  "Read carefully in order to keep your work safe.\n"
                                  "1. In order to keep the vm running you must register by /reg or /vmstart commands.\n"
                                  "2. Once registered, every 25 minutes the bot will ask you to re-register.\n"
                                  "3. You most responds within 5 minutes, if you \"away form keyboard\" more then 30"
                                  " minutes you will be logged-out.\n"
                                  "4. If no user respond and didn't re-registered them-self's within 30"
                                  " minute period the vm will be shutdown automatically.")


def announce(update: Updater, context: CallbackContext):
    for user in context.bot_data["users"]:
        context.bot.send_message(chat_id=user["user_id"], text=context.arg[1])


def vm_start(update: Updater, context: CallbackContext):
    try:
        vm_name = "default vm name"
        if context.args:
            vm_name = context.args[0]
        with AzureHandler(vm_name) as vm:
            reg_user(update, context)

            if not vm.is_vm_running():
                update.message.reply_text("starting vm")
                print('\nStart VM')
                vm.start_vm()
                update.message.reply_text("start-up completed")
            else:
                update.message.reply_text("VM is already running.")
    except KeyError as e:
        update.message.reply_text(f'Error starting VM: {e}')


def vm_stop(update: Updater, context: CallbackContext):
    try: 
        vm_name = "default vm name"
        if context.args:
            vm_name = context.args[0]
        with AzureHandler(vm_name) as vm:
            update.message.reply_text("shutting down vm")
            print('\nStop VM')
            vm.stop_vm()
            update.message.reply_text("shutdown completed")
    except KeyError as e:
        update.message.reply_text(f'Error stoping VM: {e}')


def vm_stat(update: Updater, context: CallbackContext):
    try:
        vm_name = "default vm name"
        if context.args:
            vm_name = context.args[0]
        with AzureHandler(vm_name) as vm:
            print("stat vm")
            vm_state = vm.vm_state()
            update.message.reply_text(vm_state)
    except KeyError as e:
        update.message.reply_text(f'Error checking VM status: {e}')

def vm_rest(update: Updater, context: CallbackContext):
    try:
        vm_name = "default vm name"
        if context.args:
            vm_name = context.args[0]
        with AzureHandler(vm_name) as vm:
            print('\nRestart VM')
            update.message.reply_text("resetting vm")
            vm.reset_vm()
            update.message.reply_text("vm reboot command sent")
    except KeyError as e:
        update.message.reply_text(f'Error restarting VM: {e}')
    except Exception as e:
        update.message.reply_text(f'{e}')


def reg_user(update, context: CallbackContext):
    """register users base on chat id (in our case same as user id) save to bot_data["users"] any updates"""
    # TODO: improve speed by user login and logged_out dicts instead searching user flags.

    users_dict = context.bot_data["users"]
    
    for username in users_dict.keys():
        if users_dict[username]["user_id"] == update.message.chat_id:
            users_dict[username]["registered"] = True
            users_dict[username]["last_login"] = update_login()
            context.bot.send_message(chat_id=users_dict[username]["user_id"], text="You are now registered")
            print(f"user {username} been registered")
    context.bot_data["users"] = users_dict


def send_rereg_request(context: CallbackContext):
    """Sends to all registered users whom still uses to re-register"""
    for validating_user in context.bot_data["users"].values():
        current_user_log_time = time.time() - validating_user["last_login"]
        # If user is registered, send re-register notification if user "last_log" is higher eq then SEND_RENEW_REG
        if validating_user["registered"] and int(current_user_log_time) >= SEND_RENEW_REG - (5 * 60):
            context.bot.send_message(chat_id=validating_user["user_id"],
                                     text=f"Dear user, please re-register yourself in the next 5 minutes"
                                          f"in order to keep the vm up and running."
                                          f"you are logged for: {int(current_user_log_time) / 60} minutes." 
                                          f"/reg")
        # create shutdown job only if at last one user is
        # Syncing auto stop to re-register.
        context.job_queue.jobs()
    context.job_queue.run_once(callback=automated_stop_vm, when=(60*5), context=Job.context, name="auto_vm_stop")


def automated_stop_vm(context: CallbackContext):
    """Check with all registered users answered in the 5 min period if not log them out,
     if no one answered stopping the vm"""
    count_online_users = 0
    user_dict = context.bot_data["users"]
    with AzureHandler("vm_name") as vm:
        # Span over registered users and checks if need to log them off.
        for username in user_dict.keys():
            if user_dict[username]["registered"]:
                # in case user is away more then AFK parameter then user is flagged logout and send message to user.
                if (time.time() - user_dict[username]["last_login"]) > (USER_IS_AFK - 60):
                    context.bot_data["users"][username]["registered"] = False
                    context.bot.send_message(chat_id=user_dict[username]["user_id"], text="You didn't respond previous\
                                                                                     message you are now logged-off")
                else:
                    count_online_users += 1

        if count_online_users == 0:
            print("automatically shutting down the vm")
            vm.stop_vm()


    # Case all users are logged off the vm can be shutdown and de-allocated.
def update_login():
    return time.time()


def load_json():
    """load json file and returns a dict
    :rtype: dict
    """
    with open(r"allowed_users.json", "r") as allowed_users_file:
        allowed_users_dict = json.load(allowed_users_file)
    return allowed_users_dict


def load_allowed_users():
    """load allowed users and return there telegram user ids
    :return: list user ids
    :rtype: list
    """
    r_user_ids = []
    allowed_users_dict = load_json()

    for user_id in allowed_users_dict.values():
        r_user_ids.append(user_id["user_id"])

    return r_user_ids


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    allowed_user_ids = load_allowed_users()
    tel_bot = TelegramBot()
    tel_bot.dispatcher.bot_data["users"] = load_json()
    #tel_bot.dispatcher.bot_data["azure_handler"] = AzureHandler()
    tel_bot.updater.dispatcher.add_handler(CommandHandler('vmstart', vm_start,
                                                          Filters.user(allowed_user_ids)))
    tel_bot.updater.dispatcher.add_handler(CommandHandler('vmstop', vm_stop,
                                                          Filters.user(allowed_user_ids)))
    tel_bot.updater.dispatcher.add_handler(CommandHandler('vmstat', vm_stat,
                                                          Filters.user(allowed_user_ids)))
    tel_bot.updater.dispatcher.add_handler(CommandHandler('vmreset', vm_rest,
                                                          Filters.user(allowed_user_ids)))
    tel_bot.updater.dispatcher.add_handler(CommandHandler('reg', reg_user,
                                                          Filters.user(allowed_user_ids)))
    tel_bot.updater.dispatcher.add_handler(CommandHandler('help', help,
                                                          Filters.user(allowed_user_ids)))

    tel_bot.updater.job_queue.run_repeating(callback=send_rereg_request, interval=SEND_RENEW_REG, first=SEND_RENEW_REG,
                                            last=LAST_JOB_RUN, context=Job.context, name="send_registering_request")
    tel_bot.updater.job_queue.start()
    tel_bot.updater.start_polling()
    tel_bot.updater.idle()
    tel_bot.updater.job_queue.stop()


if __name__ == '__main__':
    main()

# Press the green button in the gutter to run the script.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
