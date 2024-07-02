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
from telethon import Button
from telethon.sessions import StringSession
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.tl.custom import Button

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
        await event.respond('Halo, saya adalah userbot Telegram.\n\n➡️ /help untuk melihat fitur lengkap.', parse_mode='Markdown')
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
            parse_mode='Markdown'
        )
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addforward'))
async def add_forward(event):
    if event.sender_id == int(admin_id):
        if event.reply_to_msg_id:
            reply_msg = await event.get_reply_message()
            caption = reply_msg.text if reply_msg.text else None
            if reply_msg.media:
                forward_item = {
                    'id': reply_msg.id,
                    'message': reply_msg.text if reply_msg.text else '',
                    'media': reply_msg.media,
                    'caption': caption if caption else '',
                    'delay': delay_settings  # Default delay
                }
                forward_list.append(forward_item)
                save_forward_list(forward_list)
                await event.respond('Pesan telah ditambahkan untuk di-forward.', parse_mode='Markdown')
            else:
                await event.respond('Balas pesan media yang ingin Anda tambahkan ke daftar forward.', parse_mode='Markdown')
        else:
            await event.respond('Balas pesan yang ingin Anda tambahkan ke daftar forward.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

def save_forward_list(forward_list):
    with open('forward_list.json', 'w', encoding='utf-8') as file:
        json.dump(forward_list, file, ensure_ascii=False, indent=4)

def load_forward_list():
    try:
        with open('forward_list.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

forward_list = load_forward_list()

@client.on(events.NewMessage(pattern='/delforward'))
async def del_forward(event):
    if event.sender_id == int(admin_id):
        try:
            index = int(event.message.text.split()[1]) - 1
            if 0 <= index < len(forward_list):
                del forward_list[index]
                save_forward_list(forward_list)
                await event.respond('Pesan telah dihapus dari daftar forward.', parse_mode='Markdown')
            else:
                await event.respond('Index pesan tidak valid.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Format salah! Gunakan: /delforward [INDEX]', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/setdelay'))
async def set_delay(event):
    global delay_settings
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split()
            index = int(params[1]) - 1  # Ambil indeks pesan dari input pengguna
            new_delay = int(params[2])  # Ambil delay baru dari input pengguna
            if 0 <= index < len(forward_list):
                forward_list[index]['delay'] = new_delay  # Atur delay baru untuk pesan dengan indeks tertentu
                save_forward_list(forward_list)
                await event.respond(f'Delay pengiriman pesan dengan indeks {index + 1} diatur ke {new_delay} detik.', parse_mode='Markdown')
            else:
                await event.respond('Index pesan tidak valid.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Format salah! Gunakan: /setdelay [INDEX] [DELAY_IN_SECONDS]', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation


@client.on(events.NewMessage(pattern='/checklist'))
async def check_list(event):
    if event.sender_id == int(admin_id):
        if forward_list:
            message = 'Daftar pesan untuk di forward:\n\n'
            for idx, item in enumerate(forward_list, start=1):
                message += f"{idx}. Pesan: {item['message']}\n   Media: {bool(item['media'])}\n   Caption: {item['caption']}\n   Delay: {item['delay']} detik\n\n"
            await event.respond(message, parse_mode='Markdown')
        else:
            await event.respond('Daftar pesan untuk di forward masih kosong.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/groups'))
async def list_groups(event):
    if event.sender_id == int(admin_id):
        groups = await client.get_dialogs()
        groups_text = 'Grup yang diikuti bot:\n\n'
        for dialog in groups:
            if dialog.is_group:
                groups_text += f"- {dialog.name} ({dialog.id})\n"
        await event.respond(groups_text, parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/checkspeed'))
async def check_speed(event):
    if event.sender_id == int(admin_id):
        start_time = time.time()
        await event.respond('Menghitung kecepatan pengiriman...')
        end_time = time.time()
        response_time = end_time - start_time
        await event.respond(f'Kecepatan pengiriman bot: {response_time} detik.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/join'))
async def join_group(event):
    if event.sender_id == int(admin_id):
        try:
            chat_id = event.message.text.split()[1]
            await client.join_group(chat_id)
            await event.respond(f'Bergabung ke grup dengan ID: {chat_id}.', parse_mode='Markdown')
        except IndexError:
            await event.respond('Format salah! Gunakan: /join [GROUP_OR_CHANNEL_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Gagal bergabung ke grup dengan pesan kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/setname'))
async def set_group_name(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split()
            group_id = int(params[1])
            new_name = ' '.join(params[2:])
            await client.edit_group(group_id, title=new_name)
            await event.respond(f'Nama grup dengan ID {group_id} telah diubah menjadi: {new_name}.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Format salah! Gunakan: /setname [GROUP_ID] [NEW_NAME]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Gagal mengubah nama grup dengan pesan kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addmember'))
async def add_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split()
            group_id = int(params[1])
            user_id = int(params[2])
            await client.add_chat_members(group_id, users=user_id)
            await event.respond(f'Anggota dengan ID {user_id} telah ditambahkan ke grup dengan ID {group_id}.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Format salah! Gunakan: /addmember [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Gagal menambahkan anggota ke grup dengan pesan kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/kick'))
async def kick_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split()
            group_id = int(params[1])
            user_id = int(params[2])
            await client.kick_chat_members(group_id, users=user_id)
            await event.respond(f'Anggota dengan ID {user_id} telah dikeluarkan dari grup dengan ID {group_id}.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Format salah! Gunakan: /kick [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Gagal mengeluarkan anggota dari grup dengan pesan kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/ban'))
