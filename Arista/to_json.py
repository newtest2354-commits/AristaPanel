import os
import re
import json
import base64
import uuid
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote
from typing import Optional, Dict, Any, List

class ConfigToJSONConverter:
    def __init__(self):
        self.categories = [
            'vmess', 'vless', 'trojan', 'ss',
            'hysteria2', 'hysteria', 'tuic',
            'wireguard', 'other'
        ]
        self.tiers = [50, 100, 150, 200, 250, 300, 400, 500, "ALL"]
        self.port_tiers = [80, 8080, 443, 8443, 2096, 2087, 2053, 8880, 2083, 2086, 2095, 2052, 9443]
        self.uuid_re = re.compile(
            r"^[0-9a-fA-F]{8}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{12}$"
        )
        self.allowed_ss_ciphers = {
            "aes-128-gcm", "aes-256-gcm", "chacha20-ietf-poly1305",
            "aes-128-cfb", "aes-256-cfb", "chacha20", "chacha20-ietf",
            "2022-blake3-aes-128-gcm", "2022-blake3-aes-256-gcm",
            "2022-blake3-chacha20-poly1305"
        }
        self.allowed_fp = {
            "chrome", "firefox", "safari", "ios", "android",
            "edge", "qq", "random", "randomized"
        }

    def clean_host(self, value: str) -> str:
        if not value:
            return ""
        value = unquote(value)
        md = re.match(r'\[(.*?)\]\((.*?)\)', value)
        if md:
            return md.group(1)
        value = value.replace("http://", "")
        value = value.replace("https://", "")
        value = value.strip("/")
        return value

    def read_config_file(self, filepath):
        if not os.path.exists(filepath):
            return []
        configs = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    configs.append(line)
        return configs

    def get_original_tag(self, config_url):
        try:
            if config_url.startswith('ss://'):
                parts = config_url.split('#')
                if len(parts) > 1:
                    return unquote(parts[1]) or ""
                return ""
            elif config_url.startswith('hysteria2://') or config_url.startswith('hy2://'):
                url = urlparse(config_url)
                return unquote(url.fragment) if url.fragment else ""
            elif config_url.startswith('vmess://'):
                try:
                    decoded = base64.b64decode(config_url.replace('vmess://', '')).decode('utf-8')
                    vmess_config = json.loads(decoded)
                    return vmess_config.get('ps', "")
                except:
                    return ""
            elif config_url.startswith('trojan://'):
                url = urlparse(config_url)
                return unquote(url.fragment) if url.fragment else ""
            else:
                url = urlparse(config_url)
                return unquote(url.fragment) if url.fragment else ""
        except:
            return ""

    def safe_b64_decode(self, data: str) -> Optional[str]:
        try:
            data = data.replace("-", "+").replace("_", "/")
            data += "=" * (-len(data) % 4)
            return base64.b64decode(data).decode("utf-8", errors="ignore")
        except:
            return None

    def get_first(self, qs: Dict, key: str, default: Any = None) -> Any:
        values = qs.get(key, [])
        return values[0] if values else default

    def extract_port(self, config_str):
        try:
            if config_str.startswith('vmess://'):
                raw = config_str[8:]
                raw += '=' * (-len(raw) % 4)
                data = json.loads(base64.b64decode(raw).decode('utf-8'))
                return int(data.get('port', 0))
            elif config_str.startswith('ss://'):
                p = urlparse(config_str)
                return p.port
            elif config_str.startswith('vless://'):
                p = urlparse(config_str)
                return p.port
            elif config_str.startswith('trojan://'):
                p = urlparse(config_str)
                return p.port
            elif config_str.startswith('hysteria2://') or config_str.startswith('hy2://'):
                p = urlparse(config_str)
                return p.port
            elif config_str.startswith('hysteria://'):
                p = urlparse(config_str)
                return p.port
            elif config_str.startswith('tuic://'):
                p = urlparse(config_str)
                return p.port
            elif config_str.startswith('wireguard://'):
                p = urlparse(config_str)
                return p.port
            else:
                return None
        except:
            return None

    def build_tls(self, qs: Dict, host: str) -> Optional[Dict]:
        security = self.get_first(qs, "security", "none")
        if security not in ("tls", "reality"):
            return None
        fp = self.get_first(qs, "fp", "chrome")
        if fp not in self.allowed_fp:
            fp = "chrome"
        tls = {
            "enabled": True,
            "server_name": self.clean_host(self.get_first(qs, "sni", host)),
            "insecure": True,
            "utls": {
                "enabled": True,
                "fingerprint": fp
            }
        }
        alpn = self.get_first(qs, "alpn")
        if alpn:
            tls["alpn"] = [
                unquote(a.strip())
                for a in alpn.split(",")
                if a.strip()
            ]
        if security == "reality":
            pbk = self.get_first(qs, "pbk")
            if not pbk:
                return None
            reality = {
                "enabled": True,
                "public_key": pbk
            }
            sid = self.get_first(qs, "sid")
            if sid:
                reality["short_id"] = sid.lower()
            tls["reality"] = reality
        return tls

    def build_transport_vless(self, qs: Dict, host: str) -> Optional[Dict]:
        network = self.get_first(qs, "type", "tcp")
        if network == "ws":
            path = unquote(self.get_first(qs, "path", "/"))
            if path and not path.startswith("/"):
                path = "/" + path
            headers = {}
            host_header = self.clean_host(self.get_first(qs, "host", host))
            if host_header:
                headers["Host"] = host_header
            return {
                "type": "ws",
                "path": path,
                "headers": headers
            }
        elif network == "grpc":
            return {
                "type": "grpc",
                "service_name": unquote(self.get_first(qs, "serviceName", "GunService"))
            }
        elif network == "http":
            return {
                "type": "http",
                "host": [self.clean_host(self.get_first(qs, "host", host))],
                "path": unquote(self.get_first(qs, "path", "/"))
            }
        return None

    def build_transport_vmess(self, c: Dict) -> Optional[Dict]:
        network = c.get("net", "tcp")
        if network == "ws":
            path = unquote(c.get("path", "/"))
            if path and not path.startswith("/"):
                path = "/" + path
            headers = {}
            host_header = self.clean_host(c.get("host", c["add"]))
            if host_header:
                headers["Host"] = host_header
            return {
                "type": "ws",
                "path": path,
                "headers": headers
            }
        elif network in ("h2", "http"):
            return {
                "type": "http",
                "host": [self.clean_host(c.get("host", c["add"]))],
                "path": unquote(c.get("path", "/"))
            }
        elif network == "grpc":
            return {
                "type": "grpc",
                "service_name": unquote(c.get("path", "GunService").lstrip("/"))
            }
        return None

    def build_transport_trojan(self, qs: Dict, host: str) -> Optional[Dict]:
        network = self.get_first(qs, "type", "tcp")
        if network == "ws":
            path = unquote(self.get_first(qs, "path", "/"))
            if path and not path.startswith("/"):
                path = "/" + path
            headers = {}
            host_header = self.clean_host(self.get_first(qs, "sni", host))
            if host_header:
                headers["Host"] = host_header
            return {
                "type": "ws",
                "path": path,
                "headers": headers
            }
        elif network == "grpc":
            return {
                "type": "grpc",
                "service_name": unquote(self.get_first(qs, "serviceName", "GunService"))
            }
        return None

    def decode_ss_config(self, ss_url: str) -> Optional[Dict]:
        try:
            if not ss_url.startswith("ss://"):
                return None

            raw = ss_url[5:]
            raw = raw.split("#")[0]
            raw = raw.split("?")[0]
            name = unquote(ss_url.split("#", 1)[1]) if "#" in ss_url else ""

            def build_result(method, password, server, port):
                if not method or not password or not server or not port:
                    return None
                if method not in self.allowed_ss_ciphers:
                    return None
                if not str(port).isdigit():
                    return None
                password = str(password).strip()
                if len(password) < 2:
                    return None
                return {
                    "method": method,
                    "password": password,
                    "server": server,
                    "port": int(port),
                    "name": name
                }

            try:
                padding = "=" * ((4 - len(raw) % 4) % 4)
                decoded = base64.b64decode(raw + padding).decode("utf-8")
                if "@" in decoded:
                    creds, server_port = decoded.rsplit("@", 1)
                    if ":" in creds and ":" in server_port:
                        method, password = creds.split(":", 1)
                        server, port = server_port.rsplit(":", 1)
                        result = build_result(method, password, server, port)
                        if result:
                            return result
            except:
                pass

            if "@" in raw:
                encoded_part, server_port = raw.rsplit("@", 1)
                try:
                    padding = "=" * ((4 - len(encoded_part) % 4) % 4)
                    decoded = base64.b64decode(encoded_part + padding).decode("utf-8")
                    if ":" in decoded:
                        method, password = decoded.split(":", 1)
                        server, port = server_port.rsplit(":", 1)
                        result = build_result(method, password, server, port)
                        if result:
                            return result
                except:
                    pass

            if "@" in raw and ":" in raw:
                creds, server_port = raw.rsplit("@", 1)
                if ":" in creds and ":" in server_port:
                    method, password = creds.split(":", 1)
                    server, port = server_port.rsplit(":", 1)
                    result = build_result(method, password, server, port)
                    if result:
                        return result

            return None
        except:
            return None

    def decode_vmess(self, raw: str) -> Optional[Dict]:
        try:
            data = raw.replace("vmess://", "")
            decoded = base64.b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", errors="ignore")
            obj = json.loads(decoded)
            if "add" not in obj and "host" in obj:
                obj["add"] = obj["host"]
            return obj
        except:
            return None

    def vless_to_singbox(self, index: int, raw: str) -> Optional[Dict]:
        try:
            if not raw.startswith("vless://"):
                return None
            parsed = urlparse(raw)
            qs = parse_qs(parsed.query)
            if not all([parsed.hostname, parsed.port, parsed.username]):
                return None
            if not self.uuid_re.match(parsed.username):
                return None
            name = f"ARISTA #{index + 1}"
            config = {
                "type": "vless",
                "tag": name,
                "server": parsed.hostname,
                "server_port": int(parsed.port),
                "uuid": parsed.username,
                "domain_resolver": "google"
            }
            tls = self.build_tls(qs, parsed.hostname)
            if tls:
                config["tls"] = tls
            flow = self.get_first(qs, "flow")
            if flow in ["xtls-rprx-vision", "xtls-rprx-udp443", "xtls-rprx"]:
                config["flow"] = flow
            packet_encoding = self.get_first(qs, "packetEncoding")
            if packet_encoding:
                config["packet_encoding"] = packet_encoding
            transport = self.build_transport_vless(qs, parsed.hostname)
            if transport:
                config["transport"] = transport
            return config
        except Exception as e:
            return None

    def ss_to_singbox(self, index: int, raw: str) -> Optional[Dict]:
        try:
            if not raw.startswith("ss://"):
                return None

            d = self.decode_ss_config(raw)
            if not d:
                return None

            password = str(d.get("password", "")).strip()
            if not password or len(password) < 2:
                return None

            method = d.get("method", "")
            if method not in self.allowed_ss_ciphers:
                return None

            server = d.get("server", "")
            port = d.get("port", None)

            if not server or not port or not str(port).isdigit():
                return None

            return {
                "type": "shadowsocks",
                "tag": f"ARISTA #{index + 1}",
                "server": server,
                "server_port": int(port),
                "method": method,
                "password": password,
                "domain_resolver": "google"
            }
        except:
            return None

    def vmess_to_singbox(self, index: int, raw: str) -> Optional[Dict]:
        try:
            if not raw.startswith("vmess://"):
                return None
            c = self.decode_vmess(raw)
            if not c:
                return None
            if not all(k in c for k in ("add", "port", "id")):
                return None
            name = f"ARISTA #{index + 1}"
            config = {
                "type": "vmess",
                "tag": name,
                "server": c["add"],
                "server_port": int(c["port"]),
                "uuid": c["id"],
                "security": c.get("scy", "auto"),
                "domain_resolver": "google"
            }
            aid = int(c.get("aid", 0))
            if aid > 0:
                config["alter_id"] = aid
            tls_qs = {}
            if c.get("tls") == "tls":
                tls_qs["security"] = ["tls"]
                if c.get("sni"):
                    tls_qs["sni"] = [c["sni"]]
                if c.get("fp"):
                    tls_qs["fp"] = [c["fp"]]
                if c.get("alpn"):
                    tls_qs["alpn"] = [c["alpn"]]
            tls = self.build_tls(tls_qs, c["add"])
            if tls:
                config["tls"] = tls
            transport = self.build_transport_vmess(c)
            if transport:
                config["transport"] = transport
            return config
        except Exception as e:
            return None

    def trojan_to_singbox(self, index: int, raw: str) -> Optional[Dict]:
        try:
            if not raw.startswith("trojan://"):
                return None
            p = urlparse(raw)
            q = parse_qs(p.query)
            if not all([p.hostname, p.port, p.username]):
                return None
            name = f"ARISTA #{index + 1}"
            config = {
                "type": "trojan",
                "tag": name,
                "server": p.hostname,
                "server_port": int(p.port),
                "password": unquote(p.username),
                "domain_resolver": "google"
            }
            tls = self.build_tls(q, p.hostname)
            if tls:
                config["tls"] = tls
            transport = self.build_transport_trojan(q, p.hostname)
            if transport:
                config["transport"] = transport
            return config
        except Exception as e:
            return None

    def hysteria2_to_singbox(self, index: int, raw: str) -> Optional[Dict]:
        try:
            if not (raw.startswith("hysteria2://") or raw.startswith("hy2://")):
                return None
            raw = raw.replace("hy2://", "hysteria2://")
            p = urlparse(raw)
            q = parse_qs(p.query)
            if not all([p.hostname, p.port]):
                return None
            name = f"ARISTA #{index + 1}"
            tls_config = self.build_tls(q, p.hostname)
            if not tls_config:
                tls_config = {
                    "enabled": True,
                    "server_name": p.hostname,
                    "insecure": True,
                }
            config = {
                "type": "hysteria2",
                "tag": name,
                "server": p.hostname,
                "server_port": int(p.port),
                "password": unquote(p.username or ""),
                "domain_resolver": "google",
                "tls": tls_config
            }
            obfs = self.get_first(q, "obfs")
            obfs_pass = self.get_first(q, "obfs-password")
            if obfs and obfs_pass:
                config["obfs"] = {
                    "type": obfs,
                    "password": unquote(obfs_pass)
                }
            up = self.get_first(q, "up")
            down = self.get_first(q, "down")
            if up:
                config["up"] = up
            if down:
                config["down"] = down
            ports = self.get_first(q, "ports")
            if ports:
                config["ports"] = ports
            return config
        except Exception as e:
            return None

    def validate_outbounds(self, proxies):
        valid = []
        seen = set()
        for p in proxies:
            if not isinstance(p, dict):
                continue
            if "type" not in p or "tag" not in p:
                continue
            if p["type"] in ["vless", "vmess", "trojan", "shadowsocks", "hysteria2"]:
                p_copy = p.copy()
                if "tag" in p_copy:
                    p_copy["tag"] = re.sub(r'\s*#\s*\d+$', '', p_copy["tag"]).strip()
                p_copy.pop("domain_resolver", None)
                key = json.dumps(p_copy, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    valid.append(p)
        return valid

    def _safe_final(self, proxies: List[Dict]) -> str:
        for p in proxies:
            if p.get("tag") and "ARISTA AUTO BEST" in p.get("tag"):
                return p["tag"]
        for p in proxies:
            if p.get("tag"):
                return p["tag"]
        return "direct"

    def build_proxy_groups(self, all_proxies):
        proxy_tags = [p["tag"] for p in all_proxies if p.get("tag")]

        if not proxy_tags:
            return []

        return [
            {
                "type": "urltest",
                "tag": "\U0001f680 ARISTA AUTO BEST",
                "outbounds": proxy_tags,
                "url": "http://www.gstatic.com/generate_204",
                "interval": "2m",
                "tolerance": 30,
                "idle_timeout": "20m",
                "interrupt_exist_connections": True
            }
        ]

    def convert_config_to_singbox(self, config_str: str, index: int) -> Optional[Dict]:
        if config_str.startswith('vless://'):
            return self.vless_to_singbox(index, config_str)
        elif config_str.startswith('ss://'):
            return self.ss_to_singbox(index, config_str)
        elif config_str.startswith('hysteria2://') or config_str.startswith('hy2://'):
            return self.hysteria2_to_singbox(index, config_str)
        elif config_str.startswith('vmess://'):
            return self.vmess_to_singbox(index, config_str)
        elif config_str.startswith('trojan://'):
            return self.trojan_to_singbox(index, config_str)
        else:
            return None

    def build_singbox_config(self, proxies: List[Dict]) -> Dict:
        if not proxies:
            return {
                "log": {
                    "level": "info",
                    "timestamp": True
                },
                "inbounds": [],
                "outbounds": [
                    {
                        "type": "direct",
                        "tag": "direct"
                    }
                ],
                "route": {
                    "final": "direct",
                    "rules": []
                }
            }

        cleaned_proxies = self.validate_outbounds(proxies)

        for idx, p in enumerate(cleaned_proxies):
            if "tag" in p:
                p["tag"] = f"ARISTA #{idx + 1}"

        proxy_groups = self.build_proxy_groups(cleaned_proxies)

        return {
            "log": {
                "level": "info",
                "timestamp": True
            },

            "dns": {
                "servers": [
                    {
                        "type": "udp",
                        "tag": "google",
                        "server": "8.8.8.8"
                    },
                    {
                        "type": "udp",
                        "tag": "cloudflare",
                        "server": "1.1.1.1"
                    }
                ],
                "rules": [],
                "final": "google"
            },

            "inbounds": [
                {
                    "type": "tun",
                    "tag": "tun-in",
                    "interface_name": "singbox-tun",
                    "address": [
                        "172.19.0.1/30"
                    ],
                    "auto_route": True,
                    "strict_route": True,
                    "stack": "system",
                    "sniff": False
                }
            ],

            "outbounds": (
                cleaned_proxies
                + [
                    {
                        "type": "direct",
                        "tag": "direct"
                    },
                    {
                        "type": "block",
                        "tag": "block"
                    }
                ]
                + proxy_groups
            ),

            "route": {
                "auto_detect_interface": True,
                "default_domain_resolver": "google",
                "final": "\U0001f680 ARISTA AUTO BEST" if proxy_groups else self._safe_final(cleaned_proxies),
                "rules": [
                    {
                        "protocol": "dns",
                        "outbound": "direct"
                    }
                ]
            }
        }

    def convert_port_based_configs(self, source_dir, output_dir, source_name):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        port_output_dir = os.path.join('port.json', source_name)
        os.makedirs(port_output_dir, exist_ok=True)

        all_port_configs = {port: [] for port in self.port_tiers}
        other_ports = []

        for category in self.categories:
            cat_dir = os.path.join(source_dir, category)
            if not os.path.exists(cat_dir):
                continue
            for tier_file in os.listdir(cat_dir):
                if tier_file.endswith('.txt'):
                    filepath = os.path.join(cat_dir, tier_file)
                    configs = self.read_config_file(filepath)
                    for config in configs:
                        port = self.extract_port(config)
                        if port in self.port_tiers:
                            all_port_configs[port].append(config)
                        else:
                            other_ports.append(config)

        for port, configs in all_port_configs.items():
            if configs:
                converted_configs = []
                for idx, config in enumerate(configs):
                    converted = self.convert_config_to_singbox(config, idx)
                    if converted:
                        converted_configs.append(converted)
                if converted_configs:
                    full_config = self.build_singbox_config(converted_configs)
                    output_filename = os.path.join(port_output_dir, f'port_{port}.json')
                    with open(output_filename, 'w', encoding='utf-8') as f:
                        f.write(f"// {source_name.upper()} - Port {port}\n")
                        f.write(f"// Updated: {timestamp}\n")
                        f.write(f"// Count: {len(converted_configs)}\n\n")
                        json.dump(full_config, f, indent=2, ensure_ascii=False)

        if other_ports:
            converted_configs = []
            for idx, config in enumerate(other_ports):
                converted = self.convert_config_to_singbox(config, idx)
                if converted:
                    converted_configs.append(converted)
            if converted_configs:
                full_config = self.build_singbox_config(converted_configs)
                output_filename = os.path.join(port_output_dir, 'other_ports.json')
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(f"// {source_name.upper()} - Other Ports\n")
                    f.write(f"// Updated: {timestamp}\n")
                    f.write(f"// Count: {len(converted_configs)}\n\n")
                    json.dump(full_config, f, indent=2, ensure_ascii=False)

        all_configs = []
        for configs in all_port_configs.values():
            all_configs.extend(configs)
        all_configs.extend(other_ports)
        if all_configs:
            converted_configs = []
            for idx, config in enumerate(all_configs):
                converted = self.convert_config_to_singbox(config, idx)
                if converted:
                    converted_configs.append(converted)
            if converted_configs:
                full_config = self.build_singbox_config(converted_configs)
                output_filename = os.path.join(port_output_dir, 'all_ports.json')
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(f"// {source_name.upper()} - All Ports\n")
                    f.write(f"// Updated: {timestamp}\n")
                    f.write(f"// Count: {len(converted_configs)}\n\n")
                    json.dump(full_config, f, indent=2, ensure_ascii=False)

    def convert_source_configs(self, source_dir, output_dir, source_name):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        os.makedirs(output_dir, exist_ok=True)
        for category in self.categories:
            cat_dir = os.path.join(source_dir, category)
            if not os.path.exists(cat_dir):
                continue
            all_configs = []
            tier_files = {}
            for tier_file in os.listdir(cat_dir):
                if tier_file.endswith('.txt'):
                    filepath = os.path.join(cat_dir, tier_file)
                    configs = self.read_config_file(filepath)
                    if configs:
                        tier_name = tier_file.replace('.txt', '')
                        tier_files[tier_name] = configs
                        all_configs.extend(configs)
            if not all_configs:
                continue
            converted_by_tier = {}
            for tier_name, configs in tier_files.items():
                converted_configs = []
                for idx, config in enumerate(configs):
                    converted = self.convert_config_to_singbox(config, idx)
                    if converted:
                        converted_configs.append(converted)
                if converted_configs:
                    converted_by_tier[tier_name] = converted_configs
            if not converted_by_tier:
                continue
            output_cat_dir = os.path.join(output_dir, category)
            os.makedirs(output_cat_dir, exist_ok=True)
            for tier_name, converted_configs in converted_by_tier.items():
                full_config = self.build_singbox_config(converted_configs)
                output_filename = os.path.join(output_cat_dir, f"{tier_name}.json")
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(f"// {source_name.upper()} - {category.upper()} - Tier {tier_name}\n")
                    f.write(f"// Updated: {timestamp}\n")
                    f.write(f"// Count: {len(converted_configs)}\n\n")
                    json.dump(full_config, f, indent=2, ensure_ascii=False)
        self.convert_all_tiers(source_dir, output_dir, source_name)
        self.generate_summary_json(source_dir, output_dir, source_name)
        self.convert_port_based_configs(source_dir, output_dir, source_name)

    def convert_all_tiers(self, source_dir, output_dir, source_name):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        all_dir = os.path.join(source_dir, 'ALL')
        if not os.path.exists(all_dir):
            return
        output_all_dir = os.path.join(output_dir, 'ALL')
        os.makedirs(output_all_dir, exist_ok=True)
        for tier_file in os.listdir(all_dir):
            if tier_file.endswith('.txt'):
                filepath = os.path.join(all_dir, tier_file)
                configs = self.read_config_file(filepath)
                if not configs:
                    continue
                tier_name = tier_file.replace('.txt', '')
                converted_configs = []
                for idx, config in enumerate(configs):
                    converted = self.convert_config_to_singbox(config, idx)
                    if converted:
                        converted_configs.append(converted)
                if not converted_configs:
                    continue
                full_config = self.build_singbox_config(converted_configs)
                output_filename = os.path.join(output_all_dir, f"{tier_name}.json")
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(f"// {source_name.upper()} - ALL - Tier {tier_name}\n")
                    f.write(f"// Updated: {timestamp}\n")
                    f.write(f"// Count: {len(converted_configs)}\n\n")
                    json.dump(full_config, f, indent=2, ensure_ascii=False)

    def generate_summary_json(self, source_dir, output_dir, source_name):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        summary_data = {
            'source': source_name.upper(),
            'updated': timestamp,
            'categories': {}
        }
        for category in self.categories:
            cat_dir = os.path.join(source_dir, category)
            if os.path.exists(cat_dir):
                category_data = {}
                for tier_file in os.listdir(cat_dir):
                    if tier_file.endswith('.txt'):
                        tier_name = tier_file.replace('.txt', '')
                        filepath = os.path.join(cat_dir, tier_file)
                        configs = self.read_config_file(filepath)
                        category_data[tier_name] = len(configs)
                if category_data:
                    summary_data['categories'][category] = category_data
        all_dir = os.path.join(source_dir, 'ALL')
        if os.path.exists(all_dir):
            all_data = {}
            for tier_file in os.listdir(all_dir):
                if tier_file.endswith('.txt'):
                    tier_name = tier_file.replace('.txt', '')
                    filepath = os.path.join(all_dir, tier_file)
                    configs = self.read_config_file(filepath)
                    all_data[tier_name] = len(configs)
            if all_data:
                summary_data['ALL'] = all_data
        output_filename = os.path.join(output_dir, f"{source_name}_summary.json")
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(f"// {source_name.upper()} JSON Conversion Summary\n")
            f.write(f"// Updated: {timestamp}\n\n")
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

    def convert_all(self):
        sources = [
            ('configs.txt/combined', 'config.json/combined', 'combined'),
            ('configs.txt/telegram', 'config.json/telegram', 'telegram'),
            ('configs.txt/github', 'config.json/github', 'github')
        ]
        for source_dir, output_dir, source_name in sources:
            if os.path.exists(source_dir):
                self.convert_source_configs(source_dir, output_dir, source_name)

def main():
    print("=" * 60)
    print("CONFIG TO JSON (Sing-Box) CONVERTER")
    print("=" * 60)
    try:
        converter = ConfigToJSONConverter()
        converter.convert_all()
        print("\n✅ JSON conversion completed successfully")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
