import json
import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError, PhoneCodeInvalidError, FloodWaitError
from datetime import datetime

# Konfigurasi API Telegram
api_id = '28356794'
api_hash = 'a581331dabc5d4b7e0c7381a97dde824'

# Inisialisasi Telegram Client
client = TelegramClient('userbot', api_id, api_hash)

# Variabel Global
forward_list = []
messages = []
delay_times = []
is_forwarding = False
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

# Fungsi untuk menyimpan daftar forward ke file
def save_forward_list(forward_list):
    with open('messages.json', 'w') as f:
        json.dump(forward_list, f, default=json_serial)

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
        ".clone - Membuat userbot clone\n"
        ".listclone - Menampilkan daftar userbot clone yang aktif\n"
        ".delclone <clone_id> - Menghapus userbot clone berdasarkan ID\n"
    )
    await event.respond(help_text)

# Fungsi untuk verifikasi admin utama 
def is_admin(user_id): 
    return user_id in admins

# Handler untuk menambah pesan ke daftar forward
@client.on(events.NewMessage(pattern='.addforward'))
async def add_forward(event):
    if is_admin(event.sender_id):
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
            message_data = {
                'text': reply_message.raw_text,
                'media': None,
                'caption': reply_message.raw_text,
                'entities': []
            }
            
            # Tambahkan entities
            if reply_message.entities:
                for entity in reply_message.entities:
                    message_data['entities'].append({
                        'type': entity.__class__.__name__,
                        'offset': entity.offset,
                        'length': entity.length
                    })
            
            if reply_message.media:
                media_data = {
                    'type': reply_message.media.__class__.__name__.replace('MessageMedia', '').lower(),
                    'file': await client.download_media(reply_message.media),
                    'caption': reply_message.raw_text,
                    'entities': message_data['entities']
                }
                message_data['media'] = media_data
            
            forward_list.append(message_data)
            save_forward_list(forward_list)
            await event.respond(f'✅ Pesan ditambahkan ke daftar forward:\n\n```{reply_message.raw_text or "Media"}```', parse_mode='Markdown')
        else:
            await event.respond('⚠️ Balas ke pesan yang ingin ditambahkan ke daftar forward', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

# Handler untuk mulai mengirim pesan
@client.on(events.NewMessage(pattern='.mulai'))
async def mulai_forward(event):
    if is_admin(event.sender_id):
        global is_forwarding
        if is_forwarding:
            await event.respond('⚠️ Pengiriman pesan otomatis sudah berjalan', parse_mode='Markdown')
            return
        is_forwarding = True
        await event.respond('Oke otw kirim')
        while is_forwarding:
            for msg in forward_list:
                for dialog in await client.get_dialogs():
                    try:
                        if dialog.is_group:
                            if msg['media']:
                                await client.send_file(dialog.id, msg['media']['file'], caption=msg['caption'], entities=msg['entities'])
                            else:
                                await client.send_message(dialog.id, msg['text'], entities=msg['entities'])
                    except Exception as e:
                        print(f"Error mengirim pesan ke grup/channel {dialog.title}: {e}")
                await asyncio.sleep(delay_times[forward_list.index(msg)] if forward_list.index(msg) < len(delay_times) else 5)
            await asyncio.sleep(5)
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='Markdown')
    raise events.StopPropagation

