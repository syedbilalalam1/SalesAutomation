import sys
import os
from modules import email_marketing, linkedin_outreach, twitter_dms, facebook_marketplace
from colorama import init, Fore, Style
import time

init(autoreset=True)

def print_ascii_banner():
    banner = [
        f"{Fore.MAGENTA}          _____                    _____                    _____          ",
        f"{Fore.LIGHTMAGENTA_EX}         /\    \                  /\    \                  /\    \         ",
        f"{Fore.MAGENTA}        /::\    \                /::\    \                /::\____\        ",
        f"{Fore.LIGHTMAGENTA_EX}       /::::\    \              /::::\    \              /::::|   |        ",
        f"{Fore.MAGENTA}      /::::::\    \            /::::::\    \            /:::::|   |        ",
        f"{Fore.LIGHTMAGENTA_EX}     /:::/\:::\    \          /:::/\:::\    \          /::::::|   |        ",
        f"{Fore.MAGENTA}    /:::/  \:::\    \        /:::/__\:::\    \        /:::/|::|   |        ",
        f"{Fore.LIGHTMAGENTA_EX}   /:::/    \:::\    \      /::::\   \:::\    \      /:::/ |::|   |        ",
        f"{Fore.MAGENTA}  /:::/    / \:::\    \    /::::::\   \:::\    \    /:::/  |::|___|______  ",
        f"{Fore.LIGHTMAGENTA_EX} /:::/    /   \:::\    \  /:::/\:::\   \:::\    \  /:::/   |::::::::\    \ ",
        f"{Fore.MAGENTA}/:::/____/     \:::\____\/:::/__\:::\   \:::\____\/:::/    |:::::::::\____\\",
        f"{Fore.LIGHTMAGENTA_EX}\:::\    \      \::/    /\:::\   \:::\   \::/    /\::/    / ~~~~~/:::/    /",
        f"{Fore.MAGENTA} \:::\    \      \/____/  \:::\   \:::\   \/____/  \/____/      /:::/    / ",
        f"{Fore.LIGHTMAGENTA_EX}  \:::\    \               \:::\   \:::\    \                  /:::/    /  ",
        f"{Fore.MAGENTA}   \:::\    \               \:::\   \:::\____\                /:::/    /   ",
        f"{Fore.LIGHTMAGENTA_EX}    \:::\    \               \:::\   \::/    /               /:::/    /    ",
        f"{Fore.MAGENTA}     \:::\    \               \:::\   \/____/               /:::/    /     ",
        f"{Fore.LIGHTMAGENTA_EX}      \:::\    \               \:::\    \                  /:::/    /      ",
        f"{Fore.MAGENTA}       \:::\____\               \:::\____\                /:::/    /       ",
        f"{Fore.LIGHTMAGENTA_EX}        \::/    /                \::/    /                \::/    /        ",
        f"{Fore.MAGENTA}         \/____/                  \/____/                  \/____/         "
    ]
    for line in banner:
        print(line)
    print(f"{Fore.LIGHTBLACK_EX}             Created by syedbilalalam\n")

def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_ascii_banner()
        print(f"{Fore.CYAN}1. Email Marketing")
        print(f"{Fore.CYAN}2. LinkedIn Outreach")
        print(f"{Fore.CYAN}3. Twitter DMs")
        print(f"{Fore.CYAN}4. Facebook Marketplace")
        print(f"{Fore.LIGHTBLACK_EX}5. Exit\n")
        choice = input(f"{Fore.LIGHTGREEN_EX}Select a module (1-5): ")
        if choice == '1':
            email_marketing.run()
        elif choice == '2':
            linkedin_outreach.run()
        elif choice == '3':
            twitter_dms.run()
        elif choice == '4':
            facebook_marketplace.run()
        elif choice == '5':
            print(f"{Fore.LIGHTMAGENTA_EX}Goodbye!")
            time.sleep(1)
            sys.exit(0)
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu() 