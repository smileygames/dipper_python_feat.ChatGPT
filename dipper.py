import requests
import configparser
import subprocess
import schedule
import time

class DDNSUpdater:
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def update_address(self, ip_address):
        raise NotImplementedError("Subclasses must implement update_address method.")

class MyDNSUpdater(DDNSUpdater):
    def __init__(self, username, password, ipv4_url, ipv6_url, domain):
        super().__init__(username, password)
        self.ipv4_url = ipv4_url
        self.ipv6_url = ipv6_url
        self.domain = domain
        self.previous_ipv4 = None
        self.previous_ipv6 = None
    
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
        super().__init__(username, password)
        self.url = url
        self.domain = domain
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
def get_my_ip(ip_version):
    if ip_version == 4:
        result = subprocess.run(["dig", "@ident.me", "-4", "+short"], capture_output=True, text=True)
    elif ip_version == 6:
        result = subprocess.run(["dig", "@ident.me", "-6", "+short"], capture_output=True, text=True)
    else:
        raise ValueError("Invalid IP version. Supported values are 4 and 6.")

    if result.returncode == 0:
        return result.stdout.strip()
    else:
        raise Exception("Failed to get IP address.")


# ドメインのIPアドレスを取得する関数
def get_domain_ip(domain):
    result = subprocess.run(["dig", domain, "+short"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        raise Exception("Failed to get domain IP address.")

# 定期的なアドレス通知処理
def update_ddns(mydns, google_domains):
    # 自分のIPアドレスを取得
#    my_ip = get_my_ip()
    ipv4_address = get_my_ip(4)
    ipv6_address = get_my_ip(6)

    # ドメインのIPアドレスを取得
    domain_ip = get_domain_ip(mydns.domain)

    # IPアドレスが変更された場合のみアドレスを更新
    if ipv4_address != domain_ip:
        # IPv4アドレスを指定してアドレスを更新
        mydns.update_address(ipv4_address)

    if ipv6_address != domain_ip:
        # IPv4アドレスを指定してアドレスを更新
        mydns.update_address(ipv4_address, ipv6_address)

    # IPアドレスが変更された場合のみアドレスを更新
    if ipv4_address != get_domain_ip(google_domains.domain):
        # IPv4アドレスを指定してアドレスを更新
        google_domains.update_address(ipv4_address)

# 設定ファイルを読み込む
config = configparser.ConfigParser()
config.read('config.ini')

# MyDNSの設定を取得
mydns_ipv4_url = config.get('MyDNS', 'ipv4_url')
mydns_ipv6_url = config.get('MyDNS', 'ipv6_url')
mydns_domain = config.get('MyDNS', 'domain')
mydns_username = config.get('MyDNS', 'username')
mydns_password = config.get('MyDNS', 'password')

# Google Domainsの設定を取得
google_domains_url = config.get('GoogleDomains', 'url')
google_domains_domain = config.get('GoogleDomains', 'domain')
google_domains_username = config.get('GoogleDomains', 'username')
google_domains_password = config.get('GoogleDomains', 'password')

# MyDNSUpdaterのインスタンスを作成
mydns = MyDNSUpdater(mydns_username, mydns_password, mydns_ipv4_url, mydns_ipv6_url, mydns_domain)

# GoogleDomainsUpdaterのインスタンスを作成
google_domains = GoogleDomainsUpdater(google_domains_username, google_domains_password, google_domains_url, google_domains_domain)

# 初回のアドレス通知処理を実行
update_ddns(mydns, google_domains)

# コンフィグから通知間隔を取得
interval_hours = int(config.get('Schedule', 'interval_hours'))

# 指定された時間間隔でアドレス通知処理をスケジュール
schedule.every(interval_hours).hours.do(update_ddns, mydns, google_domains)

while True:
    schedule.run_pending()
    time.sleep(1)
