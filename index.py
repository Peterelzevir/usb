# source by @hiyaok
# telegram => @hiyaok

#jgn otak atik 
import json
import asyncio
import os
import time
from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest, EditTitleRequest, JoinChannelRequest, EditAdminRequest, EditPhotoRequest, InviteToChannelRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights, InputChatUploadedPhoto
from telethon.tl.functions.channels import InviteToChannelRequest, EditBannedRequest, GetFullChannelRequest, EditPhotoRequest
from telethon.tl.types import InputPeerUser, InputPeerChannel, InputChatUploadedPhoto
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError, PhoneCodeInvalidError, FloodWaitError
from datetime import datetime

# Konfigurasi API Telegram
api_id = '28356794' #ganti api id
api_hash = 'a581331dabc5d4b7e0c7381a97dde824' #ganti sama api hash

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
    await event.respond(f'🖐🏻 Hallo @{user.username} saya adalah userbot sebar list\n\n➡️ .help untuk list fitur')

# Fitur .help
@client.on(events.NewMessage(pattern=r'\.help'))
async def help(event):
    help_text = (
        "Daftar Fitur ⛱:\n\n"
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
        ".setadmin - set admin 💡\n"
        ".setfotogroup - set foto group ⚡\n"
        ".deladmin - hapus kepemilikan admin 🗿\n"
        ".unmuteall - unmute semua member group 🔥\n"
        ".muteall - mute all semua member group 🗿\n"
        ".listmember - list member group 💡\n"
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

@client.on(events.NewMessage(pattern='\.group'))
async def list_groups(event):
    if is_admin(event.sender_id):
        dialogs = await client.get_dialogs()
        groups = [dialog for dialog in dialogs if dialog.is_group]
        group_list = "\n".join([f"{i+1}. {group.name} - `{group.id}`" for i, group in enumerate(groups)])
        await event.respond(f'📋 Daftar grup\n\n{group_list}', parse_mode='Markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='Markdown')
    raise events.StopPropagation
    
@client.on(events.NewMessage(pattern='\.cekspeed'))
async def check_speed(event):
    if is_admin(event.sender_id):
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
    if is_admin(event.sender_id):
        try:
            new_name = event.message.text.split(' ', 1)[1]
            await client(EditTitleRequest(event.chat_id, new_name))
            await event.respond(f'✅ Nama grup berhasil diubah menjadi: {new_name}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /setnamegroup <nama_baru>', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.kick'))
async def kick_member(event):
    if is_admin(event.sender_id):
        try:
            user_id = int(event.message.text.split(' ')[1])
            await client(EditBannedRequest(event.chat_id, user_id, ChatBannedRights(until_date=None, view_messages=True)))
            await event.respond(f'✅ Anggota berhasil di-kick dari grup ini', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /kick <user_id>', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.ban'))
async def ban_member(event):
    if is_admin(event.sender_id):
        try:
            user_id = int(event.message.text.split(' ')[1])
            await client(EditBannedRequest(event.chat_id, user_id, ChatBannedRights(until_date=None, view_messages=True)))
            await event.respond(f'✅ Anggota berhasil di-ban dari grup ini', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /ban <user_id>', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.unban'))
async def unban_member(event):
    if is_admin(event.sender_id):
        try:
            user_id = int(event.message.text.split(' ')[1])
            await client(EditBannedRequest(event.chat_id, user_id, ChatBannedRights(until_date=None, view_messages=False)))
            await event.respond(f'✅ Anggota berhasil di-unban dari grup ini', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /unban <user_id>', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.mute'))
async def mute_member(event):
    if is_admin(event.sender_id):
        try:
            user_id = int(event.message.text.split(' ')[1])
            await client(EditBannedRequest(event.chat_id, user_id, ChatBannedRights(until_date=None, send_messages=True)))
            await event.respond(f'✅ Pengguna {user_id} dimute di grup ini', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /mute <user_id>', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.join'))
