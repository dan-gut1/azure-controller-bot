# #!/usr/bin/python
import time

from telegramlib import TelegramBot
from telegram.ext import CommandHandler, Filters, CallbackContext, Job
from azurelib import AzureHandler
import json

# from telegram.ext import Updater, CommandHandler, CallbackContext
USER_IS_AFK = 1800  # 30 minutes in seconds
SEND_RENEW_REG = 1500  # 25 minutes in seconds


def help(update, context):
    """help command to explain how the bot works
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to Azure controller, read carefully in order to keep your work safe.\n"
                                  "1. In order to keep the vm running you must register by /reg or /vmstart commands.\n"
                                  "2. If you registered, every 25 minutes the bot will ask you to re-register.\n"
                                  "3. If you most responds within 5 minutes, if you \"away form keyboard\" more then 30"
                                  " minutes you will be logged-out."
                                  "4. If no user didn't respond and didn't re-registered them-self's within 30"
                                  " minute period the vm will be automatically shutdown.")


def vm_start(update, context):
    vm = context.bot_data["azure_handler"]
    update.message.reply_text("starting vm")
    reg_user(update, context)
    print('\nStart VM')
    vm.start_vm()
    update.message.reply_text("start-up completed")


def vm_stop(update, context):
    vm = context.bot_data["azure_handler"]
    update.message.reply_text("shutting down vm")
    print('\nStop VM')
    vm.stop_vm()
    update.message.reply_text("shutdown completed")


def vm_stat(update, context):
    vm = context.bot_data["azure_handler"]
    print("stat vm")
    vm_state = vm.vm_state()
    update.message.reply_text(vm_state)


def vm_rest(update, context):
    vm = context.bot_data["azure_handler"]
    print('\nRestart VM')
    update.message.reply_text("resetting vm")
    vm.reset_vm()
    update.message.reply_text("vm reboot command sent")


def reg_user(update, context: CallbackContext):
    """register users base on chat id (in our case same as user id) save to bot_data["users"] any updates"""
    # TODO: improve speed by user login and logged_out dicts instead searching user flags.

    users_dict = context.bot_data["users"]

    for username in users_dict.keys():
        if users_dict[username]["user_id"] == update.message.chat_id:
            users_dict[username]["registered"] = True
            users_dict[username]["last_login"] = update_login()
            context.bot.send_message(chat_id=users_dict[username]["user_id"], text="You are now registered")
            print("user %s been registered" % username)
    context.bot_data["users"] = users_dict


def send_rereg_request(context: CallbackContext):
    """Sends to all registered users whom still uses to re-register"""
    print("send re-reg requests")
    for validating_user in context.bot_data["users"].values():
        if validating_user["registered"]:
            context.bot.send_message(chat_id=validating_user["user_id"],
                                     text="Dear user, please re-register yourself in the next 5 minutes"
                                          " in order to keep the vm up and running.\n if you just"
                                          " registered ignore this message.")


def automated_stop_vm(context: CallbackContext):
    """Check with all registered users answered in the 5 min period if not log them out,
     if no one answered stopping the vm"""
    count_online_users = 0
    user_dict = context.bot_data["users"]
    vm = context.bot_data["azure_handler"]

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


def update_login():
    return time.time()


def load_json():
    """load json file and returns a dict
    :rtype: dict
    """
    with open(r"/allowed_users.json", "r") as allowed_users_file:
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
    allowed_user_ids = load_allowed_users()
    tel_bot = TelegramBot()
    tel_bot.dispatcher.bot_data["users"] = load_json()
    tel_bot.dispatcher.bot_data["azure_handler"] = AzureHandler()
    tel_bot.updater.dispatcher.add_handler(CommandHandler('vmstart', vm_start,
                                                          Filters.user(allowed_user_ids)))
    tel_bot.updater.dispatcher.add_handler(CommandHandler('vmstop', vm_stop,
                                                          Filters.user(allowed_user_ids)))
    tel_bot.updater.dispatcher.add_handler(CommandHandler('vmstat', vm_stat,
                                                          Filters.user(allowed_user_ids)))
    tel_bot.updater.dispatcher.add_handler(CommandHandler('reg', reg_user,
                                                          Filters.user(allowed_user_ids)))
    tel_bot.updater.dispatcher.add_handler(CommandHandler('help', help,
                                                          Filters.user(allowed_user_ids)))

    # current_jobs = tel_bot.updater.job_queue.get_jobs_by_name(__name__)
    tel_bot.updater.job_queue.run_repeating(callback=send_rereg_request, interval=SEND_RENEW_REG, first=None,
                                            last=9999999999, context=Job.context, name="send_registering_request")
    tel_bot.updater.job_queue.run_repeating(callback=automated_stop_vm, interval=USER_IS_AFK, first=None,
                                            last=9999999999, context=Job.context, name="auto_vm_stop")
    tel_bot.updater.job_queue.start()
    tel_bot.updater.start_polling()
    tel_bot.updater.idle()
    tel_bot.updater.job_queue.stop()


if __name__ == '__main__':
    main()

# Press the green button in the gutter to run the script.

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
