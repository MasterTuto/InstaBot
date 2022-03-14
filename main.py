#pylint: disable=broad-except,global-statement,unnecessary-lambda
from sys import stdout
from time import sleep
from getpass import getpass
from random import choice, shuffle
from selenium import webdriver, common
from webdriver_manager.utils import ChromeType
from selenium.webdriver.common.keys import Keys
from webdriver_manager.microsoft import IEDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

TOTAL = 0

_author__ = "Breno [MasterTuto, Lord13]"
__version__ = "v6"

class InstaBot(object):
    self_following = []
    self_username = None
    all_users_tagged_once = False

    def __init__(self, browser_t, browser, must_stop_after_first_cycle=False):
        driver_gen_funcs = [
            lambda ce: webdriver.Chrome(ce),
            lambda ci: webdriver.Chrome(ci),
            lambda f:  webdriver.Firefox(executable_path=f),
            lambda ie: webdriver.Ie(ie),
            lambda e:  webdriver.Edge(e)
        ]
        self.driver = driver_gen_funcs[browser_t-1](browser) #webdriver.Firefox()
        self.driver.implicitly_wait(3)

        self.instagram_base_url = 'https://www.instagram.com/'

        self.must_stop_after_first_cycle = must_stop_after_first_cycle

    def log_in(self, username_elem, password_elem, username, password):
        username_elem.send_keys(username)
        password_elem.send_keys(password)

        username_elem.submit()
        self.driver.implicitly_wait(7)

    def log_in_native(self, username, password):
        login_url = self.instagram_base_url+'accounts/login/'
        self.driver.get(login_url)

        username_elt = self.driver.find_element_by_name("username")
        password_elt = self.driver.find_element_by_name("password")

        self.log_in(username_elt, password_elt, username, password)
        print("usuario: ", "O nome de usuário inserido não pertence a uma conta" in self.driver.page_source)
        print("senha: ", "Sua senha está incorreta" in self.driver.page_source)

        self.set_username()

    def log_in_via_facebook(self, username, password):
        login_url = self.instagram_base_url+'accounts/login/'
        self.driver.get(login_url)

        facebook_login_btn = self.driver.find_element_by_css_selector('.sqdOP.yWX7d.y3zKF')
        facebook_login_btn.click()

        facebook_username_elem = self.driver.find_element_by_name("email")
        facebook_password_elem = self.driver.find_element_by_name("pass")

        self.log_in(facebook_username_elem, facebook_password_elem, username, password)

        self.set_username()

    def set_username(self):
        try:
            profile_btn = self.driver.find_element_by_css_selector('a.gmFkV')
        except common.exceptions.NoSuchElementException as e:
            self.set_username()
            return
        
        self.self_username = profile_btn.get_attribute('href').split("/")[-2]

    def follow_user(self, user):
        self.driver.get(self.instagram_base_url+user)

        try:
            follow_btn = self.driver.find_element_by_css_selector("._5f5mN.jIbKX._6VtSN.yZn4P")
            follow_btn.click()

            return True
        except Exception:
            return False

    def scroll_down(self):
        script = ("var elem = document.getElementsByClassName('isgrP');elem[0].scrollBy(0,10000);")
        self.driver.execute_script(script)

    def set_self_following(self):
        self.driver.get(self.instagram_base_url+self.self_username)

        #self.driver.find_element_by_css_selector('a[href="/%s/following/"]'%self.self_username).click()
        self.driver.find_element_by_css_selector('a[href="/%s/followers/"]'%self.self_username).click()

        for _ in range(15):
            sleep(3)
            self.scroll_down()

        self.self_following = list(map(lambda x: x.get_attribute('title'), self.driver.find_elements_by_css_selector('a.FPmhX')))

    def get_followers_count(self, user):
        self.driver.get(self.instagram_base_url+user)

        try:
            number_of_followers = self.driver.find_element_by_css_selector('a[href="/%s/followers/"] .g47SY' % user)
        except Exception as e:
            number_of_followers = self.driver.find_element_by_css_selector('ul.k9GMp li.Y8-fY:nth-child(2) .g47SY')
        number_of_followers = number_of_followers.get_attribute("title").replace('.', '')
        return int(number_of_followers)

    def get_following_count(self, user):
        self.driver.get(self.instagram_base_url+user)
        try:
            number_of_following = self.driver.find_element_by_css_selector('a[href="/%s/following/"] .g47SY' % user).text
        except Exception:
            number_of_following = self.driver.find_element_by_css_selector('ul.k9GMp li.Y8-fY:nth-child(3) .g47SY').text
        return int(number_of_following.replace('.', '')) if 'mil' not in number_of_following else int(number_of_following.replace('.', ''))*1000

    def get_follow_ratio(self, user):
        return self.get_followers_count(user) / self.get_following_count(user)

    def is_user_valid(self, user: str) -> bool:
        headers = {
            'Host': 'www.instagram.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers'
        }
        
        return requests.get(f"https://www.instagram.com/{user}/", headers=headers).status_code != 404

    def build_message(self, text_to_send, number_of_people, preselected_users):
        message = [text_to_send]
        while number_of_people > 0:
            if preselected_users:
                shuffle(preselected_users)
                preselected_users.sort(key=lambda x: x[0])
                random_user = preselected_users[0]


                if random_user[0] == 1 and self.must_stop_after_first_cycle:
                    self.all_users_tagged_once = True
                    break
                
                if '@'+random_user[1] in message:
                    continue
                else:
                    if not self.is_user_valid(random_user):
                        continue

                    random_user[0] += 1
                    random_user = random_user[1]
            else:
                random_user = choice(self.self_following)

                if '@'+random_user in message or self.get_follow_ratio(random_user) > 3:
                    continue
        
            message.append("@"+random_user)#message.append(random_user) CHANGED
            number_of_people -= 1
        return ' '.join(message)

    def send_message(self, promo_url, message):
        if not (self.driver.current_url == promo_url):
            self.driver.get(promo_url)
        sleep(3)

        try:
            message_input = self.driver.find_element_by_css_selector('.Ypffh')
            message_input.send_keys(message)
        except Exception:
            message_input = self.driver.find_element_by_css_selector('.Ypffh')
            message_input.send_keys(message)
        
        try:
            send_btn = self.driver.find_element_by_css_selector('form.X7cDz button')
            send_btn.click()
        except Exception:
            send_btn = self.driver.find_element_by_css_selector('form.X7cDz button')
            send_btn.click()


    def send_messages(self, promo_url, text_to_send, preselected_users, number_of_people, interval):
        global TOTAL
        if not (self.self_following or preselected_users):
            self.set_self_following()			

        while True:
            if self.all_users_tagged_once and self.must_stop_after_first_cycle:
                print("[!] FINALIZADO: Todos os usuários especificados já marcados ao menos uma vez")
                break
            message = self.build_message(text_to_send, number_of_people, preselected_users)
            try:
                self.send_message(promo_url, message)
                TOTAL += 1
            #pylint: disable=broad-except
            except Exception:
                self.driver.execute_script("location.reload(true);")
                sleep(3)

            show_waiting(interval)
        
        def close_browser(self):
            self.driver.close()

