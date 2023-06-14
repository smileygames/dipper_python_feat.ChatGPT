import requests
import configparser
import subprocess
import time
import threading

import requests

class DDNSUpdater:
    def __init__(self, username, password, domain, use_ipv4=False, use_ipv6=False):
        self.username = username
        self.password = password
        self.domain = domain
        self.use_ipv4 = use_ipv4
        self.use_ipv6 = use_ipv6
    
    def update_address(self):
        raise NotImplementedError("Subclasses must implement update_address method.")

class MyDNSUpdater(DDNSUpdater):
    def __init__(self, username, password, ipv4_url, ipv6_url, domain, use_ipv4=False, use_ipv6=False):
        super().__init__(username, password, domain, use_ipv4, use_ipv6)
        self.ipv4_url = ipv4_url
        self.ipv6_url = ipv6_url
    
    def update_address(self, ipv4_address=None, ipv6_address=None):
        if self.use_ipv4 and ipv4_address:
            response = requests.get(self.ipv4_url, auth=(self.username, self.password))
            
        if self.use_ipv6 and ipv6_address:
            response = requests.get(self.ipv6_url, auth=(self.username, self.password))
            
        if response.status_code == 200:
            print("MyDNS address update successful.")
        else:
            print("Failed to update MyDNS address.")

class GoogleDomainsUpdater(DDNSUpdater):
    def __init__(self, username, password, url, domain, use_ipv4=False, use_ipv6=False):
        super().__init__(username, password, domain, use_ipv4, use_ipv6)
        self.url = url
  
    def update_address(self, ipv4_address=None, ipv6_address=None):
        if self.use_ipv4 and ipv4_address:
            url = f"{self.url}?hostname={self.domain}&myip={ipv4_address}"
            response = requests.get(url, auth=(self.username, self.password))

        elif self.use_ipv6 and ipv6_address:
            url = f"{self.url}?hostname={self.domain}&myip={ipv6_address}"
            response = requests.get(url, auth=(self.username, self.password))

        if response.status_code == 200:
            if response.text.startswith("good") or response.text.startswith("nochg"):
                print("Google Domains address update successful.")
            else:
                print("Failed to update Google Domains address.")
        else:
            print("Failed to update Google Domains address.")

# 自分のIPアドレスを取得する関数
def get_my_ip(ipv6=False):
    if ipv6:
        result = subprocess.run(["dig", "@ident.me", "-6", "+short"], capture_output=True, text=True)
    else:
        result = subprocess.run(["dig", "@ident.me", "-4", "+short"], capture_output=True, text=True)
    
    if result.returncode == 0:
        return result.stdout.strip()
#    else:
#        raise Exception("Failed to get IP address.")

# ドメインのIPアドレスを取得する関数
def get_domain_ip(domain, ipv6=False):
    if ipv6:
        result = subprocess.run(["dig", domain, "AAAA", "+short"], capture_output=True, text=True)
    else:
        result = subprocess.run(["dig", domain, "A", "+short"], capture_output=True, text=True)
    
    if result.returncode == 0:
        return result.stdout.strip()
#    else:
#        raise Exception("Failed to get domain IP address.")

# 定期的なアドレス通知処理
def update_ddns(domain_user, use_ipv4=False, use_ipv6=False):
    if use_ipv4:
        my_ipv4 = get_my_ip()
        domain_user.update_address(ipv4_address=my_ipv4)
    if use_ipv6:
        my_ipv6 = get_my_ip(ipv6=True)
        domain_user.update_address(ipv6_address=my_ipv6)

# 定期的なチェック処理
def check_ddns(domain_user, use_ipv4=False, use_ipv6=False):
    if use_ipv4:
        domain_ipv4 = get_domain_ip(domain_user.domain)
        my_ipv4 = get_my_ip()
        if my_ipv4 != domain_ipv4:
            domain_user.update_address(ipv4_address=my_ipv4)
    if use_ipv6:
        domain_ipv6 = get_domain_ip(domain_user.domain, ipv6=True)
        my_ipv6 = get_my_ip(ipv6=True)
        if my_ipv6 != domain_ipv6:
            domain_user.update_address(ipv6_address=my_ipv6)

# 別スレッド非同期タイマー処理
def timer_update(interval_time, mydns_users, use_ipv4=False, use_ipv6=False):
    while True:
        for mydns_user in mydns_users:
            update_ddns(mydns_user, use_ipv4=use_ipv4, use_ipv6=use_ipv6)

        time.sleep(interval_time)

def timer_check(interval_time, mydns_users, google_domains_users, use_ipv4=False, use_ipv6=False):
    while True:
        for mydns_user in mydns_users:
            user=mydns_user
            check_ddns(user, user.use_ipv4, user.use_ipv6)
        for google_domains_user in google_domains_users:
            user=google_domains_user
            check_ddns(user, user.use_ipv4, user.use_ipv6)

        time.sleep(interval_time)

# メイン処理
def main():
    # コンフィグファイルの読み込み
    config = configparser.ConfigParser()
    config.read('config.ini')

    # MyDNSの設定を取得
    mydns_users = []
    for section in config.sections():
        if section.startswith('MyDNS_user'):
            username = config.get(section, 'username')
            password = config.get(section, 'password')
            ipv4_url = config.get(section, 'ipv4_url')
            ipv6_url = config.get(section, 'ipv6_url')
            domain = config.get(section, 'domain')
            use_ipv4 = config.getboolean(section, 'use_ipv4')
            use_ipv6 = config.getboolean(section, 'use_ipv6')
            mydns = MyDNSUpdater(username, password, ipv4_url, ipv6_url, domain, use_ipv4, use_ipv6)
            mydns_users.append(mydns)
    
    # Google Domainsの設定を取得
    google_domains_users = []
    for section in config.sections():
        if section.startswith('GoogleDomains_user'):
            username = config.get(section, 'username')
            password = config.get(section, 'password')
            url = config.get(section, 'url')
            domain = config.get(section, 'domain')
            use_ipv4 = config.getboolean(section, 'use_ipv4')
            use_ipv6 = config.getboolean(section, 'use_ipv6')
            google_domains = GoogleDomainsUpdater(username, password, url, domain, use_ipv4, use_ipv6)
            google_domains_users.append(google_domains)


    # アドレス通知処理の非同期実行
    notification_interval = int(config.get('Schedule', 'notification_interval_sec'))
    notification_threads = []
    thread = threading.Thread(target=timer_update, args=(notification_interval, mydns_users, use_ipv4, use_ipv6))
    thread.start()
    notification_threads.append(thread)

    # アドレスチェック処理の非同期実行
    check_interval = int(config.get('Schedule', 'check_interval_sec'))
    check_threads = []
    thread = threading.Thread(target=timer_check, args=(check_interval, mydns_users, google_domains_users, use_ipv4, use_ipv6))
    thread.start()
    check_threads.append(thread)

    # メインスレッドの実行を継続
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
