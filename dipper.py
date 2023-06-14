import requests
import configparser
import subprocess
import schedule
import time
import threading

class DDNSUpdater:
    def __init__(self, username, password, domain):
        self.username = username
        self.password = password
        self.domain = domain
    
    def update_address(self, ip_address):
        raise NotImplementedError("Subclasses must implement update_address method.")

class MyDNSUpdater(DDNSUpdater):
    def __init__(self, username, password, ipv4_url, ipv6_url, domain):
        super().__init__(username, password, domain)
        self.ipv4_url = ipv4_url
        self.ipv6_url = ipv6_url
        self.previous_ip = None
    
    def update_address(self, ipv4_address=None, ipv6_address=None):
        if ipv6_address:
            url = self.ipv6_url
        else:
            url = self.ipv4_url
        
        response = requests.get(url, auth=(self.username, self.password))
        
        if response.status_code == 200:
            print("MyDNS address update successful.")
        else:
            print("Failed to update MyDNS address.")

class GoogleDomainsUpdater(DDNSUpdater):
    def __init__(self, username, password, url, domain):
        super().__init__(username, password, domain)
        self.url = url
        self.previous_ip = None
    
    def update_address(self, ip_address):
        url = f"{self.url}?hostname={self.domain}&myip={ip_address}"
        
        response = requests.get(url, auth=(self.username, self.password))
        
        if response.status_code == 200:
            if response.text.startswith("good") or response.text.startswith("nochg"):
                print("Google Domains address update successful.")
            else:
                print("Failed to update Google Domains address.")
        else:
            print("Failed to update Google Domains address.")

# 自分のIPアドレスを取得する関数
def get_my_ip():
    result = subprocess.run(["dig", "@ident.me", "-4", "+short"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        raise Exception("Failed to get IP address.")

# ドメインのIPアドレスを取得する関数
def get_domain_ip(domain):
    result = subprocess.run(["dig", domain, "-4", "+short"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        raise Exception("Failed to get domain IP address.")

# 定期的なアドレス通知処理
def update_ddns(domain_user):
    # 自分のIPアドレスを取得
    my_ip = get_my_ip()

    # MyDNSのアップデート
    domain_user.update_address(my_ip)

# 定期的なチェック処理
def check_ddns(domains_user):
    # ドメインのIPアドレスを取得
    mydns_domain_ip = get_domain_ip(domains_user.domain)

    # IPアドレスが変更された場合にアドレスを更新
    my_ip = get_my_ip()
    if my_ip != mydns_domain_ip:
        domains_user.update_address(my_ip)

# 別スレッド非同期タイマー処理
def timer_update(interval_time, mydns_users, google_domains_users):
    while True:
        for mydns_user in mydns_users:
            update_ddns(mydns_user)
        time.sleep(interval_time)

def timer_check(interval_time, mydns_users, google_domains_users):
    while True:
        for mydns_user in mydns_users:
            check_ddns(mydns_user)
        for google_domains_user in google_domains_users:
            check_ddns(google_domains_user)

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
            mydns = MyDNSUpdater(username, password, ipv4_url, ipv6_url, domain)
            mydns_users.append(mydns)
    
    # Google Domainsの設定を取得
    google_domains_users = []
    for section in config.sections():
        if section.startswith('GoogleDomains_user'):
            username = config.get(section, 'username')
            password = config.get(section, 'password')
            url = config.get(section, 'url')
            domain = config.get(section, 'domain')
            google_domains = GoogleDomainsUpdater(username, password, url, domain)
            google_domains_users.append(google_domains)

    # アドレス通知処理の非同期実行
    notification_interval = int(config.get('Schedule', 'notification_interval_sec'))
    notification_threads = []
    thread = threading.Thread(target=timer_update, args=(notification_interval, mydns_users, google_domains_users,))
    thread.start()
    notification_threads.append(thread)

    # アドレスチェック処理の非同期実行
    check_interval = int(config.get('Schedule', 'check_interval_sec'))
    check_threads = []
    thread = threading.Thread(target=timer_check, args=(check_interval, mydns_users, google_domains_users,))
    thread.start()
    check_threads.append(thread)

    # メインスレッドの実行を継続
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