# Handler untuk cek daftar pesan
@client.on(events.NewMessage(pattern=r'\.ceklist'))
async def ceklist(event):
    if is_admin(event.sender_id):
        list_text = "Daftar Pesan:\n"
        for i, message_data in enumerate(forward_list):
            if 'text' in message_data:
                list_text += f"{i}: {message_data['text']}\n"
            elif 'formatted_text' in message_data:
                list_text += f"{i}: {message_data['formatted_text']}\n"
        await event.respond(list_text)
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Handler untuk menghapus pesan dari daftar
@client.on(events.NewMessage(pattern=r'\.dellist (\d+)'))
async def dellist(event):
    if is_admin(event.sender_id):
        index = int(event.pattern_match.group(1))
        if index < len(forward_list):
            deleted_message = forward_list.pop(index)
            save_forward_list(forward_list)
            await event.respond(f'Pesan ke-{index} berhasil dihapus:\n\n{deleted_message["text"] if "text" in deleted_message else "Media"}')
        else:
            await event.respond('Index pesan tidak valid.')
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Handler untuk mengatur delay masing-masing pesan
@client.on(events.NewMessage(pattern=r'\.setdelay (\d+) (\d+)'))
async def setdelay(event):
    if is_admin(event.sender_id):
        index = int(event.pattern_match.group(1))
        waktu = int(event.pattern_match.group(2))
        if index < len(forward_list):
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

@client.on(events.NewMessage(pattern=r'\.stop'))
async def stop(event):
    if is_admin(event.sender_id):
        global is_forwarding
        is_forwarding = False
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

# Handler untuk meminta informasi cloning
@client.on(events.NewMessage(pattern=r'\.clone'))
async def clone(event):
    if is_admin(event.sender_id):
        await event.respond('Silakan masukkan nomor telepon yang ingin digunakan untuk cloning:')
        @client.on(events.NewMessage(from_users=admins))
        async def get_phone_number(event_phone):
            phone_number = event_phone.message.message
            await event.respond('Silakan masukkan kode OTP yang diterima:')
            @client.on(events.NewMessage(from_users=admins))
            async def get_otp_code(event_otp):
                otp_code = event_otp.message.message
                try:
                    new_client = TelegramClient(f'userbot_clone_{event_phone.sender_id}', api_id, api_hash)
                    await new_client.start(phone_number, otp_code)
                    clone_data = {
                        'phone_number': phone_number,
                        'admin_id': event_phone.sender_id,
                        'api_id': api_id,
                        'api_hash': api_hash,
                        'clone_id': event_phone.sender_id,
                        'created': str(datetime.now())
                    }
                    clone_file = f'clone_{event_phone.sender_id}.json'
                    with open(clone_file, 'w') as f:
                        json.dump(clone_data, f)
                    await event_phone.respond('Userbot clone berhasil dibuat.')
                except PhoneNumberInvalidError:
                    await event_phone.respond('Nomor telepon tidak valid.')
                except PhoneCodeInvalidError:
                    await event_phone.respond('Kode OTP tidak valid.')
                except FloodWaitError as e:
                    await event_phone.respond(f'Harap tunggu {e.seconds} detik sebelum mencoba lagi.')
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .listclone
@client.on(events.NewMessage(pattern=r'\.listclone'))
async def listclone(event):
    if is_admin(event.sender_id):
        clone_list = []
        for file in os.listdir():
            if file.startswith('clone_') and file.endswith('.json'):
                with open(file, 'r') as f:
                    clone_list.append(json.load(f))
        if clone_list:
            clone_text = "Daftar Userbot Clone:\n"
            for clone in clone_list:
                clone_text += (
                    f"Phone Number: {clone['phone_number']}\n"
                    f"Admin ID: {clone['admin_id']}\n"
                    f"Clone ID: {clone['clone_id']}\n"
                    f"Created: {clone['created']}\n\n"
                )
            await event.respond(clone_text)
        else:
            await event.respond('Tidak ada userbot clone yang ditemukan.')
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

# Fitur .delclone
@client.on(events.NewMessage(pattern=r'\.delclone (\d+)'))
async def delclone(event):
    if is_admin(event.sender_id):
        clone_id = event.pattern_match.group(1)
        clone_file = f'clone_{clone_id}.json'
        if os.path.exists(clone_file):
            os.remove(clone_file)
            await event.respond(f'Userbot clone dengan ID {clone_id} berhasil dihapus.')
        else:
            await event.respond('ID clone tidak valid.')
    else:
        await event.respond('Fitur ini hanya dapat digunakan oleh admin utama.')

client.start()
client.run_until_disconnected()