def show_waiting(time_to_wait):
    global TOTAL
    for current_sec in range(time_to_wait, 0, -1):
        stdout.write("\r[%s] Esperando %s para enviar novamente..." % (TOTAL, current_sec))
        stdout.flush()
        sleep(1)

def ask_for_user_and_passwd():
    use_facebook = input("Logar com Facebook? [Sim/Não] ")
    if use_facebook.lower() == 'sim' or use_facebook.lower() == 's':
        use_facebook = True
    elif  use_facebook.lower() == 'nao' or use_facebook.lower() == 'não' or use_facebook.lower() == 'n':
        use_facebook = False
    else:
        print("Não entendi, digite novamente.")
        return ask_for_user_and_passwd()

    username = input("Digite seu usuario (email ou telefone): ")
    password = getpass("Digite sua senha: ")

    return username, password, use_facebook

def follow_required_users(insta_bot):
    print("Antes de continuar, digite um a um os usuários que precisa seguir (sem @) ou -1 para não enviar.")
    user_to_follow = input("Digite um usuário: @")
    while user_to_follow != '-1':
        follow_sucessful = insta_bot.follow_user(user_to_follow)

        if not follow_sucessful:
            print("Não foi possível seguir usuário, verifique o usuário digitado (NÃO adicione arrobas - @!).")
        user_to_follow = input("Digite um usuário: @")

