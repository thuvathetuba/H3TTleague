from typing import Final
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from database import add_player, get_leaderboard, update_score

TOKEN = "7674380569:AAGuyJeH-ZwCLrQaqIGBrl8T9mZQpL0idw8"
BOT_USERNAME: Final = "@H3TTbot"
DB_FILE = "TT.db"

def setup_database(): 
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    

async def start_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I'm the Table Tennis Game Master!.")

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("I am the Game Master for our Table Tennis League !")

async def test_command(update: Update, context: CallbackContext):
    await update.message.reply_text("TEST")

async def add_player_command(update: Update, context: CallbackContext): 
    if len(context.args) < 1: 
        await update.message.reply_text("Usage: /add_player <name>")
        return
    
    player_name = ' '.join(context.args)
    add_player(player_name)
    await update.message.reply_text(f"Player '{player_name}' added!")

import sqlite3

DB_FILE = 'TT.db'

def setup_database(): 
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS table_tennis_league (
            name TEXT UNIQUE NOT NULL PRIMARY KEY,
            wins INTEGER DEFAULT 0 NOT NULL,
            loss INTEGER DEFAULT 0 NOT NULL,
            sets_won INTEGER DEFAULT 0 NOT NULL,
            sets_loss INTEGER DEFAULT 0 NOT NULL,
            set_difference INTEGER DEFAULT 0 NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def add_player(name): 
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try: 
        cursor.execute("INSERT INTO table_tennis_league (name) VALUES (?)", (name,))
        conn.commit()
        print(f"Player '{name}' added successfully")
    except sqlite3.IntegrityError: 
        print(f"Player '{name}' already exists")

    conn.close()

def update_score(player1, player2, winner, sets_won_p1, sets_won_p2):
    """Updates scores based on match results."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    sets_loss_p1 = sets_won_p2
    sets_loss_p2 = sets_won_p1
    
    if winner == player1:
        cursor.execute("""
            UPDATE table_tennis_league
            SET wins = wins + 1, sets_won = sets_won + ?, sets_loss = sets_loss + ?, set_difference = set_difference + ?
            WHERE name = ?
        """, (sets_won_p1, sets_loss_p1, sets_won_p1 - sets_loss_p1, player1))
        
        cursor.execute("""
            UPDATE table_tennis_league
            SET loss = loss + 1, sets_won = sets_won + ?, sets_loss = sets_loss + ?, set_difference = set_difference + ?
            WHERE name = ?
        """, (sets_won_p2, sets_loss_p2, sets_won_p2 - sets_loss_p2, player2))
    else:
        cursor.execute("""
            UPDATE table_tennis_league
            SET wins = wins + 1, sets_won = sets_won + ?, sets_loss = sets_loss + ?, set_difference = set_difference + ?
            WHERE name = ?
        """, (sets_won_p2, sets_loss_p2, sets_won_p2 - sets_loss_p2, player2))
        
        cursor.execute("""
            UPDATE table_tennis_league
            SET loss = loss + 1, sets_won = sets_won + ?, sets_loss = sets_loss + ?, set_difference = set_difference + ?
            WHERE name = ?
        """, (sets_won_p1, sets_loss_p1, sets_won_p1 - sets_loss_p1, player1))
    
    conn.commit()
    conn.close()

def get_leaderboard(): 
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT name, wins, loss, sets_won, sets_loss, set_difference FROM table_tennis_league ORDER BY wins DESC, set_difference DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows

async def update_score_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Enter players in format: player1 vs player2")
    response = await context.bot.wait_for_message(update.message.chat_id)
    players = response.text.split(" vs ")
    if len(players) != 2:
        await update.message.reply_text("Invalid format. Use: player1 vs player2")
        return
    player1, player2 = players
    
    await update.message.reply_text(f"Who won? {player1} or {player2}")
    winner_response = await context.bot.wait_for_message(update.message.chat_id)
    winner = winner_response.text.strip()
    if winner not in [player1, player2]:
        await update.message.reply_text("Invalid winner name. Try again.")
        return
    
    await update.message.reply_text("Enter the set score in format: sets_won_by_player1-sets_won_by_player2")
    score_response = await context.bot.wait_for_message(update.message.chat_id)
    try:
        sets_won_p1, sets_won_p2 = map(int, score_response.text.split("-"))
        if sets_won_p1 > 2 or sets_won_p2 > 2:
            await update.message.reply_text("Invalid score. Sets won cannot be more than 2. Try again.")
            return
    except ValueError:
        await update.message.reply_text("Invalid score format. Use: 2-1")
        return
    
    update_score(player1, player2, winner, sets_won_p1, sets_won_p2)
    await update.message.reply_text(f"Updated match result: {player1} vs {player2}, Winner: {winner}, Score: {sets_won_p1}-{sets_won_p2}")

async def leaderboard_command(update: Update, context: CallbackContext):
    leaderboard = get_leaderboard()

    if not leaderboard:
        await update.message.reply_text("No players in the league yet!")
        return

    leaderboard_text = "**🏆 League Leaderboard 🏆**\n"
    for idx, (name, wins, loss, sets_won, sets_loss, set_difference) in enumerate(leaderboard, start=1):
        leaderboard_text += f"{idx}. {name} | Wins: {wins} | Loss: {loss} | Sets Won: {sets_won} | Sets Loss: {sets_loss} | Set Diff: {set_difference}\n"

    await update.message.reply_text(leaderboard_text)


##responses 

def handle_response(text: str) -> str: 
    processed: str = text.lower()

    if 'hello' in text: 
        return 'Hey there!'
    if 'how are you' in text: 
        return 'I am good!'
    return 'I do not understand what you are saying...'

async def handle_message(update: Update, context: CallbackContext): 
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group' : 
        if BOT_USERNAME in text: 
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text) 
        else: 
            return
    else: 
        response: str = handle_response(text) 
    
    print('Bot:', response) 
    await update.message.reply_text(response) 


async def errors(update: Update, context: CallbackContext): 
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__': 
    app = Application.builder().token(TOKEN).build()
    
    ## COMMANDS
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('test', test_command))
    app.add_handler(CommandHandler('add_player', add_player_command))
    app.add_handler(CommandHandler('update_score', update_score_command))
    app.add_handler(CommandHandler('leaderboard', leaderboard_command))

    ## MESSAGES
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


    ## ERRORS
    app.add_error_handler(errors)

    ## Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)