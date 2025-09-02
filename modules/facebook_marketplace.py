from colorama import Fore, Style
import os
 
def run():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.LIGHTMAGENTA_EX}--- Facebook Marketplace ---{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Coming Soon...\n")
    input(f"{Fore.LIGHTBLACK_EX}Press Enter to return to main menu...") 