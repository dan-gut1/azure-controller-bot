import logging
from telegram.ext import Updater, CommandHandler, Filters, CallbackContext, Job

API_TOKEN = "1986898545:AAF3xhgNRkQmziDPmrnLE_gEDDKc0oM-lsU"


class TelegramBot:
    def __init__(self):
        print("init telegrambot")
        #logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.filetrs = Filters
        self.job = Job
        self.updater = Updater(token=API_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('userid', self.get_userid))

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="welcome to validation's azure manager."
                                                                        " type /help for commands")

    def get_userid(self, update, context: CallbackContext):
        update.message.reply_text("You user ID: %d" % update.message.chat_id)


def main():
    # updater = Updater(token=API_TOKEN, use_context=True)
    # dispatcher = updater.dispatcher
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #                    level=logging.INFO)
    # start_handler = CommandHandler('start', self.start)
    # dispatcher.add_handler(start_handler)

    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)

    # caps_handler = CommandHandler('caps', caps)
    # dispatcher.add_handler(caps_handler)
    pass


if __name__ == "__main__":
    main()
