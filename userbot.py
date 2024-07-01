import logging
import time
import asyncio
import sqlite3
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest, EditBannedRequest, EditTitleRequest
from telethon.tl.types import ChatBannedRights

logging.basicConfig(level=logging.INFO)

# Replace these with your actual API ID and hash
api_id = '28356794'
api_hash = 'a581331dabc5d4b7e0c7381a97dde824'

# Replace with your actual string session
string_session = '1BVtsOGcBu5uEA0k29aCSrBvDPXZ8WXHIGdwp2chGoIw6GLDwZLBDnPu6xH7ocvb1pASn3sCHRUZZ_mo4oKrVvdMGdJ6zY2srwbmmENO97drhEYAW8AOknk-O5Gqvxs6j4xQQnQ8KrpBSK-xCoKUUIDl7rFG9yHawzs5KfqUXh1b8pPpPO8j6dAvWNARpLMOLa_qt7I46QZcgRjbxFa6rMpOutgiBObv24v93Hyefd0uWhhFuObb9ORgovcfVuJy5VGUsdmhlngv1jz-Vk8HqmNaKSM73kvgctbeIFXVbwnqRdPkYLVA49q_0d6YubcFnrqazkPwtlJxxY57CedOUfoO72G67DCc='
admin_id = '5988451717'

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

forward_list = []  # List pesan yang akan di forward
delay_settings = 60  # Default delay dalam detik
is_forwarding = False  # Status forwarding

async def create_clone(api_id, api_hash, string_session, admin_id):
    clone_client = TelegramClient(StringSession(string_session), api_id, api_hash)
    await clone_client.start()
    clone_clients[admin_id] = clone_client
    return clone_client

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    if event.sender_id == int(admin_id):
        await event.respond('👋 *Halo! Saya adalah userbot Telegram.*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/clone'))
