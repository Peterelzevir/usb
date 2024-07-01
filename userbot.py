import logging
import time
import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetAllChats
from telethon.tl.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument, InputMediaGif, InputMediaAudio

logging.basicConfig(level=logging.INFO)

# Masukkan string session Anda
string_session = '1BVtsOGcBuyhbhUbKGA1M09zrT9e4XpDCnv1_xs_24nYGMuNyGgEhzNYERCwiHM9Z2ViLegoWwGgRfKuIsZ-NZ84KNLMZS-wNfO8ERF6lhqHY0Qoxg7bPNlAL5aKuEWMLPJTXptBaSi_Glcihem_7FmrVgLhbwQwQSKKri5UeM-GN-Fy6s1qaVRg5KX-rw-4-2nEHEObwlpVXPbiuIzwGfCi-5zKlc9EZuHtHOTxzrjy02jOgika3D4VuEIBaTewJNpmAdorV0tWTb6-V1MPEQMGo_4kQzAi_Wkxqn5ASZgQJzH3SexjOzJ3LAjK36sQwP4zha5zJ8S5ZEST8Hl9pDW_MpZkinYM='
client = TelegramClient('session_name', api_id=None, api_hash=None).start(bot_token=string_session)

forward_list = []  # List pesan yang akan di forward
delay_settings = 60  # Default delay dalam detik
is_forwarding = False  # Status forwarding

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Halo! Saya adalah userbot Telegram.')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/help'))
async def help(event):
    help_text = (
        'Berikut adalah perintah yang tersedia:\n'
        '/start - Mulai bot\n'
        '/help - Bantuan\n'
        '/addforward - Tambah pesan untuk di forward\n'
        '/delforward - Hapus pesan dari daftar forward\n'
        '/setdelay - Atur delay pengiriman pesan\n'
        '/checklist - Lihat daftar pesan yang di forward\n'
        '/groups - Lihat grup yang diikuti bot\n'
        '/checkspeed - Cek kecepatan pengiriman bot\n'
        '/mulai - Mulai mengirim pesan otomatis\n'
        '/stop - Hentikan pengiriman pesan otomatis'
    )
    await event.respond(help_text)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/addforward'))
async def add_forward(event):
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        forward_list.append(reply_message)
        await event.respond(f'Pesan ditambahkan ke daftar forward: {reply_message.text or "Media"}')
    else:
        await event.respond('Balas ke pesan yang ingin ditambahkan ke daftar forward.')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/delforward'))
async def del_forward(event):
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        if reply_message in forward_list:
            forward_list.remove(reply_message)
            await event.respond(f'Pesan dihapus dari daftar forward: {reply_message.text or "Media"}')
        else:
            await event.respond('Pesan tidak ditemukan dalam daftar forward.')
    else:
        await event.respond('Balas ke pesan yang ingin dihapus dari daftar forward.')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/setdelay'))
async def set_delay(event):
    global delay_settings
    try:
        delay = int(event.message.message.split(' ')[1])
        delay_settings = delay
        await event.respond(f'Delay pengiriman pesan diatur ke {delay} detik.')
    except (IndexError, ValueError):
        await event.respond('Gunakan format: /setdelay [detik]')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/checklist'))
async def check_list(event):
    if forward_list:
        response = 'Daftar pesan yang akan di forward:\n' + '\n'.join([f'{msg.text or "Media"}' for msg in forward_list])
    else:
        response = 'Tidak ada pesan dalam daftar forward.'
    await event.respond(response)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/groups'))
async def list_groups(event):
    result = await client(GetAllChats([]))
    groups = [dialog.title for dialog in result.chats if getattr(dialog, 'megagroup', False)]
    response = 'Grup yang diikuti bot:\n' + '\n'.join(groups)
    await event.respond(response)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/checkspeed'))
async def check_speed(event):
    start_time = time.time()
    await event.respond('Mengukur kecepatan...')
    end_time = time.time()
    response = f'Kecepatan pengiriman bot: {end_time - start_time:.2f} detik.'
    await event.respond(response)
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/mulai'))
async def mulai(event):
    global is_forwarding
    is_forwarding = True
    await event.respond('Pengiriman pesan otomatis dimulai.')
    raise events.StopPropagation

@client.on(events.NewMessage(pattern='/stop'))
async def stop(event):
    global is_forwarding
    is_forwarding = False
    await event.respond('Pengiriman pesan otomatis dihentikan.')
    raise events.StopPropagation

async def forward_messages():
    while True:
        if is_forwarding and forward_list:
            result = await client(GetAllChats([]))
            groups = [dialog for dialog in result.chats if getattr(dialog, 'megagroup', False)]
            for group in groups:
                for msg in forward_list:
                    if msg.photo:
                        await client.send_file(group, msg.photo, caption=msg.text)
                    elif msg.video:
                        await client.send_file(group, msg.video, caption=msg.text)
                    elif msg.document:
                        await client.send_file(group, msg.document, caption=msg.text)
                    elif msg.gif:
                        await client.send_file(group, msg.gif, caption=msg.text)
                    elif msg.audio:
                        await client.send_file(group, msg.audio, caption=msg.text)
                    else:
                        await client.send_message(group, msg.text)
                    await asyncio.sleep(delay_settings)
        await asyncio.sleep(1)

async def main():
    await client.start()
    client.loop.create_task(forward_messages())
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
