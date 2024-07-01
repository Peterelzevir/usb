import logging
import time
import asyncio
import sqlite3
import json
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest, EditBannedRequest, EditTitleRequest
from telethon.tl.types import ChatBannedRights

logging.basicConfig(level=logging.INFO)

api_id = '28356794'  # ganti api id mu
api_hash = 'a581331dabc5d4b7e0c7381a97dde824'  # ganti dengan api_hash mu
string_session = '1BVtsOGcBu5uEA0k29aCSrBvDPXZ8WXHIGdwp2chGoIw6GLDwZLBDnPu6xH7ocvb1pASn3sCHRUZZ_mo4oKrVvdMGdJ6zY2srwbmmENO97drhEYAW8AOknk-O5Gqvxs6j4xQQnQ8KrpBSK-xCoKUUIDl7rFG9yHawzs5KfqUXh1b8pPpPO8j6dAvWNARpLMOLa_qt7I46QZcgRjbxFa6rMpOutgiBObv24v93Hyefd0uWhhFuObb9ORgovcfVuJy5VGUsdmhlngv1jz-Vk8HqmNaKSM73kvgctbeIFXVbwnqRdPkYLVA49q_0d6YubcFnrqazkPwtlJxxY57CedOUfoO72G67DCc='  # string session telethon mu
admin_id = '5988451717'  # ganti dengan id admin yg kamu mau

client = TelegramClient(StringSession(string_session), api_id, api_hash)
clone_clients = {}

# Database setup
def init_db():
    conn = sqlite3.connect('userbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clones (user_id INTEGER PRIMARY KEY, api_id TEXT, api_hash TEXT, string_session TEXT, admin_id TEXT)''')
    conn.commit()
    conn.close()

init_db()

forward_list_file = 'forward_list.json'  # jgn di ganti
delay_settings = 60  # default
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

