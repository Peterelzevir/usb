import json
import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import (MessageEntityBold, MessageEntityItalic, MessageEntityCode, 
                               MessageEntityPre, MessageEntityUnderline, MessageEntityTextUrl, 
                               MessageEntityStrike, InputMediaPhoto, InputMediaDocument)
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from config import api_id, api_hash, main_admin_id

# Inisialisasi client
client = TelegramClient('userbot', api_id, api_hash)

# Path file JSON untuk menyimpan pesan dan clones
JSON_FILE_PATH = 'pesan.json'
CLONES_FILE_PATH = 'clone.json'

# Fungsi untuk memuat pesan dari file JSON
def load_messages():
    if os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Fungsi untuk menyimpan pesan ke file JSON
def save_messages(messages):
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# Fungsi untuk memuat clone dari file JSON
def load_clones():
    if os.path.exists(CLONES_FILE_PATH):
        with open(CLONES_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Fungsi untuk menyimpan clone ke file JSON
def save_clones(clones):
    with open(CLONES_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(clones, f, ensure_ascii=False, indent=4)

# Muat pesan saat startup
messages = load_messages()
clones = load_clones()

# Fungsi untuk memeriksa apakah pengirim adalah admin
def is_admin(event):
    return event.sender_id == int(main_admin_id)

@client.on(events.NewMessage(pattern='^\.start$', from_users=main_admin_id))
async def start(event):
    username = (await event.get_sender()).username
    await event.reply(f"Hai @{username}, saya adalah userbot sebar list")

@client.on(events.NewMessage(pattern='^\.help$', from_users=main_admin_id))
async def help(event):
    help_text = """
    Fitur-fitur bot:
    1. .start - Menyapa pengguna.
    2. .add - Menyimpan pesan yang di-reply ke file JSON.
    3. .mulai - Memulai pengiriman pesan ke semua grup.
    4. .setdelay (index) (waktu) - Menyetel jeda waktu pengiriman pesan.
    5. .stop - Menghentikan pengiriman pesan.
    6. .clone - Membuat clone userbot.
    7. .listclone - Menampilkan daftar clone userbot.
    8. .delclone - Menghapus clone userbot.
    """
    await event.reply(help_text)

@client.on(events.NewMessage(pattern='^\.add$', from_users=main_admin_id))
async def add_message(event):
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        message_dict = {
            'id': len(messages) + 1,
            'message': reply_msg.to_dict()
        }
        messages.append(message_dict)
        save_messages(messages)
        await event.reply("Pesan telah disimpan!")

@client.on(events.NewMessage(pattern='^\.mulai$', from_users=main_admin_id))
async def mulai(event):
    async def send_messages():
        while True:
            for msg in messages:
                message = msg['message']
                # Ambil semua grup
                async for dialog in client.iter_dialogs():
                    if dialog.is_group:
                        if 'media' in message:
                            media = message['media']
                            if media['type'] == 'photo':
                                await client.send_file(dialog.id, InputMediaPhoto(media['photo']['id']))
                            elif media['type'] == 'document':
                                await client.send_file(dialog.id, InputMediaDocument(media['document']['id']))
                        else:
                            await client.send_message(dialog.id, message['message'])
                await asyncio.sleep(10)  # Ganti dengan waktu delay yang diinginkan

    asyncio.create_task(send_messages())
    await event.reply("Pengiriman pesan dimulai!")

@client.on(events.NewMessage(pattern=r'^\.setdelay (\d+) (\d+)$', from_users=main_admin_id))
async def set_delay(event):
    index = int(event.pattern_match.group(1)) - 1
    delay = int(event.pattern_match.group(2))
    if 0 <= index < len(messages):
        messages[index]['delay'] = delay
        save_messages(messages)
        await event.reply(f"Delay pesan {index + 1} disetel ke {delay} detik.")
    else:
        await event.reply("Index pesan tidak valid!")

@client.on(events.NewMessage(pattern='^\.stop$', from_users=main_admin_id))
async def stop(event):
    # Hentikan semua task pengiriman pesan
    for task in asyncio.all_tasks():
        task.cancel()
    await event.reply("Pengiriman pesan dihentikan!")

# Fungsi untuk membuat clone userbot
async def create_clone_userbot(api_id, api_hash, phone, main_admin_id):
    clone_client = TelegramClient(f'clone_{phone}', api_id, api_hash)
    try:
        await clone_client.start(phone)
        await clone_client.send_code_request(phone)
        await clone_client.send_message(main_admin_id, f"Kode OTP telah dikirim ke {phone}. Masukkan kode OTP dengan format .otp <kode>")
        return clone_client
    except PhoneNumberInvalidError:
        await client.send_message(main_admin_id, f"Nomor telepon {phone} tidak valid.")
        return None

# Fitur untuk membuat clone userbot
@client.on(events.NewMessage(pattern=r'^\.clone (\d+) (\d+) (\d+)$', from_users=main_admin_id))
async def clone_userbot(event):
    api_id = int(event.pattern_match.group(1))
    api_hash = event.pattern_match.group(2)
    phone = event.pattern_match.group(3)
    clone_client = await create_clone_userbot(api_id, api_hash, phone, main_admin_id)
    if clone_client:
        clone_data = {
            'username': (await clone_client.get_me()).username,
            'phone': phone,
            'api_id': api_id,
            'api_hash': api_hash,
            'main_admin_id': main_admin_id,
            'status': 'pending'
        }
        clones.append(clone_data)
        save_clones(clones)
        await event.reply(f"Userbot clone untuk {phone} sedang menunggu kode OTP.")

# Fitur untuk memasukkan kode OTP
@client.on(events.NewMessage(pattern=r'^\.otp (\d+)$', from_users=main_admin_id))
async def input_otp(event):
    code = event.pattern_match.group(1)
    for clone in clones:
        if clone['status'] == 'pending':
            clone_client = TelegramClient(f'clone_{clone["phone"]}', clone['api_id'], clone['api_hash'])
            await clone_client.connect()
            try:
                await clone_client.sign_in(clone['phone'], code)
                clone['status'] = 'active'
                save_clones(clones)
                await event.reply(f"Userbot clone untuk {clone['phone']} berhasil diaktifkan.")
                break
            except Exception as e:
                await event.reply(f"Gagal mengaktifkan clone userbot: {str(e)}")

# Fitur untuk melihat daftar clone userbot
@client.on(events.NewMessage(pattern='^\.listclone$', from_users=main_admin_id))
async def list_clone(event):
    if clones:
        message = "Daftar clone userbot:\n\n"
        for clone in clones:
            message += f"Username: {clone['username']}\nPhone: {clone['phone']}\nStatus: {clone['status']}\n"
        await event.reply(message)
    else:
        await event.reply("Tidak ada clone userbot yang terdaftar.")

# Fitur untuk menghapus clone userbot
@client.on(events.NewMessage(pattern=r'^\.delclone (\d+)$', from_users=main_admin_id))
async def delete_clone(event):
    phone = event.pattern_match.group(1)
    global clones
    clones = [clone for clone in clones if clone['phone'] != phone]
    save_clones(clones)
    await event.reply(f"Clone userbot dengan nomor {phone} telah dihapus.")

# Start client
client.start()
client.run_until_disconnected()
