# dipper_python_feat.ChatGPT
ChatGPTでオブジェクト指向で実装してみる事で、勉強する用

機能としてはdipperと同じものを目指しました。

一応完成？はしました。
ちょっとついていけなくなってきた。辞書機能を使いだしたので。

9割ChatGPTさん作成です。
自分は出来上がったものをデバッグしておかしいところをc言語的思考で直しただけですね。

まぁ構成はかなり指示を出しましたが。
無理やりすべてクラスにしてもらったりしていますのでPythonの書き方としては違うかもしれませんが。

クラス図も書いてくれた！

```python
    +-------------------------------------+
    |             DDNSUpdater             |
    +-------------------------------------+
    | - username: str                     |
    | - password: str                     |
    | - domain: str                       |
    | - use_ipv4: bool                     |
    | - use_ipv6: bool                     |
    +-------------------------------------+
    | + __init__(username, password,      |
    |    domain, use_ipv4=False,          |
    |    use_ipv6=False)                  |
    | + update_address(ipv4_address=None, |
    |    ipv6_address=None)               |
    +-------------------------------------+
                  ^
                  |
         +-------------------+
         |                   |
+---------------------+ +-----------------------+
|    MyDNSUpdater     | | GoogleDomainsUpdater  |
+---------------------+ +-----------------------+
| - ipv4_url: str    | | - url: str             |
| - ipv6_url: str    | +-----------------------+
+---------------------+
| + __init__(username,|
|    password,        |
|    ipv4_url,        |
|    ipv6_url,        |
|    domain,          |
|    use_ipv4=False,  |
|    use_ipv6=False)  |
| + update_address(ipv4_address=None,|
|    ipv6_address=None)                 |
+---------------------+
                  ^
                  |
            +-------------+
            |             |
      +----------------+ +-------------------+
      | DDNSManager    | | DDNSConfigLoader  |
      +----------------+ +-------------------+
      | - mappings: dict                   |
      +----------------+                   |
      | + add_ddns_user(user)              |
      | + update_ddns_address(domain)      |
      | + check_ddns_address(domain)       |
      | + get_my_ip(ipv6=False)            |
      | + get_domain_ip(domain, ipv6=False)|
      +-----------------------------------+
                  ^
                  |
      +-----------------------+
      |                       |
+------------------+ +------------------+
| DDNSUpdaterThread| | DDNSCheckerThread|
+------------------+ +------------------+
| - ddns_manager: DDNSManager         |
| - interval_time: int                |
| - use_ipv4: bool                    |
| - use_ipv6: bool                    |
+------------------+ +------------------+
| + run()                            |
+------------------+ +------------------+
```

