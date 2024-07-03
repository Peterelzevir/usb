import json
import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError, PhoneCodeInvalidError, FloodWaitError

# Konfigurasi API Telegram
api_id = '28356794'
api_hash = 'a581331dabc5d4b7e0c7381a97dde824'

# Inisialisasi Telegram Client
client = TelegramClient('userbot', api_id, api_hash)

# Variabel Global
messages = []
delay_times = []
sending = False
admins = [5988451717]  # Ganti dengan ID admin utama Anda

# Membaca Pesan dari File JSON
def load_messages():
    global messages, delay_times
    if os.path.exists('messages.json'):
        with open('messages.json', 'r') as f:
            messages = json.load(f)
    if os.path.exists('delays.json'):
        with open('delays.json', 'r') as f:
            delay_times = json.load(f)

# Fungsi untuk serialisasi objek JSON
def json_serial(obj):
    if isinstance(obj, bytes):
        return obj.decode()
    raise TypeError ("Type not serializable")

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
        ".ceklist - Menampilkan daftar pesan yang tersimpan\n"
        ".dellist <index> - Menghapus pesan dari daftar berdasarkan index\n"
        ".clone <api_id> <api_hash> <admin_id> <expiration_time> - Membuat userbot clone\n"
        ".listclone - Menampilkan daftar userbot clone yang aktif\n"
        ".delclone <clone_id> - Menghapus userbot clone berdasarkan ID\n"
    )
    await event.respond(help_text)

# Fungsi untuk verifikasi admin utama
def is_admin(user_id):
    return user_id in admins

