import sqlite3

DB_FILE = 'TT.db'

def setup_database(): 
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    conn.commit()
    conn.close()

def add_player(name): 
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try: 
        cursor.execute("INSERT INTO table tennis league (name) VALUES (?)", (name,))
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
            GP = GP + 1, SET wins = wins + 1, sets_won = sets_won + ?, sets_loss = sets_loss + ?, set_difference = set_difference + ?
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