async def create_clone(api_id, api_hash, string_session, admin_id):
    clone_client = TelegramClient(StringSession(string_session), api_id, api_hash)
    await clone_client.start()
    clone_clients[admin_id] = clone_client
    return clone_client

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id == int(admin_id):
        await event.respond('Halo kak Saya adalah userbot Telegram\n\n➡️ /help untuk lebih lengkap', parse_mode='Markdown')
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
        await event.respond('Siapkan informasi berikut untuk kloning:\n1. API ID\n2. API Hash\n3. String Session\n4. Admin ID', buttons=buttons, parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addclone'))
async def add_clone(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 5:
            _, api_id, api_hash, string_session, admin_id = params
            clone_client = await create_clone(api_id, api_hash, string_session, admin_id)
            with sqlite3.connect('userbot.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO clones (api_id, api_hash, string_session, admin_id) VALUES (?, ?, ?, ?)", (api_id, api_hash, string_session, admin_id))
                conn.commit()
            await event.respond('Userbot kloning berhasil dibuat.', parse_mode='Markdown')
        else:
            await event.respond('Format salah! Gunakan: /addclone [API_ID] [API_HASH] [STRING_SESSION] [ADMIN_ID]', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    if event.sender_id == int(admin_id):
        buttons = [
            [Button.inline("Fitur Bot", b"features")],
            [Button.inline("Kembali", b"back")]
        ]
        await event.respond('Pilih untuk melihat fitur atau kembali ke menu utama:', buttons=buttons, parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.CallbackQuery(data=b"features"))
async def show_features(event):
    features_text = (
        'Berikut adalah perintah yang tersedia:\n\n'
        '/start - Mulai bot\n'
        '/help - Bantuan\n'
        '/bantuan - Bantuan\n'
        '/clone - Siapkan kloning userbot\n'
        '/addclone [API_ID] [API_HASH] [STRING_SESSION] [ADMIN_ID] - Tambah userbot kloning\n'
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
        '/stop - Hentikan pengiriman pesan otomatis'
    )
    buttons = [
        [Button.inline("Kembali", b"back")]
    ]
    await event.edit(features_text, buttons=buttons, parse_mode='Markdown')

@client.on(events.CallbackQuery(data=b"back"))
async def back_to_help(event):
    buttons = [
        [Button.inline("Fitur Bot", b"features")],
        [Button.inline("Kembali", b"back")]
    ]
    await event.edit('Pilih untuk melihat fitur atau kembali ke menu utama:', buttons=buttons, parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/addforward'))
async def add_forward(event):
    if event.sender_id == int(admin_id):
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
            forward_list.append({
                'text': reply_message.text,
                'media': reply_message.media,
                'entities': reply_message.entities
            })
            save_forward_list(forward_list)
            await event.respond(f'Pesan ditambahkan ke daftar forward:\n\n{reply_message.text or "Media"}', parse_mode='Markdown')
        else:
            await event.respond('Balas ke pesan yang ingin ditambahkan ke daftar forward.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/delforward'))
async def del_forward(event):
    if event.sender_id == int(admin_id):
        try:
            index = int(event.message.text.split(' ')[1]) - 1
            if 0 <= index < len(forward_list):
                removed_item = forward_list.pop(index)
                save_forward_list(forward_list)
                await event.respond(f'Pesan berhasil dihapus dari daftar forward:\n\n{removed_item["text"] or "Media"}', parse_mode='Markdown')
            else:
                await event.respond('Indeks tidak valid.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /delforward [index]', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/checklist'))
async def checklist(event):
    if event.sender_id == int(admin_id):
        if forward_list:
            checklist_message = 'Daftar Pesan Forward:\n\n'
            for i, item in enumerate(forward_list, start=1):
                checklist_message += f'{i}. {"Media" if item["media"] else item["text"]}\n'
            await event.respond(checklist_message, parse_mode='Markdown')
        else:
            await event.respond('Daftar forward kosong.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/setdelay'))
async def set_delay(event):
    if event.sender_id == int(admin_id):
        try:
            global delay_settings
            delay_settings = int(event.message.text.split(' ')[1])
            await event.respond(f'Delay pengiriman pesan diatur ke {delay_settings} detik.', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /setdelay [detik]', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/mulai'))
async def mulai(event):
    global is_forwarding
    if event.sender_id == int(admin_id):
        if is_forwarding:
            await event.respond('Pengiriman pesan otomatis sudah berjalan.', parse_mode='Markdown')
        else:
            is_forwarding = True
            await event.respond(f'Mulai mengirim pesan dengan delay {delay_settings} detik.', parse_mode='Markdown')
            while is_forwarding:
                for item in forward_list:
                    for dialog in await client.get_dialogs():
                        if dialog.is_group or dialog.is_channel:
                            try:
                                if item["media"]:
                                    await client.send_file(dialog.id, item["media"], caption=item["text"], entities=item["entities"])
                                else:
                                    await client.send_message(dialog.id, item["text"], entities=item["entities"])
                                await asyncio.sleep(delay_settings)
                            except Exception as e:
                                logging.error(f'Error sending message to {dialog.name}: {e}')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')

@client.on(events.NewMessage(pattern='/stop'))
async def stop(event):
    global is_forwarding
    if event.sender_id == int(admin_id):
        is_forwarding = False
        await event.respond('Pengiriman pesan otomatis dihentikan.', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/checkspeed'))
async def check_speed(event):
    if event.sender_id == int(admin_id):
        start_time = time.time()
        await event.respond('Mengukur kecepatan...')
        end_time = time.time()
        speed = end_time - start_time
        await event.respond(f'Kecepatan bot: {speed:.2f} detik', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/groups'))
async def list_groups(event):
    if event.sender_id == int(admin_id):
        dialogs = await client.get_dialogs()
        group_list = 'Grup yang diikuti:\n\n'
        for dialog in dialogs:
            if dialog.is_group or dialog.is_channel:
                group_list += f'{dialog.id} - {dialog.name}\n'
        await event.respond(group_list, parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/join'))
async def join_group(event):
    if event.sender_id == int(admin_id):
        try:
            group = event.message.text.split(' ')[1]
            await client(JoinChannelRequest(group))
            await event.respond(f'Berhasil bergabung dengan grup: {group}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /join [GROUP_OR_CHANNEL]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Error: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/setname'))
async def set_group_name(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ', 2)
            group_id = int(params[1])
            new_name = params[2]
            await client(EditTitleRequest(group_id, new_name))
            await event.respond(f'Nama grup diubah menjadi: {new_name}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /setname [GROUP_ID] [NEW_NAME]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Error: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addmember'))
async def add_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, view_messages=False)))
            await event.respond(f'Anggota dengan ID {user_id} telah ditambahkan ke grup {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /addmember [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Error: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/kick'))
async def kick_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, view_messages=True)))
            await event.respond(f'Anggota dengan ID {user_id} telah di-kick dari grup {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /kick [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Error: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/ban'))
async def ban_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, view_messages=True)))
            await event.respond(f'Anggota dengan ID {user_id} telah di-ban dari grup {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /ban [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Error: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/unban'))
async def unban_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, view_messages=False)))
            await event.respond(f'Anggota dengan ID {user_id} telah di-unban dari grup {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /unban [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Error: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/mute'))
async def mute_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, send_messages=True)))
            await event.respond(f'Anggota dengan ID {user_id} telah di-mute di grup {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /mute [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Error: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/unmute'))
async def unmute_member(event):
    if event.sender_id == int(admin_id):
        try:
            params = event.message.text.split(' ')
            group_id = int(params[1])
            user_id = int(params[2])
            await client(EditBannedRequest(group_id, user_id, ChatBannedRights(until_date=None, send_messages=False)))
            await event.respond(f'Anggota dengan ID {user_id} telah di-unmute di grup {group_id}', parse_mode='Markdown')
        except (IndexError, ValueError):
            await event.respond('Gunakan format: /unmute [GROUP_ID] [USER_ID]', parse_mode='Markdown')
        except Exception as e:
            await event.respond(f'Error: {str(e)}', parse_mode='Markdown')
    else:
        await event.respond('Anda tidak memiliki akses untuk menggunakan bot ini.', parse_mode='Markdown')
    raise events.StopPropagation

async def main():
    async with client:
        await client.run_until_disconnected()

if __name__ == '__main__':
    client.loop.run_until_complete(main())
