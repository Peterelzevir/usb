import os
import asyncio
import random
import getpass
from telethon import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, UserPrivacyRestrictedError
from colorama import init, Fore, Style
import json
import logging

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format=f'{Fore.CYAN}[%(levelname)s]{Style.RESET_ALL} %(message)s',
    handlers=[
        logging.FileHandler("invite_log.txt"),
        logging.StreamHandler()
    ]
)

init(autoreset=True)

class SmartInviteManager:
    @staticmethod
    async def smart_invite(client, source_entity, dest_entity, members, max_invites=100):
        """
        Metode invite cerdas dengan berbagai strategi anti-limit
        """
        eligible_members = [
            member for member in members
            if not member.bot and member.access_hash and member.status
        ]

        random.shuffle(eligible_members)
        invited_members = eligible_members[:max_invites]
        
        total_invited = 0
        errors = {'flood': 0, 'privacy': 0, 'other': 0}

        for member in invited_members:
            try:
                await asyncio.sleep(random.uniform(3, 7))  # Delay antara undangan
                await client(InviteToChannelRequest(dest_entity, [member]))
                total_invited += 1
                logging.info(f"{Fore.GREEN}Invited: {member.username or member.first_name}{Style.RESET_ALL}")

                if total_invited % 10 == 0:
                    await asyncio.sleep(random.uniform(10, 20))  # Tambah delay setelah 10 undangan

            except FloodWaitError as e:
                errors['flood'] += 1
                logging.warning(f"{Fore.RED}Flood wait for {e.seconds} seconds{Style.RESET_ALL}")
                await asyncio.sleep(e.seconds + 10)
            except UserPrivacyRestrictedError:
                errors['privacy'] += 1
                logging.warning(f"{Fore.YELLOW}Privacy restricted: {member.username}{Style.RESET_ALL}")
            except Exception as e:
                errors['other'] += 1
                logging.error(f"{Fore.MAGENTA}Unexpected error: {e}{Style.RESET_ALL}")

        logging.info(f"""
        {Fore.BLUE}Invite Report:
        - Total Invited: {total_invited}
        - Flood Errors: {errors['flood']}
        - Privacy Errors: {errors['privacy']}
        - Other Errors: {errors['other']}
        {Style.RESET_ALL}""")

        return {'total_invited': total_invited, 'errors': errors}

class TelegramAuth:
    @staticmethod
    async def login(api_id, api_hash, phone_number):
        """
        Proses login interaktif dengan Telegram
        """
        try:
            client = TelegramClient(StringSession(), api_id, api_hash)
            await client.start(phone=lambda: phone_number, code_callback=lambda: input(f"{Fore.GREEN}Masukkan kode verifikasi: {Style.RESET_ALL}"))
            
            # Jika 2FA diperlukan
            if not await client.is_user_authorized():
                password = getpass.getpass(f"{Fore.YELLOW}Masukkan password 2FA: {Style.RESET_ALL}")
                await client.sign_in(password=password)

            session_string = client.session.save()
            logging.info(f"{Fore.GREEN}Login Berhasil!{Style.RESET_ALL}")
            return {'client': client, 'session_string': session_string}
        except Exception as e:
            logging.error(f"{Fore.RED}Gagal Login: {e}{Style.RESET_ALL}")
            return None

class TelegramMemberInviteTool:
    def __init__(self):
        self.accounts = {}
        self.config_file = 'accounts.json'
        self.load_accounts()

    def load_accounts(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.accounts = json.load(f)
            except:
                self.accounts = {}

    def save_accounts(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.accounts, f)

    async def add_account(self):
        """Menambahkan akun baru dengan proses login lengkap"""
        print(f"{Fore.CYAN}[HIYAOK] Tambah Akun Telegram{Style.RESET_ALL}")
        
        api_id = input(f"{Fore.YELLOW}Masukkan API ID: {Style.RESET_ALL}")
        api_hash = input(f"{Fore.YELLOW}Masukkan API Hash: {Style.RESET_ALL}")
        phone_number = input(f"{Fore.YELLOW}Masukkan Nomor Telepon (dengan kode negara): {Style.RESET_ALL}")

        login_result = await TelegramAuth.login(int(api_id), api_hash, phone_number)

        if login_result:
            self.accounts[phone_number] = {
                'api_id': api_id,
                'api_hash': api_hash,
                'session_string': login_result['session_string'],
            }
            self.save_accounts()
            print(f"{Fore.GREEN}✓ Akun berhasil ditambahkan!{Style.RESET_ALL}")
            await login_result['client'].disconnect()
        else:
            print(f"{Fore.RED}✗ Gagal menambahkan akun{Style.RESET_ALL}")

    async def invite_process(self):
        """Proses invite member dengan strategi cerdas"""
        if not self.accounts:
            print(f"{Fore.RED}✗ Tidak ada akun yang tersimpan{Style.RESET_ALL}")
            return

        print(f"{Fore.CYAN}Pilih Akun:{Style.RESET_ALL}")
        for idx, (phone, _) in enumerate(self.accounts.items(), 1):
            print(f"{Fore.YELLOW}{idx}. {phone}{Style.RESET_ALL}")

        account_choice = int(input(f"{Fore.GREEN}Pilih nomor akun: {Style.RESET_ALL}"))
        selected_phone = list(self.accounts.keys())[account_choice - 1]
        selected_account = self.accounts[selected_phone]

        source_group = input(f"{Fore.YELLOW}Username/link group sumber: {Style.RESET_ALL}")
        dest_group = input(f"{Fore.YELLOW}Username/link group tujuan: {Style.RESET_ALL}")
        max_invites = int(input(f"{Fore.YELLOW}Jumlah maksimal member untuk diundang: {Style.RESET_ALL}"))

        client = TelegramClient(
            StringSession(selected_account['session_string']),
            int(selected_account['api_id']),
            selected_account['api_hash']
        )

        await client.start()

        try:
            await client(JoinChannelRequest(source_group))
            await client(JoinChannelRequest(dest_group))

            source_entity = await client.get_entity(source_group)
            dest_entity = await client.get_entity(dest_group)
            members = await client.get_participants(source_entity)

            result = await SmartInviteManager.smart_invite(client, source_entity, dest_entity, members, max_invites)

            print(f"{Fore.GREEN}✓ Proses invite selesai!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Total member diundang: {result['total_invited']}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}✗ Gagal: {e}{Style.RESET_ALL}")
        finally:
            await client.disconnect()

    def main_menu(self):
        """Menu utama aplikasi"""
        while True:
            print(f"\n{Fore.CYAN}[HIYAOK] TELEGRAM MEMBER INVITE TOOL{Style.RESET_ALL}")
            print(f"{Fore.GREEN}1. Tambah Akun{Style.RESET_ALL}")
            print(f"{Fore.GREEN}2. Proses Invite Member{Style.RESET_ALL}")
            print(f"{Fore.RED}3. Keluar{Style.RESET_ALL}")

            pilihan = input(f"{Fore.YELLOW}Pilih menu (1-3): {Style.RESET_ALL}")

            if pilihan == '1':
                asyncio.run(self.add_account())
            elif pilihan == '2':
                asyncio.run(self.invite_process())
            elif pilihan == '3':
                print(f"{Fore.RED}Keluar dari aplikasi...{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}Pilihan tidak valid!{Style.RESET_ALL}")

def main():
    tool = TelegramMemberInviteTool()
    tool.main_menu()

if __name__ == "__main__":
    main()
