# source by hiyaok programmer
# not for resale
# update V1.3

import logging
import time
import asyncio
import sqlite3
import json
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

logging.basicConfig(level=logging.INFO)

api_id = '28356794'  # Ganti dengan API ID Anda
api_hash = 'a581331dabc5d4b7e0c7381a97dde824'  # Ganti dengan API Hash Anda
string_session = '1BVtsOGcBu5uEA0k29aCSrBvDPXZ8WXHIGdwp2chGoIw6GLDwZLBDnPu6xH7ocvb1pASn3sCHRUZZ_mo4oKrVvdMGdJ6zY2srwbmmENO97drhEYAW8AOknk-O5Gqvxs6j4xQQnQ8KrpBSK-xCoKUUIDl7rFG9yHawzs5KfqUXh1b8pPpPO8j6dAvWNARpLMOLa_qt7I46QZcgRjbxFa6rMpOutgiBObv24v93Hyefd0uWhhFuObb9ORgovcfVuJy5VGUsdmhlngv1jz-Vk8HqmNaKSM73kvgctbeIFXVbwnqRdPkYLVA49q_0d6YubcFnrqazkPwtlJxxY57CedOUfoO72G67DCc='  # Ganti dengan String Session Anda
admin_id = '5988451717'  # Ganti dengan ID admin Anda

client = TelegramClient(StringSession(string_session), api_id, api_hash)
clone_clients = {}

# Setup database
def init_db():
    conn = sqlite3.connect('userbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clones (user_id INTEGER PRIMARY KEY, api_id TEXT, api_hash TEXT, string_session TEXT, admin_id TEXT, expiry_date TEXT)''')
    conn.commit()
    conn.close()

init_db()

forward_list_file = 'forward_list.json'
delay_settings = 60
is_forwarding = False