async def ban_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split()
            group_id = int(params[1])
            user_id = int(params[2])
            await client.edit_permissions(group_id, user_id, view_messages=False)
            await event.respond(f'Anggota dengan ID {user_id} telah diban dari grup dengan ID {group_id}.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Format salah! Gunakan: /ban [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Gagal memban anggota dari grup dengan pesan kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/unban'))
async def unban_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split()
            group_id = int(params[1])
            user_id = int(params[2])
            await client.edit_permissions(group_id, user_id, view_messages=True)
            await event.respond(f'Anggota dengan ID {user_id} telah di-unban dari grup dengan ID {group_id}.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Format salah! Gunakan: /unban [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Gagal meng-unban anggota dari grup dengan pesan kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/mute'))
async def mute_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split()
            group_id = int(params[1])
            user_id = int(params[2])
            await client.edit_permissions(group_id, user_id, send_messages=False)
            await event.respond(f'Anggota dengan ID {user_id} telah dimute di grup dengan ID {group_id}.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Format salah! Gunakan: /mute [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Gagal memute anggota di grup dengan pesan kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/unmute'))
async def unmute_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split()
            group_id = int(params[1])
            user_id = int(params[2])
            await client.edit_permissions(group_id, user_id, send_messages=True)
            await event.respond(f'Anggota dengan ID {user_id} telah di-unmute di grup dengan ID {group_id}.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Format salah! Gunakan: /unmute [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Gagal meng-unmute anggota di grup dengan pesan kesalahan: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/mulai'))
async def start_forward(event):
    if event.sender_id == int(admin_id):
        async def forward_messages():
            while True:
                for item in forward_list:
                    for group in await client.get_dialogs():
                        if group.is_group:
                            if item['media']:
                                await client.send_file(group, item['media'], caption=item['caption'])
                            else:
                                await client.send_message(group, item['message'], parse_mode='Markdown')
                            await asyncio.sleep(item['delay'])
        asyncio.create_task(forward_messages())
        await event.respond('Pengiriman pesan ke seluruh grup telah dimulai.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/stop'))
async def stop_forward(event):
    if event.sender_id == int(admin_id):
        for task in asyncio.all_tasks():
            if task.get_name() == 'forward_messages':
                task.cancel()
        await event.respond('Pengiriman pesan ke seluruh grup telah dihentikan.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/listclone'))
async def list_clone(event):
    if event.sender_id == int(admin_id):
        with sqlite3.connect('userbot.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM clones")
            clones = c.fetchall()

        if clones:
            message = 'Daftar kloning userbot:\n\n'
            for clone in clones:
                message += (
                    f"API ID: {clone[1]}\n"
                    f"API Hash: {clone[2]}\n"
                    f"String Session: {clone[3]}\n"
                    f"Admin ID: {clone[4]}\n"
                    f"Expiry Date: {clone[5]}\n\n"
                )
            await event.respond(message, parse_mode='Markdown')
        else:
            await event.respond('Tidak ada kloning userbot yang aktif saat ini.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

async def forward_messages():
    global is_forwarding
    while is_forwarding:
        for message_info in forward_list:
            message_id = message_info['id']
            delay = message_info['delay']

            try:
                if 'media' in message_info and message_info['media']:
                    if isinstance(message_info['media'], MessageMediaPhoto):
                        await client.send_message(admin_id, file=message_info['media'], caption=message_info['caption'])
                    elif isinstance(message_info['media'], MessageMediaDocument):
                        await client.send_file(admin_id, file=message_info['media'], caption=message_info['caption'])
                else:
                    await client.send_message(admin_id, message_info['message'])

                await asyncio.sleep(delay)
            except Exception as e:
                logging.error(f'Gagal mengirim pesan: {str(e)}')
        
        # Reset delay_settings to default
        delay_settings = 60

    logging.info('Pengiriman pesan otomatis dihentikan.')

async def main():
    await client.start()
    logging.info("Bot Telegram berjalan. Tekan Ctrl+C untuk berhenti.")
    client.loop.create_task(check_expiry())
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
