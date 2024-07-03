import json
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import os

# Konfigurasi API Telegram
api_id = '28356794'
api_hash = 'a581331dabc5d4b7e0c7381a97dde824'

# Inisialisasi Telegram Client
client = TelegramClient('userbot', api_id, api_hash)

# Variabel Global
messages = []
delay_times = []
sending = False

# Membaca Pesan dari File JSON
if os.path.exists('messages.json'):
    with open('messages.json', 'r') as f:
        messages = json.load(f)
        
if os.path.exists('delays.json'):
    with open('delays.json', 'r') as f:
        delay_times = json.load(f)

# Fitur .start
@client.on(events.NewMessage(pattern=r'\.start'))
async def start(event):
    user = await event.get_sender()
    await event.respond(f'Hai @{user.username}, saya adalah userbot sebar list')

# Fitur .help
@client.on(events.NewMessage(pattern=r'\.help'))
async def help(event):
    help_text = (
        "Daftar Fitur:\n"
        ".start - Menyapa user\n"
        ".help - Menampilkan bantuan\n"
        ".add - Menambahkan pesan ke daftar\n"
        ".mulai - Memulai pengiriman pesan ke grup\n"
        ".setdelay <index> <waktu> - Mengatur jeda waktu pengiriman pesan\n"
        ".stop - Menghentikan pengiriman pesan\n"
        ".group - Menampilkan daftar grup yang diikuti userbot\n"
    )
    await event.respond(help_text)

# Fitur .add
@client.on(events.NewMessage(pattern=r'\.add'))
async def add(event):
    reply = await event.get_reply_message()
    if reply:
        message_data = {
            'text': reply.message,
            'media': None,
            'caption': reply.raw_text
        }
        if reply.media:
            message_data['media'] = reply.media
        
        messages.append(message_data)
        
        with open('messages.json', 'w') as f:
            json.dump(messages, f)
        
        await event.respond('Pesan berhasil ditambahkan.')
    else:
        await event.respond('Harap reply ke pesan yang ingin ditambahkan.')

# Fitur .mulai dan .stop
@client.on(events.NewMessage(pattern=r'\.mulai'))
async def mulai(event):
    global sending
    sending = True
    while sending:
        for i, message_data in enumerate(messages):
            if not sending:
                break
            for dialog in await client.get_dialogs():
                if dialog.is_group:
                    if message_data['media']:
                        await client.send_file(dialog.id, message_data['media'], caption=message_data['caption'])
                    else:
                        await client.send_message(dialog.id, message_data['text'])
            await asyncio.sleep(delay_times[i] if i < len(delay_times) else 5)

@client.on(events.NewMessage(pattern=r'\.stop'))
async def stop(event):
    global sending
    sending = False
    await event.respond('Pengiriman pesan dihentikan.')

# Fitur .setdelay
@client.on(events.NewMessage(pattern=r'\.setdelay (\d+) (\d+)'))
async def setdelay(event):
    index = int(event.pattern_match.group(1))
    waktu = int(event.pattern_match.group(2))
    if index < len(messages):
        if len(delay_times) <= index:
            delay_times.extend([5] * (index - len(delay_times) + 1))
        delay_times[index] = waktu
        with open('delays.json', 'w') as f:
            json.dump(delay_times, f)
        await event.respond(f'Delay pesan ke-{index} diatur ke {waktu} detik.')
    else:
        await event.respond('Index pesan tidak valid.')

# Fitur .dellist & .ceklist
@client.on(events.NewMessage(pattern=r'\.ceklist'))
async def ceklist(event):
    list_text = "Daftar Pesan:\n"
    for i, message_data in enumerate(messages):
        list_text += f"{i}: {message_data['text']}\n"
    await event.respond(list_text)

@client.on(events.NewMessage(pattern=r'\.dellist (\d+)'))
async def dellist(event):
    index = int(event.pattern_match.group(1))
    if 0 <= index < len(messages):
        del messages[index]
        with open('messages.json', 'w') as f:
            json.dump(messages, f)
        await event.respond(f"Pesan pada index {index} berhasil dihapus.")
    else:
        await event.respond('Index pesan tidak valid.')


# Fitur .group
@client.on(events.NewMessage(pattern=r'\.group'))
async def group(event):
    group_list = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            group_list.append(dialog.title)
    group_text = "Grup yang diikuti userbot:\n" + "\n".join(group_list)
    await event.respond(group_text)

# Menjalankan Client
async def main():
    await client.start()
    print("Userbot berjalan...")
    await client.run_until_disconnected()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