async def clone(event):
    if event.sender_id == int(admin_id):
        buttons = [
            [Button.text("📲 API ID"), Button.text("🔑 API Hash")],
            [Button.text("🔒 String Session"), Button.text("👤 Admin ID")]
        ]
        await event.respond('🔧 *Siapkan informasi berikut untuk kloning:*\n1. API ID\n2. API Hash\n3. String Session\n4. Admin ID', buttons=buttons, parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
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
            await event.respond('✅ *Userbot kloning berhasil dibuat.*', parse_mode='markdown')
        else:
            await event.respond('❌ *Format salah! Gunakan: /addclone [API_ID] [API_HASH] [STRING_SESSION] [ADMIN_ID]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    if event.sender_id == int(admin_id):
        help_text = (
            '🛠 *Berikut adalah perintah yang tersedia:*\n\n'
            '/start - Mulai bot\n'
            '/help - Bantuan\n'
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
        await event.respond(help_text, parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addforward'))
async def add_forward(event):
    if event.sender_id == int(admin_id):
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
            forward_list.append(reply_message)
            await event.respond(f'✅ *Pesan ditambahkan ke daftar forward:*\n\n```{reply_message.text or "Media"}```', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Balas ke pesan yang ingin ditambahkan ke daftar forward.*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/delforward'))
async def del_forward(event):
    if event.sender_id == int(admin_id):
        if event.reply_to_msg_id:
            reply_message = await event.get_reply_message()
            if reply_message in forward_list:
                forward_list.remove(reply_message)
                await event.respond(f'✅ *Pesan dihapus dari daftar forward:*\n\n```{reply_message.text or "Media"}```', parse_mode='markdown')
            else:
                await event.respond('⚠️ *Pesan tidak ditemukan dalam daftar forward.*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Balas ke pesan yang ingin dihapus dari daftar forward.*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/setdelay'))
async def set_delay(event):
    if event.sender_id == int(admin_id):
        global delay_settings
        try:
            delay = int(event.message.message.split(' ')[1])
            delay_settings = delay
            await event.respond(f'⏱ *Delay pengiriman pesan diatur ke* `{delay}` *detik.*', parse_mode='markdown')
        except (IndexError, ValueError):
            await event.respond('⚠️ *Gunakan format: /setdelay [detik]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/checklist'))
async def check_list(event):
    if event.sender_id == int(admin_id):
        if forward_list:
            response = '📋 *Daftar pesan yang akan di forward:*\n\n' + '\n'.join([f'```{msg.text or "Media"}```' for msg in forward_list])
        else:
            response = '⚠️ *Tidak ada pesan dalam daftar forward.*'
        await event.respond(response, parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/groups'))
async def list_groups(event):
    if event.sender_id == int(admin_id):
        response = '👥 *Grup yang diikuti bot:*\n\n'
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                response += f'• **{dialog.name}** - `{dialog.id}`\n'
        await event.respond(response, parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addgroup'))
async def add_group(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 2:
            group_id = int(params[1])
            try:
                await client(functions.messages.AddChatUserRequest(
                    chat_id=group_id,
                    user_id=event.sender_id,
                    fwd_limit=10
                ))
                await event.respond(f'✅ *Berhasil menambahkan ke grup* `{group_id}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal menambahkan ke grup: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /addgroup [GROUP_ID]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/removegroup'))
async def remove_group(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 2:
            group_id = int(params[1])
            try:
                await client(functions.messages.DeleteChatUserRequest(
                    chat_id=group_id,
                    user_id=event.sender_id
                ))
                await event.respond(f'✅ *Berhasil dihapus dari grup* `{group_id}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal menghapus dari grup: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /removegroup [GROUP_ID]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/checkspeed'))
async def check_speed(event):
    if event.sender_id == int(admin_id):
        start_time = time.time()
        await event.respond('🏎 *Mengukur kecepatan...*', parse_mode='markdown')
        end_time = time.time()
        response = f'⚡️ *Kecepatan pengiriman bot: {end_time - start_time:.2f} detik.*'
        await event.respond(response, parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/mulai'))
async def mulai(event):
    if event.sender_id == int(admin_id):
        global is_forwarding
        is_forwarding = True
        await event.respond('▶️ *Pengiriman pesan otomatis dimulai.*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/stop'))
async def stop(event):
    if event.sender_id == int(admin_id):
        global is_forwarding
        is_forwarding = False
        await event.respond('⏹️ *Pengiriman pesan otomatis dihentikan.*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/join'))
async def join_group(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 2:
            group_link = params[1]
            try:
                await client(JoinChannelRequest(group_link))
                await event.respond(f'✅ *Berhasil join ke grup/channel* `{group_link}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal join ke grup/channel: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /join [GROUP_OR_CHANNEL_LINK]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/setname'))
async def set_group_name(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) >= 3:
            group_id = int(params[1])
            new_name = ' '.join(params[2:])
            try:
                await client(EditTitleRequest(channel=group_id, title=new_name))
                await event.respond(f'✅ *Nama grup berhasil diubah menjadi* `{new_name}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal mengubah nama grup: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /setname [GROUP_ID] [NEW_NAME]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addmember'))
async def add_member(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 3:
            group_id = int(params[1])
            user_id = int(params[2])
            try:
                await client(functions.channels.InviteToChannelRequest(channel=group_id, users=[user_id]))
                await event.respond(f'✅ *Anggota berhasil ditambahkan ke grup* `{group_id}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal menambahkan anggota ke grup: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /addmember [GROUP_ID] [USER_ID]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/kick'))
async def kick_member(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 3:
            group_id = int(params[1])
            user_id = int(params[2])
            try:
                await client(EditBannedRequest(channel=group_id, user_id=user_id, banned_rights=ChatBannedRights(until_date=None, view_messages=True)))
                await event.respond(f'✅ *Anggota berhasil di-kick dari grup* `{group_id}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal meng-kick anggota dari grup: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /kick [GROUP_ID] [USER_ID]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/ban'))
async def ban_member(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 3:
            group_id = int(params[1])
            user_id = int(params[2])
            try:
                await client(EditBannedRequest(channel=group_id, user_id=user_id, banned_rights=ChatBannedRights(until_date=None, view_messages=True)))
                await event.respond(f'✅ *Anggota berhasil di-ban dari grup* `{group_id}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal mem-ban anggota dari grup: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /ban [GROUP_ID] [USER_ID]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/unban'))
async def unban_member(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 3:
            group_id = int(params[1])
            user_id = int(params[2])
            try:
                await client(EditBannedRequest(channel=group_id, user_id=user_id, banned_rights=ChatBannedRights(until_date=None, view_messages=False)))
                await event.respond(f'✅ *Anggota berhasil di-unban dari grup* `{group_id}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal meng-unban anggota dari grup: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /unban [GROUP_ID] [USER_ID]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/mute'))
async def mute_member(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 3:
            group_id = int(params[1])
            user_id = int(params[2])
            try:
                await client(EditBannedRequest(channel=group_id, user_id=user_id, banned_rights=ChatBannedRights(until_date=None, send_messages=True)))
                await event.respond(f'✅ *Anggota berhasil di-mute di grup* `{group_id}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal mem-mute anggota di grup: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /mute [GROUP_ID] [USER_ID]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/unmute'))
async def unmute_member(event):
    if event.sender_id == int(admin_id):
        params = event.message.text.split()
        if len(params) == 3:
            group_id = int(params[1])
            user_id = int(params[2])
            try:
                await client(EditBannedRequest(channel=group_id, user_id=user_id, banned_rights=ChatBannedRights(until_date=None, send_messages=False)))
                await event.respond(f'✅ *Anggota berhasil di-unmute di grup* `{group_id}`.', parse_mode='markdown')
            except Exception as e:
                await event.respond(f'❌ *Gagal meng-unmute anggota di grup: {e}*', parse_mode='markdown')
        else:
            await event.respond('⚠️ *Gunakan format: /unmute [GROUP_ID] [USER_ID]*', parse_mode='markdown')
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

async def auto_forward():
    while True:
        if is_forwarding:
            for msg in forward_list:
                async for dialog in client.iter_dialogs():
                    if dialog.is_group:
                        await client.send_message(dialog.id, msg)
                        await asyncio.sleep(delay_settings)
        await asyncio.sleep(1)

@client.on(events.NewMessage(pattern='/forward'))
async def start_forward(event):
    if event.sender_id == int(admin_id):
        await event.respond('▶️ *Pengiriman pesan otomatis dimulai.*', parse_mode='markdown')
        await auto_forward()
    else:
        await event.respond('❌ *Anda tidak memiliki akses untuk menggunakan bot ini.*', parse_mode='markdown')
    raise events.StopPropagation

client.start()
client.run_until_disconnected()
