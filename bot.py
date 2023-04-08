import telegram
from telegram.ext import Updater, CommandHandler

# Replace 'YOUR_BOT_TOKEN' with your own bot token provided by BotFather
API = '5796978790:AAHxviQvn6Q0jU9IqT5_wvjdihqT-oZyYac'

# Define a dictionary to store user balances
balances = {100000000}

# Define the price of a single Googly Token
TOKEN_PRICE = 1

# Define the commission percentage for affiliate referrals
COMMISSION_PERCENTAGE = 10

# Define a dictionary to store user referral links
referral_links = {}

# Define a function to handle the '/buy' command
def buy(update, context):
    # Get the user ID and the amount of tokens they want to buy
    user_id = update.message.from_user.id
    amount = int(context.args[0])

    # Calculate the total price of the tokens
    total_price = amount * TOKEN_PRICE

    # Check if the user has enough funds
    if user_id not in balances or balances[user_id] < total_price:
        context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, you don't have enough funds to buy that many tokens.")
    else:
        # Update the user's balance and send a confirmation message
        balances[user_id] -= total_price
        if user_id not in balances:
            balances[user_id] = total_price
        else:
            balances[user_id] += total_price
        context.bot.send_message(chat_id=update.message.chat_id, text="You bought {} Googly Tokens for {} credits. Your balance is now {} tokens.".format(amount, total_price, balances[user_id] // TOKEN_PRICE))

        # Check if the user has a referrer
        if 'referrer' in context.user_data:
            referrer_id = context.user_data['referrer']
            referrer_balance = balances.get(referrer_id, 0)
            commission = total_price * COMMISSION_PERCENTAGE / 100
            balances[referrer_id] = referrer_balance + commission
            context.bot.send_message(chat_id=referrer_id, text="Your referral earned you {} tokens.".format(commission // TOKEN_PRICE))

# Define a function to handle the '/sell' command
def sell(update, context):
    # Get the user ID and the amount of tokens they want to sell
    user_id = update.message.from_user.id
    amount = int(context.args[0])

    # Check if the user has enough tokens to sell
    if user_id not in balances or balances[user_id] < amount:
        context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, you don't have enough tokens to sell.")
    else:
        # Update the user's balance and send a confirmation message
        balances[user_id] -= amount
        total_price = amount * TOKEN_PRICE
        context.bot.send_message(chat_id=update.message.chat_id, text="You sold {} Googly Tokens for {} credits. Your balance is now {} tokens.".format(amount, total_price, balances[user_id] // TOKEN_PRICE))

# Define a function to handle the '/balance' command
def balance(update, context):
    # Get the user ID and send their balance
    user_id = update.message.from_user.id
    if user_id not in balances:
        context.bot.send_message(chat_id=update.message.chat_id, text="Your balance is 0 Googly Tokens.")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="Your balance is {} Googly Tokens.".format(balances[user_id] // TOKEN_PRICE))

        # Define a function to handle the '/referral' command
        def referral(update, context):
            # Get the user ID and generate their referral link
            user_id = update.message.from_user.id
            if user_id not in referral_links:
                referral_links[user_id] = 'https://t.me/{}?start=ref{}'.format(context.bot.username, user_id)
            context.bot.send_message(chat_id=update.message.chat_id,
                                     text="Your referral link is: {}".format(referral_links[user_id]))

        # Define a function to handle the '/activate' command
        def activate(update, context):
            # Get the user ID and the referral link they want to activate
            user_id = update.message.from_user.id
            referral_link = update.message.text.split()[1]

            # Check if the referral link is valid
            if referral_link.startswith('https://t.me/{}?start=ref'.format(context.bot.username)):
                referrer_id = int(referral_link.split('=')[1][3:])
                if referrer_id != user_id:
                    # Update the user's referral data and send a confirmation message
                    context.user_data['referrer'] = referrer_id
                    context.bot.send_message(chat_id=update.message.chat_id,
                                             text="Your referral link has been activated. Welcome to Googly Tokens!")
                else:
                    context.bot.send_message(chat_id=update.message.chat_id,
                                             text="Sorry, you can't activate your own referral link.")
            else:
                context.bot.send_message(chat_id=update.message.chat_id,
                                         text="Sorry, that's not a valid referral link.")

        # Define a function to handle the '/transfer' command
        def transfer(update, context):
            # Get the user ID, the recipient ID, and the amount of tokens to transfer
            user_id = update.message.from_user.id
            recipient_id = int(context.args[0])
            amount = int(context.args[1])

            # Check if the user has enough tokens to transfer
            if user_id not in balances or balances[user_id] < amount:
                context.bot.send_message(chat_id=update.message.chat_id,
                                         text="Sorry, you don't have enough tokens to transfer.")
            else:
                # Update the balances of both users and send confirmation messages
                balances[user_id] -= amount
                if recipient_id not in balances:
                    balances[recipient_id] = amount
                else:
                    balances[recipient_id] += amount
                context.bot.send_message(chat_id=update.message.chat_id,
                                         text="You transferred {} Googly Tokens to user {}. Your balance is now {} tokens.".format(
                                             amount, recipient_id, balances[user_id] // TOKEN_PRICE))
                context.bot.send_message(chat_id=recipient_id,
                                         text="You received {} Googly Tokens from user {}.".format(amount, user_id))

        # Define a function to handle errors
        def error(update, context):
            print('Error: %s', context.error)

        # Create an instance of the Updater class and pass in the bot token
        updater = Updater(token=BOT_TOKEN, use_context=True)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # Register the command handlers
        dispatcher.add_handler(CommandHandler('buy', buy))
        dispatcher.add_handler(CommandHandler('sell', sell))
        dispatcher.add_handler(CommandHandler('balance', balance))
        dispatcher.add_handler(CommandHandler('referral', referral))
        dispatcher.add_handler(CommandHandler('activate', activate))
        dispatcher.add_handler(CommandHandler('transfer', transfer))

        # Register the error handler
        dispatcher.add_error_handler(error)

        # Start the bot
        updater.start_polling()