async def join_group(event):
    if is_admin(event.sender_id):
        try:
            group_link = event.message.text.split(' ')[1]
            await client(JoinChannelRequest(group_link))
            await event.respond(f'✅ Berhasil bergabung ke grup: {group_link}', parse_mode='Markdown')
        except IndexError:
            await event.respond('⚠️ Gunakan format: /join <link_grup>', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.listmember'))
async def list_members(event):
    if is_admin(event.sender_id):
        try:
            group_id = event.chat_id
            group = await client.get_entity(group_id)
            members = []
            async for user in client.iter_participants(group):
                members.append(f'{user.id} - {user.first_name} {user.last_name or ""}')
            members_list = "\n".join(members)
            await event.respond(f'📋 Daftar anggota grup:\n\n{members_list}', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.muteall'))
async def mute_all(event):
    if is_admin(event.sender_id):
        try:
            group_id = event.chat_id
            group = await client.get_entity(group_id)
            async for user in client.iter_participants(group):
                await client(EditBannedRequest(group, user.id, ChatBannedRights(send_messages=True)))
            await event.respond('✅ Semua anggota telah di-mute.', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.unmuteall'))
async def unmute_all(event):
    if is_admin(event.sender_id):
        try:
            group_id = event.chat_id
            group = await client.get_entity(group_id)
            async for user in client.iter_participants(group):
                await client(EditBannedRequest(group, user.id, ChatBannedRights(send_messages=False)))
            await event.respond('✅ Semua anggota telah di-unmute.', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.member'))
async def add_group_member(event):
    if is_admin(event.sender_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            user = await client.get_entity(user_id)
            group = await client.get_entity(group_id)
            await client(InviteToChannelRequest(group, [user.id]))
            await event.respond(f'✅ Anggota {user_id} berhasil ditambahkan ke grup: {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /member <group_id> <user_id>', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.ChatAction)
async def welcome_or_farewell(event):
    if event.user_added or event.user_joined:
        await event.respond(f'👋 Selamat datang di grup, {event.user.first_name}!', parse_mode='Markdown')
    elif event.user_kicked or event.user_left:
        await event.respond(f'👋 Selamat tinggal, {event.user.first_name}.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='\.setfotogroup'))
async def set_group_photo(event):
    if is_admin(event.sender_id):
        if event.photo:
            try:
                photo = await event.download_media()
                file = await client.upload_file(photo)
                await client(EditPhotoRequest(event.chat_id, InputChatUploadedPhoto(file)))
                await event.respond(f'✅ Foto grup berhasil diubah', parse_mode='Markdown')
            except Exception as e:
                await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
        else:
            await event.respond('⚠️ Kirim perintah ini dengan foto yang ingin diatur sebagai foto grup', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.setadmin'))
async def set_admin(event):
    if is_admin(event.sender_id):
        try:
            user_id = int(event.message.text.split(' ')[1])
            rights = ChatAdminRights(add_admins=False, invite_users=True, change_info=True, ban_users=True, delete_messages=True, pin_messages=True)
            await client(EditAdminRequest(event.chat_id, user_id, rights))
            await event.respond(f'✅ Pengguna {user_id} telah diangkat menjadi admin', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /setadmin <user_id>', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='\.deladmin'))
async def del_admin(event):
    if is_admin(event.sender_id):
        try:
            user_id = int(event.message.text.split(' ')[1])
            rights = ChatAdminRights(add_admins=False, invite_users=False, change_info=False, ban_users=False, delete_messages=False, pin_messages=False)
            await client(EditAdminRequest(event.chat_id, user_id, rights))
            await event.respond(f'✅ Pengguna {user_id} telah dicabut hak adminnya', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ Gunakan format: /deladmin <user_id>', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'❌ Terjadi kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('❌ Anda tidak memiliki akses untuk menggunakan bot ini', parse_mode='Markdown')
    raise events.StopPropagation

client.start()
client.run_until_disconnected()