# Fitur .add
@clie# Fitur .add
@client.on(events.NewMessage(pattern=r'\.add'))
async def add(event):
    if is_admin(event.sender_id):
        reply = await event.get_reply_message()
        if reply:
            message_data = {
                'text': reply.raw_text,  # Simpan caption mentah dari pesan
                'media': None,
                'caption': reply.raw_text,  # Simpan caption mentah dari pesan
                'formatted_text': reply.text  # Simpan teks yang diformat dari pesan
            }
            if reply.media:
                if isinstance(reply.media, MessageMediaPhoto):
                    media_data = {
                        'type': 'photo',
                        'file': await client.download_media(reply.media),
                        'caption': reply.raw_text  # Simpan caption mentah dari media
                    }
                    message_data['media'] = media_data
                elif isinstance(reply.media, MessageMediaDocument):
                    media_data = {
                        'type': 'document',
                        'file': await client.download_media(reply.media),
                        'caption': reply.raw_text  # Simpan caption mentah dari media
                    }
                    message_data['media'] = media_data
                elif isinstance(reply.media, MessageMediaVideo):
                    media_data = {
                        'type': 'video',
                        'file': await client.download_media(reply.media),
                        'caption': reply.raw_text  # Simpan caption mentah dari media
                    }
                    message_data['media'] = media_data
                elif isinstance(reply.media, MessageMediaPhoto):
                    media_data = {
                        'type': 'gif',
                        'file': await client.download_media(reply.media),
                        'caption': reply.raw_text  # Simpan caption mentah dari media
                    }
                    message_data['media'] = media_data

            messages.append(message_data)
            
            with open('messages.json', 'w') as f:
                json.dump(messages, f, default=json_serial)
            
            await event.respond('Pesan berhasil ditambahkan.')
        else:
            await event.respond('Harap reply ke pesan yang ingin ditambahkan.')
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .mulai
@client.on(events.NewMessage(pattern=r'\.mulai'))
async def mulai(event):
    if is_admin(event.sender_id):
        global sending
        await event.respond('Oke otw kirim')
        sending = True
        while sending:
            for i, message_data in enumerate(messages):
                if not sending:
                    break
                for dialog in await client.get_dialogs():
                    if dialog.is_group:
                        try:
                            if message_data['media']:
                                media_type = message_data['media']['type']
                                media_file = message_data['media']['file']
                                media_caption = message_data['media']['caption']
                                if media_type == 'photo':
                                    await client.send_file(dialog.id, media_file, caption=media_caption)
                                elif media_type == 'document':
                                    await client.send_file(dialog.id, media_file, caption=media_caption)
                                elif media_type == 'video':
                                    await client.send_file(dialog.id, media_file, caption=media_caption)
                                elif media_type == 'gif':
                                    await client.send_file(dialog.id, media_file, caption=media_caption)
                            else:
                                # Menggunakan formatted_text untuk pesan teks
                                await client.send_message(dialog.id, message_data['formatted_text'])
                        except Exception as e:
                            print(f"Error mengirim pesan ke grup {dialog.title}: {e}")
                await asyncio.sleep(delay_times[i] if i < len(delay_times) else 5)
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .setdelay
@client.on(events.NewMessage(pattern=r'\.setdelay (\d+) (\d+)'))
async def setdelay(event):
    if is_admin(event.sender_id):
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
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .stop
@client.on(events.NewMessage(pattern=r'\.stop'))
async def stop(event):
    if is_admin(event.sender_id):
        global sending
        sending = False
        await event.respond('Pengiriman pesan dihentikan.')
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .group
@client.on(events.NewMessage(pattern=r'\.group'))
async def group(event):
    if is_admin(event.sender_id):
        group_list = []
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                group_list.append(dialog.title)
        group_text = "Grup yang diikuti userbot:\n" + "\n".join(group_list)
        await event.respond(group_text)
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .ceklist
@client.on(events.NewMessage(pattern=r'\.ceklist'))
async def ceklist(event):
    if is_admin(event.sender_id):
        list_text = "Daftar Pesan:\n"
        for i, message_data in enumerate(messages):
            list_text += f"{i}: {message_data['text']}\n"
        await event.respond(list_text)
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .dellist
@client.on(events.NewMessage(pattern=r'\.dellist (\d+)'))
async def dellist(event):
    if is_admin(event.sender_id):
        index = int(event.pattern_match.group(1))
        if 0 <= index < len(messages):
            del messages[index]
            with open('messages.json', 'w') as f:
                json.dump(messages, f, default=json_serial)
            await event.respond(f"Pesan pada index {index} berhasil dihapus.")
        else:
            await event.respond('Index pesan tidak valid.')
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .clone
@client.on(events.NewMessage(pattern=r'\.clone (\d+) (\w+) (\d+) (\d+)'))
async def clone(event):
    if is_admin(event.sender_id):
        api_id = event.pattern_match.group(1)
        api_hash = event.pattern_match.group(2)
        admin_id = event.pattern_match.group(3)
        expiration_time = event.pattern_match.group(4)
        
        # Proses pengiriman OTP
        try:
            phone_number = input("Masukkan nomor telepon untuk verifikasi OTP: ")
            await client.sign_in(phone=phone_number)
            
            code = input("Masukkan kode OTP yang dikirimkan ke nomor tersebut: ")
            await client.sign_in(code=code)
            
            # Simpan detail userbot clone ke database
            clone_details = {
                'api_id': api_id,
                'api_hash': api_hash,
                'admin_id': admin_id,
                'expiration_time': expiration_time,
                'messages': [],
                'delay_times': []
            }
            
            # Simpan detail ke file json terpisah untuk userbot clone
            clone_filename = f'clone_{random.randint(1000, 9999)}.json'
            with open(clone_filename, 'w') as f:
                json.dump(clone_details, f, default=json_serial)
            
            await event.respond(f"Userbot clone berhasil dibuat dengan ID {clone_filename}.")
        except PhoneNumberInvalidError:
            await event.respond("Nomor telepon tidak valid.")
        except PhoneCodeInvalidError:
            await event.respond("Kode OTP salah.")
        except Exception as e:
            await event.respond(f"Terjadi kesalahan: {str(e)}")
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .listclone
@client.on(events.NewMessage(pattern=r'\.listclone'))
async def listclone(event):
    if is_admin(event.sender_id):
        clone_list = []
        for filename in os.listdir():
            if filename.startswith('clone_') and filename.endswith('.json'):
                with open(filename, 'r') as f:
                    clone_data = json.load(f)
                    clone_list.append(f"ID: {filename}, Admin ID: {clone_data['admin_id']}, Expiration Time: {clone_data['expiration_time']}")
        clone_text = "Daftar Userbot Clone:\n" + "\n".join(clone_list)
        await event.respond(clone_text)
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .delclone
@client.on(events.NewMessage(pattern=r'\.delclone (\w+)'))
async def delclone(event):
    if is_admin(event.sender_id):
        clone_id = event.pattern_match.group(1)
        if os.path.exists(clone_id):
            os.remove(clone_id)
            await event.respond(f"Userbot clone dengan ID {clone_id} berhasil dihapus.")
        else:
            await event.respond('ID userbot clone tidak valid.')
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Menjalankan Client
async def main():
    load_messages()
    await client.start()
    print("Userbot berjalan...")
    await client.run_until_disconnected()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
