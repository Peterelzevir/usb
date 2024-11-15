from telethon import TelegramClient, events, Button, sync
import random
import datetime

# Ganti dengan API ID dan API Hash Anda
api_id = '28356794'
api_hash = 'a581331dabc5d4b7e0c7381a97dde824'
client = TelegramClient('userbot_features', api_id, api_hash)

# Data permainan Tic-Tac-Toe dan fitur lainnya
games = {}

def check_winner(board):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Baris
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Kolom
        [0, 4, 8], [2, 4, 6]              # Diagonal
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] and board[combo[0]] != " ":
            return board[combo[0]]
    if " " not in board:
        return "Draw"
    return None

def create_board_buttons(board):
    return [[Button.inline(board[i], f"move_{i}") for i in range(j, j + 3)] for j in range(0, 9, 3)]

def userbot_move(board):
    empty_positions = [i for i, value in enumerate(board) if value == " "]
    if empty_positions:
        return random.choice(empty_positions)
    return None

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond(
        "Selamat datang! Pilih fitur:\n1. Kalkulator\n2. Tic-Tac-Toe\n3. Jam/Pengingat",
        buttons=[
            [Button.inline("Kalkulator", b"calculator"), Button.inline("Tic-Tac-Toe", b"tictactoe")],
            [Button.inline("Jam", b"clock"), Button.inline("Pengingat", b"reminder")]
        ]
    )

@client.on(events.CallbackQuery(pattern=b"tictactoe"))
async def start_tictactoe(event):
    chat_id = event.chat_id
    games[chat_id] = {
        "board": [" "] * 9,
        "turn": "X",
        "player": event.sender_id
    }
    buttons = create_board_buttons(games[chat_id]["board"])
    await event.edit(
        "Permainan Tic-Tac-Toe dimulai!\nGiliran: X (Anda)",
        buttons=buttons
    )

@client.on(events.CallbackQuery(pattern=b"calculator"))
async def calculator_handler(event):
    await event.edit("Masukkan operasi matematika (contoh: `5 + 3`):", parse_mode='markdown')

@client.on(events.NewMessage)
async def message_handler(event):
    if event.text.startswith("/calc"):
        try:
            expression = event.text.split("/calc ")[1]
            result = eval(expression)
            await event.reply(f"Hasil: `{result}`", parse_mode='markdown')
        except Exception as e:
            await event.reply("Terjadi kesalahan dalam perhitungan. Pastikan format benar.")

@client.on(events.CallbackQuery(pattern=b"clock"))
async def clock_handler(event):
    now = datetime.datetime.now()
    time_str = now.strftime("%H:%M:%S")
    await event.edit(f"Waktu saat ini: {time_str}")

@client.on(events.CallbackQuery)
async def callback_query_handler(event):
    chat_id = event.chat_id
    sender_id = event.sender_id

    if chat_id not in games:
        await event.answer("Permainan belum dimulai, tekan '/start' untuk memulai.")
        return

    game = games[chat_id]

    if sender_id != game["player"]:
        await event.answer("Hanya pemain yang memulai permainan yang bisa bermain!", alert=True)
        return

    move = int(event.data.decode().split('_')[1])
    if game["board"][move] != " ":
        await event.answer("Kotak sudah diisi!", alert=True)
        return

    game["board"][move] = "X"
    game["turn"] = "O"

    winner = check_winner(game["board"])
    if winner:
        if winner == "Draw":
            await event.edit("Hasil permainan: Seri!", buttons=[Button.inline("Mulai Ulang", b"tictactoe")])
        else:
            await event.edit(f"Pemenang: {winner} (Anda)!", buttons=[Button.inline("Mulai Ulang", b"tictactoe")])
        del games[chat_id]
        return

    bot_move = userbot_move(game["board"])
    if bot_move is not None:
        game["board"][bot_move] = "O"
        game["turn"] = "X"
        winner = check_winner(game["board"])
        if winner:
            if winner == "Draw":
                await event.edit("Hasil permainan: Seri!", buttons=[Button.inline("Mulai Ulang", b"tictactoe")])
            else:
                await event.edit("Pemenang: O (Userbot)!", buttons=[Button.inline("Mulai Ulang", b"tictactoe")])
            del games[chat_id]
            return

    buttons = create_board_buttons(game["board"])
    await event.edit("Giliran: X (Anda)", buttons=buttons)

print("Userbot berjalan...")
client.start()
client.run_until_disconnected()