# Load forward list from JSON file
def load_forward_list():
    try:
        with open(forward_list_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save forward list to JSON file
def save_forward_list(forward_list):
    with open(forward_list_file, 'w') as file:
        json.dump(forward_list, file, indent=4)

forward_list = load_forward_list()

async def create_clone(api_id, api_hash, string_session, admin_id, expiry_date):
    clone_client = TelegramClient(StringSession(string_session), api_id, api_hash)
    await clone_client.start()
    clone_clients[admin_id] = (clone_client, expiry_date)
    return clone_client

async def check_expiry():
    while True:
        for admin_id, (clone_client, expiry_date) in list(clone_clients.items()):
            if datetime.now() > expiry_date:
                await clone_client.disconnect()
                del clone_clients[admin_id]
                with sqlite3.connect('userbot.db') as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM clones WHERE admin_id = ?", (admin_id,))
                    conn.commit()
        await asyncio.sleep(60)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id == int(admin_id):
        await event.respond('Halo, saya adalah userbot Telegram.\n\n➡️ /help untuk melihat fitur lengkap.', buttons=[Button.text('/help')], parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/clone'))
async def clone(event):
    if event.sender_id == int(admin_id):
        buttons = [
            [Button.text("API ID"), Button.text("API Hash")],
            [Button.text("String Session"), Button.text("Admin ID")]
        ]
        await event.respond('Silakan siapkan informasi berikut untuk kloning:\n1. API ID\n2. API Hash\n3. String Session\n4. Admin ID\n5. Expiry (dalam format: YYYY-MM-DD HH:MM)', buttons=buttons, parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addclone'))
async def add_clone(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 6:
            _, api_id, api_hash, string_session, admin_id, expiry = params
            try:
                expiry_date = datetime.strptime(expiry, '%Y-%m-%d %H:%M')
            except ValueError:
                await event.respond('Format tanggal kedaluwarsa salah! Gunakan: YYYY-MM-DD HH:MM', parse_mode='Markdown')
                return

            clone_client = await create_clone(api_id, api_hash, string_session, admin_id, expiry_date)
            with sqlite3.connect('userbot.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO clones (api_id, api_hash, string_session, admin_id, expiry_date) VALUES (?, ?, ?, ?, ?)", (api_id, api_hash, string_session, admin_id, expiry_date.strftime('%Y-%m-%d %H:%M')))
                conn.commit()
            await event.respond('Userbot kloning berhasil dibuat.', parse_mode='Markdown')
        else:
            await event.respond('Format salah! Gunakan: /addclone [API_ID] [API_HASH] [STRING_SESSION] [ADMIN_ID] [EXPIRY_DATE]', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/deleteclone'))
async def delete_clone(event):
    if event.sender_id == int(admin_id):
        try:
            clone_admin_id = event.message.text.split()[1]
            with sqlite3.connect('userbot.db') as conn:
                c = conn.cursor()
                c.execute("DELETE FROM clones WHERE admin_id = ?", (clone_admin_id,))
                conn.commit()
            await event.respond('Clone bot telah dihapus.', parse_mode='Markdown')
        except (IndexError, sqlite3.Error) as e:
            await event.respond('Format salah atau terjadi kesalahan!', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/runtime'))
async def runtime(event):
    if event.sender_id == int(admin_id):
        current_time = datetime.now()
        uptime = current_time - start_time
        await event.respond(f'Bot telah berjalan selama: {uptime}.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    if event.sender_id == int(admin_id):
        await event.respond(
            'Berikut adalah perintah yang tersedia:\n\n'
            '/start - Mulai bot\n'
            '/help - Bantuan\n'
            '/bantuan - Bantuan\n'
            '/clone - Siapkan kloning userbot\n'
            '/addclone [API_ID] [API_HASH] [STRING_SESSION] [ADMIN_ID] [EXPIRY_DATE] - Tambah userbot kloning\n'
            '/addforward - Tambah pesan untuk di forward\n'
            '/delforward - Hapus pesan dari daftar forward\n'
            '/setdelay - Atur delay pengiriman pesan\n'
            '/checklist - Lihat daftar pesan yang di forward\n'
            '/groups - Lihat dan kelola grup yang diikuti bot\n'
            '/checkspeed - Cek kecepatan pengiriman bot\n'
            '/join [GROUP_OR_CHANNEL] - Gabung ke grup atau channel\n'
            '/setname [GROUP_ID] [NEW_NAME] - Ubah nama grup\n'
            '/addmember [GROUP_ID] [USER_ID] - Tambah anggota grup\n'
            '/kick [GROUP_ID] [USER_ID] - Kick anggota dari grup\n'
            '/ban [GROUP_ID] [USER_ID] - Ban anggota dari grup\n'
            '/unban [GROUP_ID] [USER_ID] - Unban anggota dari grup\n'
            '/mute [GROUP_ID] [USER_ID] - Mute anggota di grup\n'
            '/unmute [GROUP_ID] [USER_ID] - Unmute anggota di grup\n'
            '/mulai - Mulai mengirim pesan otomatis\n'
            '/stop - Hentikan pengiriman pesan otomatis\n'
            '/listclone - Lihat daftar kloning userbot',
            buttons=[Button.text('/start'), Button.text('/help')],
            parse_mode='Markdown'
        )
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addforward'))
async def addforward(event):
    if event.sender_id == int(admin_id):
        try:
            text = event.message.message.split(maxsplit=1)[1]
            forward_list.append(text)
            save_forward_list(forward_list)
            await event.respond('Pesan berhasil ditambahkan ke daftar forward.', parse_mode='Markdown')
        except IndexError:
            await event.respond('Penggunaan: /addforward [TEKS]', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/delforward'))
async def delforward(event):
    if event.sender_id == int(admin_id):
        try:
            index = int(event.message.message.split()[1])
            if 0 <= index < len(forward_list):
                del forward_list[index]
                save_forward_list(forward_list)
                await event.respond('Pesan berhasil dihapus dari daftar forward.', parse_mode='Markdown')
            else:
                await event.respond('Indeks di luar jangkauan!', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Penggunaan: /delforward [INDEX]', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/checklist'))
async def checklist(event):
    if event.sender_id == int(admin_id):
        if forward_list:
            response = 'Daftar pesan yang di forward:\n'
            response += '\n'.join([f'{i}. {text}' for i, text in enumerate(forward_list)])
            await event.respond(response, parse_mode='Markdown')
        else:
            await event.respond('Daftar forward kosong.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/groups'))
async def groups(event):
    if event.sender_id == int(admin_id):
        dialogs = await client.get_dialogs()
        groups = [dialog for dialog in dialogs if dialog.is_group]
        response = 'Daftar grup:\n'
        response += '\n'.join([f'{i + 1}. {group.title} (ID: {group.id})' for i, group in enumerate(groups)])
        await event.respond(response, parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/setdelay'))
async def setdelay(event):
    if event.sender_id == int(admin_id):
        try:
            delay = int(event.message.message.split()[1])
            global delay_settings
            delay_settings = delay
            await event.respond(f'Delay pengiriman pesan diatur ke {delay} detik.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Penggunaan: /setdelay [DETIK]', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/mulai'))
async def mulai(event):
    if event.sender_id == int(admin_id):
        global is_forwarding
        is_forwarding = True
        await event.respond('Pengiriman pesan otomatis dimulai.', parse_mode='Markdown')

        while is_forwarding:
            for text in forward_list:
                dialogs = await client.get_dialogs()
                groups = [dialog for dialog in dialogs if dialog.is_group]
                for group in groups:
                    await client.send_message(group, text)
                    await asyncio.sleep(delay_settings)
            await asyncio.sleep(delay_settings)
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/stop'))
async def stop(event):
    if event.sender_id == int(admin_id):
        global is_forwarding
        is_forwarding = False
        await event.respond('Pengiriman pesan otomatis dihentikan.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/checkspeed'))
async def checkspeed(event):
    if event.sender_id == int(admin_id):
        start = time.time()
        await event.respond('Cek kecepatan...')
        end = time.time()
        await event.respond(f'Kecepatan pengiriman bot: {end - start} detik.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/listclone'))
async def listclone(event):
    if event.sender_id == int(admin_id):
        with sqlite3.connect('userbot.db') as conn:
            c = conn.cursor()
            c.execute("SELECT admin_id, expiry_date FROM clones")
            clones = c.fetchall()
        response = 'Daftar kloning userbot:\n'
        response += '\n'.join([f'Admin ID: {admin_id}, Kedaluwarsa: {expiry_date}' for admin_id, expiry_date in clones])
        await event.respond(response, parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage)
async def forward_messages(event):
    if event.sender_id == int(admin_id) and event.message.text in forward_list:
        dialogs = await client.get_dialogs()
        groups = [dialog for dialog in dialogs if dialog.is_group]
        for group in groups:
            await client.send_message(group, event.message.text)

@client.on(events.NewMessage)
async def photo_handler(event):
    if isinstance(event.message.media, MessageMediaPhoto):
        dialogs = await client.get_dialogs()
        groups = [dialog for dialog in dialogs if dialog.is_group]
        for group in groups:
            await client.send_message(group, event.message.message, file=event.message.media)

@client.on(events.NewMessage)
async def document_handler(event):
    if isinstance(event.message.media, MessageMediaDocument):
        dialogs = await client.get_dialogs()
        groups = [dialog for dialog in dialogs if dialog.is_group]
        for group in groups:
            await client.send_message(group, event.message.message, file=event.message.media)

start_time = datetime.now()

with client:
    client.loop.run_until_complete(check_expiry())
    client.run_until_disconnected()
