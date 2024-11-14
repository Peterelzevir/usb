from pyrogram import Client, filters
import random

app = Client("my_userbot")

# Command /ping
@app.on_message(filters.command("ping"))
async def ping(client, message):
    start_time = message.date
    end_time = message.edit_date if message.edit_date else start_time
    latency = (end_time - start_time).microseconds / 1000  # Convert to milliseconds
    await message.reply_text(f"Pong! Bot response time: {latency:.2f} ms")

# Command /admin
@app.on_message(filters.command("admin"))
async def admin(client, message):
    await message.reply_text("Hubungi admin di t.me/hiyaok")

# Command /send (pesan)
@app.on_message(filters.command("send"))
async def send_message(client, message):
    if len(message.command) < 2:
        await message.reply_text("Harap masukkan pesan yang ingin dikirim. Contoh: /send Halo!")
        return
    
    text_to_send = message.text.split(" ", 1)[1]
    contacts = await client.get_contacts()  # Mengambil daftar kontak
    random_contacts = random.sample(contacts, min(5, len(contacts)))  # Memilih 5 kontak acak

    for contact in random_contacts:
        try:
            await client.send_message(contact.user_id, text_to_send)
        except Exception as e:
            print(f"Error sending to {contact.user_id}: {e}")

    await message.reply_text(f"Pesan telah dikirim ke {len(random_contacts)} kontak.")
