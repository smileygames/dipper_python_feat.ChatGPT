# dipper_python_feat.ChatGPT
ChatGPTでオブジェクト指向で実装してみる事で、勉強する用

一応完成？はしました。
ちょっとついていけなくなってきた。辞書機能を使いだしたので。

9割ChatGPTさん作成です。
自分は出来上がったものをデバッグしておかしいところをc言語的思考で直しただけですね。

まぁ構成はかなり指示を出しましたが。
無理やりすべてクラス図にしてもらったりしていますのでPythonの書き方としては違うかもしれませんが。

クラス図も書いてくれた！

```python
+------------------------------------+
|            DDNSUpdater             |
+------------------------------------+
| - username: str                    |
| - password: str                    |
| - domain: str                      |
| - use_ipv4: bool                   |
| - use_ipv6: bool                   |
+------------------------------------+
| + update_address(ipv4_address=None, |
|     ipv6_address=None)              |
+------------------------------------+
                ^
                |
        +-----------------+
        |                 |
+----------------+  +----------------------+
| MyDNSUpdater   |  | GoogleDomainsUpdater |
+----------------+  +----------------------+
| - ipv4_url: str |  | - url: str           |
| - ipv6_url: str |  +----------------------+
+----------------+  | + update_address(ipv4_address=None, |
                    |     ipv6_address=None)              |
                    +------------------------------------+
                                ^
                                |
               +-----------------------------------+
               |                                   |
      +-----------------+                 +--------------------+
      | DDNSManager     |                 | DDNSConfigLoader    |
      +-----------------+                 +--------------------+
      | - mappings: dict[str, DDNSUpdater] |                    |
      +-----------------+                 +--------------------+
      | + add_ddns_user(user: DDNSUpdater) | + load_config(filename: str): DDNSManager |
      | + update_ddns_address(domain: str) |                                    |
      | + check_ddns_address(domain: str)  |                                    |
      | + get_my_ip(ipv6: bool = False): str|                                   |
      | + get_domain_ip(domain: str, ipv6: bool = False): str |              |
      +-----------------+                 +--------------------+
                            ^
                            |
             +-----------------------+
             |                       |
    +-------------------+    +-------------------+
    | DDNSUpdaterThread |    | DDNSCheckerThread |
    +-------------------+    +-------------------+
    | - ddns_manager: DDNSManager | - ddns_manager: DDNSManager |
    | - interval_time: int        | - interval_time: int        |
    | - use_ipv4: bool            | - use_ipv4: bool            |
    | - use_ipv6: bool            | - use_ipv6: bool            |
    +-------------------+    +-------------------+
    | + run()            |    | + run()            |
    +-------------------+    +-------------------+
```

一応書き直してみた。
![UML クラス](https://github.com/smileygames/dipper_python_feat.ChatGPT/assets/134200591/347411b2-ce1e-44f7-bba6-6b561d3a3b5a)

