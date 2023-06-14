import requests
import configparser
import subprocess
import time
import threading

class DDNSUpdater:
    def __init__(self, username, password, domain, use_ipv4=False, use_ipv6=False):
        self.username = username
        self.password = password
        self.domain = domain
        self.use_ipv4 = use_ipv4
        self.use_ipv6 = use_ipv6

    def update_address(self, ipv4_address=None, ipv6_address=None):
        if self.use_ipv4 and ipv4_address:
            raise NotImplementedError("Subclasses must implement update_address() method.")

        if self.use_ipv6 and ipv6_address:
            raise NotImplementedError("Subclasses must implement update_address() method.")

class MyDNSUpdater(DDNSUpdater):
    def __init__(self, username, password, ipv4_url, ipv6_url, domain, use_ipv4=False, use_ipv6=False):
        super().__init__(username, password, domain, use_ipv4, use_ipv6)
        self.ipv4_url = ipv4_url
        self.ipv6_url = ipv6_url
    
    def update_address(self, ipv4_address=None, ipv6_address=None):
        if self.use_ipv4 and ipv4_address:
            response = requests.get(self.ipv4_url, auth=(self.username, self.password))
            if response.status_code == 200:
                print("MyDNS address update successful.")
            else:
                print("Failed to update MyDNS address.")
           
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
        else:
            return

        if response.status_code == 200:
            if response.text.startswith("good") or response.text.startswith("nochg"):
                print("Google Domains address update successful.")
            else:
                print("Failed to update Google Domains address.")
        else:
            print("Failed to update Google Domains address.")

class DDNSManager:
    def __init__(self):
        self.mappings = {}
    
    def add_ddns_user(self, user):
        self.mappings[user.domain] = user
    
    def update_ddns_address(self, domain):
        user = self.mappings.get(domain)
        if user:
            if user.use_ipv4:
                my_ipv4 = self.get_my_ip()
                user.update_address(ipv4_address=my_ipv4)
            if user.use_ipv6:
                my_ipv6 = self.get_my_ip(ipv6=True)
                user.update_address(ipv6_address=my_ipv6)
    
    def check_ddns_address(self, domain):
        user = self.mappings.get(domain)
        if user:
            if user.use_ipv4:
                domain_ipv4 = self.get_domain_ip(user.domain)
                my_ipv4 = self.get_my_ip()
                if my_ipv4 != domain_ipv4:
                    user.update_address(ipv4_address=my_ipv4)
            if user.use_ipv6:
                domain_ipv6 = self.get_domain_ip(user.domain, ipv6=True)
                my_ipv6 = self.get_my_ip(ipv6=True)
                if my_ipv6 != domain_ipv6:
                    user.update_address(ipv6_address=my_ipv6)
    
    def get_my_ip(self, ipv6=False):
        if ipv6:
            result = subprocess.run(["dig", "@ident.me", "-6", "+short"], capture_output=True, text=True)
        else:
            result = subprocess.run(["dig", "@ident.me", "-4", "+short"], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    
    def get_domain_ip(self, domain, ipv6=False):
        if ipv6:
            result = subprocess.run(["dig", domain, "AAAA", "+short"], capture_output=True, text=True)
        else:
            result = subprocess.run(["dig", domain, "A", "+short"], capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None

class DDNSUpdaterThread(threading.Thread):
    def __init__(self, ddns_manager, interval_time, use_ipv4=False, use_ipv6=False):
        super().__init__()
        self.ddns_manager = ddns_manager
        self.interval_time = interval_time
        self.use_ipv4 = use_ipv4
        self.use_ipv6 = use_ipv6
    
    def run(self):
        while True:
            for domain in self.ddns_manager.mappings.keys():
                self.ddns_manager.update_ddns_address(domain)
            time.sleep(self.interval_time)

class DDNSCheckerThread(threading.Thread):
    def __init__(self, ddns_manager, interval_time, use_ipv4=False, use_ipv6=False):
        super().__init__()
        self.ddns_manager = ddns_manager
        self.interval_time = interval_time
        self.use_ipv4 = use_ipv4
        self.use_ipv6 = use_ipv6
    
    def run(self):
        while True:
            for domain in self.ddns_manager.mappings.keys():
                self.ddns_manager.check_ddns_address(domain)
            time.sleep(self.interval_time)

class DDNSConfigLoader:
    @classmethod
    def load_config(cls, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        
        ddns_manager = DDNSManager()

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
                ddns_manager.add_ddns_user(mydns)

            if section.startswith('GoogleDomains_user'):
                username = config.get(section, 'username')
                password = config.get(section, 'password')
                url = config.get(section, 'url')
                domain = config.get(section, 'domain')
                use_ipv4 = config.getboolean(section, 'use_ipv4')
                use_ipv6 = config.getboolean(section, 'use_ipv6')
                google_domains = GoogleDomainsUpdater(username, password, url, domain, use_ipv4, use_ipv6)
                ddns_manager.add_ddns_user(google_domains)
        
        return ddns_manager

def main():
    # コンフィグファイルの読み込み
    config = configparser.ConfigParser()
    config.read('config.ini')
    ddns_manager = DDNSConfigLoader.load_config('config.ini')

    # アドレス通知処理の非同期実行
    notification_interval = int(config.get('Schedule', 'notification_interval_sec'))
    notification_thread = DDNSUpdaterThread(ddns_manager, notification_interval, use_ipv4=True, use_ipv6=True)
    notification_thread.start()

    # アドレスチェック処理の非同期実行
    check_interval = int(config.get('Schedule', 'check_interval_sec'))
    check_thread = DDNSCheckerThread(ddns_manager, check_interval, use_ipv4=True, use_ipv6=True)
    check_thread.start()

    # メインスレッドの実行を継続
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