def ask_for_promo_url():
    promo_url = input("Digite a URL da promoção: ")

    if not promo_url.lower().startswith('http'):
        print("Obrigatório a URL se iniciar com http:// !!")
        return ask_for_promo_url()

    if 'instagram' not in promo_url.lower():
        print("O site não é o instagram!")
        return ask_for_promo_url()

    return promo_url

def ask_for_pretext():
    use_pretext = input("Deseja digitar alguma mensagem fora a marcação? [Sim/Não] ").lower()
    if not (use_pretext.startswith("s") or use_pretext.startswith('n')):
        print("Não entendi, digite novamente.")
        return ask_for_pretext()

    return input("Digite o texto para ir junto da citação: ") if use_pretext[0] == 's' else ''

def ask_for_preselected_users():
    preselect_users = input("Deseja digitar/listar com antecedência os usuários para marcar? [Sim/Não] ").lower()
    if not (preselect_users.startswith("s") or preselect_users.startswith('n')):
        print("Não entendi, digite novamente.")
        return ask_for_preselected_users()

    if preselect_users[0] == 'n':
        return []

    
    open_file = input("Os usuários estão num arquivo? [Sim/Não] ").lower()
    while not (open_file.startswith("s") or open_file.startswith('n')): 
        print("Não entendi, digite novamente.")
        open_file = input("Os usuários estão num arquivo? [Sim/Não] ").lower()

    preselected_users = []
    if open_file[0] == 's':
        went_wrong = True

        while went_wrong:
            users_file = input("Digite o caminho do arquivo (ou o nome apenas se estiver na mesma pasta do script): ")
            try:
                with open(users_file, 'r') as file:
                    preselected_users = [[0, c.strip()] for c in file.readlines()]
                went_wrong = False
            except FileNotFoundError:
                print("Arquivo não encontrado! Insira novamente.")
                went_wrong = True
    else:
        user = input("Digite um usuario de cada vez (sem @) e -1 para parar.")
        while user != '-1':
            preselected_users.append([ 0, '@'+user ])
            user = input("Digite um usuário: @")

    return preselected_users

def ask_for_number_per_comment():
    number_of_people = int(input("Marcar quantas pessoas por comentário? "))
    return number_of_people if number_of_people > 0 else ask_for_number_per_comment()

def ask_for_browser():
    browser_gen_funcs = [lambda: ChromeDriverManager().install(),
                         lambda: ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(),
                         lambda: GeckoDriverManager().install(),
                         lambda: IEDriverManager().install(),
                         lambda: EdgeChromiumDriverManager().install()]

    print(('Qual browser você usa?\n'
          '\t[1] Chrome\n'
          '\t[2] Chromium\n'
          '\t[3] FireFox\n'
          '\t[4] Internet Explorer\n'
          '\t[5] Microsoft Edge\n\n'
          '\t[0] Nenhum destes\n'))
    
    browser = int(input("Digite o numero do seu browser: "))
    while browser < 0 or browser > 5:
        browser = input("Valor inválido! Digite outro numero: ")

    if browser == 0:
        print("Browser não suportado :/")
        exit(1)
    else:
        return browser, browser_gen_funcs[browser-1]()

def ask_for_interval():
    interval = int(input("Digite o intervalo (em segundos) desejado entre cada mensagem: "))
    if interval < 4:
        print("Digite um invervalo maior que quatro segundos!")
        interval = int(input("Digite o intervalo desejado entre cada mensagem: "))
    
    return interval

def main():
    browser_t, browser = ask_for_browser()

    insta_bot = InstaBot(browser_t, browser)

    login_unsuccessful = True
    while login_unsuccessful:
        username, password, use_facebook = ask_for_user_and_passwd()
        if use_facebook:
            login_unsuccessful = insta_bot.log_in_via_facebook(username, password)
        else:
            login_unsuccessful = insta_bot.log_in_native(username, password)

    follow_required_users(insta_bot)
    
    promo_url = ask_for_promo_url()
    text_to_send = ask_for_pretext()

    preselected_users = ask_for_preselected_users()
    number_of_people = ask_for_number_per_comment()
    interval = ask_for_interval()

    print("[*] Enviando mensagens...")
    insta_bot.send_messages(promo_url, text_to_send, preselected_users, number_of_people, interval)


if __name__ == '__main__':
    main()