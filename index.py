# source by @hiyaok
# telegram => @hiyaok

#jgn otak atik 
import json
import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError, PhoneCodeInvalidError, FloodWaitError
from datetime import datetime

# Konfigurasi API Telegram
api_id = '' #ganti api id
api_hash = '' #ganti sama api hash

# Inisialisasi Telegram Client
client = TelegramClient('userbot', api_id, api_hash)

# variabel
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
    await event.respond(f'🖐🏻 Hallo @{user.username} saya adalah userbot sebar list\n\n➡️ /help untuk list fitur')

# Fitur .help
@client.on(events.NewMessage(pattern=r'\.help'))
async def help(event):
    help_text = (
        "Daftar Fitur ⛱:\n"
        ".start - Menyapa user 🖐🏻\n"
        ".help - Menampilkan bantuan 😎\n"
        ".add - Menambahkan pesan ke daftar 📁\n"
        ".send - Memulai pengiriman pesan ke grup ⚡\n"
        ".setdelay <index> <waktu> - Mengatur jeda waktu pengiriman masing pesan 🔥\n"
        ".stop - Menghentikan pengiriman pesan ❗\n"
        ".group - Menampilkan daftar grup yang diikuti userbot 🔥\n"
        ".ceklist - Menampilkan daftar pesan yang tersimpan 🔐\n"
        ".dellist <index> - Menghapus pesan dari daftar berdasarkan index 🔥\n"
        ".join [ link group ] untuk userbot join group 💡\n"
        ".kick [ id group ] [ id user ] untuk kick user di group 🗿\n"
        ".addmember [ id group ] [ id user ] invite user ke group 🗿\n"
        ".cekspeed - untuk cek speed userbot ⚡\n"
        ".setnamegroup [ id group ] [ name new ] untuk set name group 💡\n"
        ".ban - ban user dari group kamu 🔥\n"
        ".unban - unban user dari group kamu 💡\n"
        ".mute - mute pengguna dari group kamu 🔥\n"
        ".unmute - unmute pengguna dari group kamu 🔥\n"
    )
    await event.respond(help_text)

# Fungsi untuk verifikasi admin utama 
def is_admin(user_id): 
    return user_id in admins

# Handler untuk menambah pesan ke daftar forward
@client.on(events.NewMessage(pattern='\.add'))
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
@client.on(events.NewMessage(pattern='\.send'))
async def mulai_forward(event):
    if is_admin(event.sender_id):
        global is_forwarding
        if is_forwarding:
            await event.respond('⚠️ Pengiriman pesan otomatis sudah berjalan', parse_mode='Markdown')
            return
        is_forwarding = True
        await event.respond('Oke otw kirim 🔥')
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
                        print(f"Error mengirim pesan ke grup {dialog.title}: {e}")
                await asyncio.sleep(delay_times[forward_list.index(msg)] if forward_list.index(msg) < len(delay_times) else 5)
            await asyncio.sleep(5)
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
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
@client.on(events.NewMessage(pattern='\.group'))
async def list_groups(event):
    if event.sender_id == int(admin_id):
        dialogs = await client.get_dialogs()
        groups = [dialog for dialog in dialogs if dialog.is_group]
        group_list = "\n".join([f"{i+1}. {group.name} - `{group.id}`" for i, group in enumerate(groups)])
        await event.respond(f'📋 Daftar grup\n\n{group_list}', parse_mode='Markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.addmember'))
async def add_group_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, view_messages=False)))
            await event.respond(f'✅ Anggota berhasil ditambahkan ke grup: {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /addmember <group_id> <user_id>', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.cekspeed'))
async def check_speed(event):
    if event.sender_id == int(admin_id):
        start = time.time()
        await event.respond('⚡ checking', parse_mode='Markdown')
        end = time.time()
        speed = end - start
        await event.respond(f'⚡ kecepatan bot: {speed:.2f} detik', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.setnamegroup'))
async def set_group_name(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ', 2)
            group_id = int(params[1])
            new_name = params[2]
            await client(EditTitleRequest(group_id, new_name))
            await event.respond(f'✅ Nama grup berhasil diubah menjadi: {new_name}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /setname <group_id> <nama_baru>', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.kick'))
async def kick_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, view_messages=True)))
            await event.respond(f'✅ Anggota berhasil di-kick dari grup: {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /kick <group_id> <user_id>', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.ban'))
async def ban_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, view_messages=True)))
            await event.respond(f'✅ Anggota berhasil di-ban dari grup: {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /ban <group_id> <user_id>', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.unban'))
async def unban_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, view_messages=False)))
            await event.respond(f'✅ Anggota berhasil di-unban dari grup: {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /unban <group_id> <user_id>', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.mute'))
async def mute_member(event):
    if event.sender_id == int(admin_id):
        try:
            _, group_id, user_id = event.message.text.split()
            await client(EditBannedRequest(int(group_id), int(user_id), ChatBannedRights(until_date=None, send_messages=True)))
            await event.respond(f'✅ Pengguna {user_id} dimute di grup {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /mute [GROUP_ID] [USER_ID]', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='.\unmute'))
async def unmute_member(event):
    if event.sender_id == int(admin_id):
        try:
            _, group_id, user_id = event.message.text.split()
            await client(EditBannedRequest(int(group_id), int(user_id), ChatBannedRights(until_date=None, send_messages=False)))
            await event.respond(f'✅ Pengguna {user_id} diunmute di grup {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /unmute [GROUP_ID] [USER_ID]', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.join'))
async def join_group(event):
    if event.sender_id == int(admin_id):
        try:
            group_link = event.message.text.split(' ')[1]
            await client(JoinChannelRequest(group_link))
            await event.respond(f'✅ Berhasil bergabung ke grup: {group_link}', parse_mode='Markdown')
        except IndexError:
            await event.respond('⚠️ Gunakan format: /join <link_grup>*', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

client.start()
client.run_until_disconnected()
