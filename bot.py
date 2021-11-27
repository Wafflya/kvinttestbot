from transitions import Machine
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

SIZES = ["большую", "маленькую"]
PAYMENT_TYPE = ["наличный", "безналичный"]


class BotState(object):
    states = ['start_state', 'ask_payment_type', 'confirm_order', 'end_state']

    def __init__(self):
        self.machine = Machine(model=self, states=BotState.states, initial='start_state')
        self.machine.add_ordered_transitions(states=self.states)
        self.machine.add_transition(trigger='clear', source='*', dest='start_state')



# function to handle the /start command
def start(update, context):
    context.user_data['state'] = BotState()
    first_name = update.message.chat.first_name
    update.message.reply_text(f"Приветствую, {first_name}, приятно познакомиться!")
    start_order(update, context)


def start_order(update, context):
    update.message.reply_text(
        "Какую вы хотите пиццу? Большую или маленькую?")


def recieve_pizza_size(update, context):
    text = update.message.text.lower()
    if (text in SIZES):
        context.user_data['state'].next_state()
        context.user_data['pizza_size'] = text
        update.message.reply_text("Как вы будете платить? (наличный/безналичный)")
    else:
        update.message.reply_text("Некорректно выбран размер!")


def recieve_payment_type(update, context):
    text = update.message.text.lower()
    if (text in PAYMENT_TYPE):
        context.user_data['state'].next_state()
        context.user_data['payment_type'] = text
        update.message.reply_text("Вы хотите {} пиццу, тип оплаты - {} расчёт?".format(context.user_data['pizza_size'],
                                                                                      context.user_data[
                                                                                          'payment_type']))
    else:
        update.message.reply_text("Некорректно выбран тип оплаты! Введите 'наличный' или 'безналичный':")

def recieve_confirmation(update, context):
    text = update.message.text.lower()
    if text == "да":
        update.message.reply_text("Спасибо за заказ!")
        context.user_data['state'].next_state()
    elif text == "нет":
        update.message.reply_text("Заказ сброшен")
        context.user_data['state'].clear()
    else:
        update.message.reply_text("Подвердите или сбросьте заказ ('Да'/'Нет')")


# function to handle the /help command
def help(update, context):
    update.message.reply_text("Введите '/start', чтобы сделать заказ")


# function to handle errors occured in the dispatcher
def error(update, context):
    update.message.reply_text('Непридвиденная ошибка')


# function to handle normal text
def text(update, context):

    if context.user_data['state'].state == "start_state":
        recieve_pizza_size(update, context)
    elif context.user_data['state'].state == "ask_payment_type":
        recieve_payment_type(update, context)
    elif context.user_data['state'].state == "confirm_order":
        recieve_confirmation(update, context)
    elif context.user_data['state'].state == "end_state":
        update.message.reply_text('Если вы хотите снова сделать заказ, введите /start')


def main():
    TOKEN = "2140973984:AAE1gDyhrFYgitFi8UN2W8M6CCiev5_DW_8"
    # create the updater, that will automatically create also a dispatcher and a queue to
    # make them dialoge
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    # add handlers for start and help commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    # add an handler for normal text (not commands)
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    # add an handler for errors
    dispatcher.add_error_handler(error)
    # start your shiny new bot
    updater.start_polling()
    # run the bot until Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
