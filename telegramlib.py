from telegram.ext import Updater, CommandHandler
import logging

API_TOKEN = "api_token"


class TelegramBot:
    def __init__(self):
        print("init telegrambot")
        self.updater = Updater(token=API_TOKEN, use_context=True)
        self.dispatcher = self.updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(self.start_handler)

    def start(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="welcome to validation's azure manager."
                                                                        " type /help for commands")


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
