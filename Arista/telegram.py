import requests
import re
import json
import hashlib
import base64
import uuid
import random
import time
import os
import asyncio
import aiohttp
import socket
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse, parse_qs, unquote, quote
from bs4 import BeautifulSoup
from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity=10000):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def clear(self):
        self.cache.clear()

    def __len__(self):
        return len(self.cache)


class TelegramConfigExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,image/webp,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })

        self.channels = self.load_channels()

        self.config_patterns = [
            r"(vmess://[A-Za-z0-9+/=_-]+)",
            r'''(vless://[^\s<>"'`]+)''',
            r'''(trojan://[^\s<>"'`]+)''',
            r'''(ss://[^\s<>"'`]+)''',
            r'''(hysteria2://[^\s<>"'`]+)''',
            r'''(hysteria://[^\s<>"'`]+)''',
            r'''(hy2://[^\s<>"'`]+)''',
            r'''(tuic://[^\s<>"'`]+)''',
            r'''(wireguard://[^\s<>"'`]+)'''
        ]

        self.dead_cache = {}
        self.failed_counter = {}
        self.last_post_cache = {}
        self.permanent_blacklist = {}
        self.temp_suspended_cache = {}

        cache_dir = ".cache/telegram"
        os.makedirs(cache_dir, exist_ok=True)

        self.cache_file = os.path.join(
            cache_dir,
            "dead_cache.json"
        )
        self.permanent_blacklist_file = os.path.join(
            cache_dir,
            "permanent_blacklist.json"
        )
        self.temp_suspend_file = os.path.join(
            cache_dir,
            "temp_suspend.json"
        )
        self.last_seen_file = os.path.join(
            cache_dir,
            "last_seen.json"
        )

        self.health_dir = "health"
        self.health_file = os.path.join(
            self.health_dir,
            "telegram_health.json"
        )
        self.health_max_failures = 3
        self.health_timeout = 3
        self.health_concurrency = 200
        self.health_state_retention = 86400

        self.health_stats = {
            "checked": 0,
            "healthy": 0,
            "unstable": 0,
            "dead": 0,
            "unchecked": 0
        }

        self.config_hash_cache = LRUCache(
            capacity=10000
        )

        self.load_dead_cache()
        self.load_permanent_blacklist()
        self.load_temp_suspend()
        self.load_last_seen()

        if os.path.exists("stats.json"):
            try:
                os.remove("stats.json")
            except OSError:
                pass

    def load_channels(self):
        channels_json = os.environ.get("CHANNELS_JSON")

        if channels_json:
            try:
                data = json.loads(channels_json)

                if isinstance(data, list):
                    return list({
                        str(item).strip()
                        for item in data
                        if str(item).strip()
                    })

            except (
                json.JSONDecodeError,
                TypeError,
                ValueError
            ):
                pass

        try:
            channels_file = "Entry/channels.json"

            if not os.path.exists(channels_file):
                return []

            with open(
                channels_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if isinstance(data, list):
                return list({
                    str(item).strip()
                    for item in data
                    if str(item).strip()
                })

            if isinstance(data, dict):
                channels = data.get("channels", [])

                if isinstance(channels, list):
                    return list({
                        str(item).strip()
                        for item in channels
                        if str(item).strip()
                    })

            return []

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):
            return []

    def load_dead_cache(self):
        try:
            if not os.path.exists(self.cache_file):
                return

            with open(
                self.cache_file,
                "r",
                encoding="utf-8"
            ) as file:
                cache_data = json.load(file)

            if not isinstance(cache_data, dict):
                return

            for url, timestamp_str in cache_data.items():
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str
                    )
                    self.dead_cache[str(url)] = timestamp
                except (
                    TypeError,
                    ValueError
                ):
                    continue

        except (
            OSError,
            json.JSONDecodeError
        ):
            self.dead_cache = {}

    def save_dead_cache(self):
        try:
            directory = os.path.dirname(self.cache_file)
            os.makedirs(directory, exist_ok=True)

            cache_data = {
                url: timestamp.isoformat()
                for url, timestamp in self.dead_cache.items()
            }

            with open(
                self.cache_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    cache_data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

        except OSError:
            pass

    def load_permanent_blacklist(self):
        try:
            if not os.path.exists(
                self.permanent_blacklist_file
            ):
                return

            with open(
                self.permanent_blacklist_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return

            for url, timestamp_str in data.items():
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str
                    )
                    self.permanent_blacklist[str(url)] = timestamp
                except (
                    TypeError,
                    ValueError
                ):
                    continue

        except (
            OSError,
            json.JSONDecodeError
        ):
            self.permanent_blacklist = {}

    def save_permanent_blacklist(self):
        try:
            directory = os.path.dirname(
                self.permanent_blacklist_file
            )
            os.makedirs(directory, exist_ok=True)

            data = {
                url: timestamp.isoformat()
                for url, timestamp
                in self.permanent_blacklist.items()
            }

            with open(
                self.permanent_blacklist_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

        except OSError:
            pass

    def load_temp_suspend(self):
        try:
            if not os.path.exists(self.temp_suspend_file):
                return

            with open(
                self.temp_suspend_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return

            for url, timestamp_str in data.items():
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str
                    )
                    self.temp_suspended_cache[str(url)] = timestamp
                except (
                    TypeError,
                    ValueError
                ):
                    continue

        except (
            OSError,
            json.JSONDecodeError
        ):
            self.temp_suspended_cache = {}

    def save_temp_suspend(self):
        try:
            directory = os.path.dirname(
                self.temp_suspend_file
            )
            os.makedirs(directory, exist_ok=True)

            data = {
                url: timestamp.isoformat()
                for url, timestamp
                in self.temp_suspended_cache.items()
            }

            with open(
                self.temp_suspend_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

        except OSError:
            pass

    def load_last_seen(self):
        try:
            if not os.path.exists(self.last_seen_file):
                return

            with open(
                self.last_seen_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return

            for url, timestamp_str in data.items():
                try:
                    timestamp = datetime.fromisoformat(
                        timestamp_str
                    )
                    self.last_post_cache[str(url)] = timestamp
                except (
                    TypeError,
                    ValueError
                ):
                    continue

        except (
            OSError,
            json.JSONDecodeError
        ):
            self.last_post_cache = {}

    def save_last_seen(self):
        try:
            directory = os.path.dirname(
                self.last_seen_file
            )
            os.makedirs(directory, exist_ok=True)

            data = {
                url: timestamp.isoformat()
                for url, timestamp
                in self.last_post_cache.items()
            }

            with open(
                self.last_seen_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

        except OSError:
            pass

    def update_dead_cache(self, url):
        now = datetime.now(timezone.utc)

        self.failed_counter[url] = (
            self.failed_counter.get(url, 0) + 1
        )

        if self.failed_counter[url] >= 3:
            self.dead_cache[url] = now
            self.save_dead_cache()

            print(
                "  → Added to dead cache "
                f"(failed {self.failed_counter[url]} times)"
            )

    def should_skip_channel(self, url):
        if url in self.permanent_blacklist:
            print("  → Permanently blacklisted")
            return True

        if url in self.temp_suspended_cache:
            suspend_time = self.temp_suspended_cache[url]
            time_since_suspend = (
                datetime.now(timezone.utc)
                - suspend_time
            )

            if time_since_suspend < timedelta(days=7):
                remaining = (
                    timedelta(days=7)
                    - time_since_suspend
                )

                print(
                    "  → Temporarily suspended "
                    f"({remaining.days}d "
                    f"{remaining.seconds // 3600}h remaining)"
                )

                return True

            del self.temp_suspended_cache[url]
            self.permanent_blacklist[url] = (
                datetime.now(timezone.utc)
            )

            self.save_temp_suspend()
            self.save_permanent_blacklist()

            print(
                "  → Moved to permanent blacklist "
                "(no posts for 7+ days)"
            )

            return True

        if url in self.dead_cache:
            last_fail_time = self.dead_cache[url]
            time_since_fail = (
                datetime.now(timezone.utc)
                - last_fail_time
            )

            if time_since_fail < timedelta(hours=24):
                print(
                    "  → Skipped "
                    f"(in dead cache, "
                    f"{int(time_since_fail.total_seconds() / 3600)}h ago)"
                )

                return True

            del self.dead_cache[url]
            self.failed_counter.pop(url, None)
            self.save_dead_cache()

        return False

    def adaptive_delay(self):
        time.sleep(random.uniform(0.4, 1.2))

    def fetch_page(self, url):
        try:
            response = self.session.get(
                url,
                timeout=20
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return ""

    def get_last_post_time(self, soup):
        try:
            time_tags = soup.find_all("time")

            if not time_tags:
                return None

            latest_time = None

            for time_tag in time_tags:
                dt_str = time_tag.get("datetime")

                if not dt_str:
                    continue

                try:
                    post_time = datetime.fromisoformat(
                        dt_str.replace("Z", "+00:00")
                    )

                    if (
                        latest_time is None
                        or post_time > latest_time
                    ):
                        latest_time = post_time

                except ValueError:
                    continue

            return latest_time

        except Exception as exc:
            print(
                f"Error parsing last post time: {exc}"
            )
            return None

    def extract_from_soup(self, soup):
        configs = []
        elements = soup.find_all(
            ["code", "pre", "div"]
        )

        for element in elements:
            text = element.get_text(
                " ",
                strip=False
            )

            for pattern in self.config_patterns:
                matches = re.findall(
                    pattern,
                    text,
                    re.IGNORECASE
                )

                for match in matches:
                    cleaned = self.clean_config(match)

                    if cleaned:
                        configs.append(cleaned)

        return configs

    def clean_config(self, config_str):
        if not config_str:
            return ""

        config_str = str(config_str)

        config_str = re.sub(
            r"[\n\r\t]+",
            "",
            config_str
        )

        config_str = re.sub(
            r"\s+",
            "",
            config_str
        )

        config_str = config_str.strip(
            ' \'"<>`.,;:!?،؛'
        )

        config_str = re.sub(
            r"[\]\[{}()]+$",
            "",
            config_str
        )

        if "#" in config_str:
            base, fragment = config_str.split(
                "#",
                1
            )

            base = base.rstrip(
                ' \'"<>`.,;:!?،؛'
            )

            fragment = fragment.strip()

            fragment = re.split(
                r"\s+(?:https?://|t\.me/|telegram\.me/)",
                fragment,
                maxsplit=1,
                flags=re.IGNORECASE
            )[0]

            fragment = fragment.strip(
                ' \'"<>`'
            )

            if base:
                config_str = base

                if fragment:
                    config_str += "#" + fragment

        return config_str

    def decode_vmess(self, config_str):
        try:
            base64_part = config_str[8:].strip()

            padding = "=" * (
                (-len(base64_part)) % 4
            )

            decoded = base64.urlsafe_b64decode(
                base64_part + padding
            ).decode("utf-8")

            data = json.loads(decoded)

            if isinstance(data, dict):
                return data

        except (
            ValueError,
            TypeError,
            UnicodeDecodeError,
            json.JSONDecodeError
        ):
            pass

        return None

    def standardize_ss(self, config_str):
        try:
            if not config_str.startswith("ss://"):
                return config_str

            config_str = self.clean_config(
                config_str
            )

            parts = config_str.split(
                "#",
                1
            )

            base_part = parts[0][5:]

            if "@" in base_part:
                encoded_part, server_part = (
                    base_part.split("@", 1)
                )

                try:
                    padding = "=" * (
                        (-len(encoded_part)) % 4
                    )

                    decoded = base64.urlsafe_b64decode(
                        encoded_part + padding
                    ).decode("utf-8")

                    if "@" in decoded:
                        method_pass, server = (
                            decoded.split("@", 1)
                        )

                        encoded_mp = (
                            base64.urlsafe_b64encode(
                                method_pass.encode()
                            )
                            .decode()
                            .rstrip("=")
                        )

                        result = (
                            f"ss://{encoded_mp}@{server}"
                        )

                        if (
                            len(parts) == 2
                            and parts[1]
                        ):
                            result += "#" + quote(
                                unquote(parts[1]),
                                safe=""
                            )

                        return result

                except (
                    ValueError,
                    TypeError,
                    UnicodeDecodeError
                ):
                    pass

            padding = "=" * (
                (-len(base_part)) % 4
            )

            try:
                decoded = base64.urlsafe_b64decode(
                    base_part + padding
                ).decode("utf-8")

                if "@" in decoded:
                    method_pass, server = (
                        decoded.split("@", 1)
                    )

                    encoded_mp = (
                        base64.urlsafe_b64encode(
                            method_pass.encode()
                        )
                        .decode()
                        .rstrip("=")
                    )

                    result = (
                        f"ss://{encoded_mp}@{server}"
                    )

                    if len(parts) == 2 and parts[1]:
                        result += "#" + quote(
                            unquote(parts[1]),
                            safe=""
                        )

                    return result

            except (
                ValueError,
                TypeError,
                UnicodeDecodeError
            ):
                pass

            return config_str

        except Exception:
            return config_str

    def extract_host_port(self, parsed):
        try:
            host = parsed.hostname

            if not host:
                return "", 0

            port = parsed.port

            if not port:
                return host, 0

            if port < 1 or port > 65535:
                return "", 0

            return host, port

        except ValueError:
            return "", 0

    def validate_host(self, host):
        if not host:
            return False

        host = str(host).strip()

        if len(host) > 253:
            return False

        if any(
            char.isspace()
            for char in host
        ):
            return False

        if (
            host.startswith(".")
            or host.endswith(".")
            or ".." in host
        ):
            return False

        if ":" in host:
            ipv6_pattern = re.compile(
                r"^[0-9a-fA-F:]+$"
            )

            return bool(
                ipv6_pattern.fullmatch(host)
            )

        hostname_pattern = re.compile(
            r"^(?=.{1,253}$)"
            r"(?:[A-Za-z0-9]"
            r"(?:[A-Za-z0-9-]{0,61}"
            r"[A-Za-z0-9])?\.)*"
            r"[A-Za-z0-9]"
            r"(?:[A-Za-z0-9-]{0,61}"
            r"[A-Za-z0-9])?$"
        )

        return bool(
            hostname_pattern.fullmatch(host)
        )

    def validate_uri_endpoint(
        self,
        config_str,
        require_user=True
    ):
        try:
            parsed = urlparse(config_str)

            if not parsed.scheme:
                return False

            if require_user and not parsed.username:
                return False

            host, port = self.extract_host_port(
                parsed
            )

            if not self.validate_host(host):
                return False

            if port < 1 or port > 65535:
                return False

            return True

        except (
            ValueError,
            TypeError
        ):
            return False

    def validate_vmess_dict(self, config_dict):
        required_keys = [
            "v",
            "ps",
            "add",
            "port",
            "id",
            "aid"
        ]

        if not all(
            key in config_dict
            for key in required_keys
        ):
            return False

        try:
            port = int(
                config_dict["port"]
            )

            if port < 1 or port > 65535:
                return False

            uuid.UUID(
                str(config_dict["id"])
            )

            if not self.validate_host(
                str(config_dict["add"])
            ):
                return False

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            return False

        return True

    def validate_vless(self, config_str):
        try:
            parsed = urlparse(config_str)

            if parsed.scheme.lower() != "vless":
                return False

            if not parsed.username:
                return False

            if not self.validate_host(
                parsed.hostname or ""
            ):
                return False

            if not parsed.port:
                return False

            if parsed.port < 1 or parsed.port > 65535:
                return False

            uuid.UUID(
                unquote(parsed.username)
            )

            return True

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            return False

    def validate_trojan(self, config_str):
        try:
            parsed = urlparse(config_str)

            if parsed.scheme.lower() != "trojan":
                return False

            if not parsed.username:
                return False

            if not self.validate_host(
                parsed.hostname or ""
            ):
                return False

            if not parsed.port:
                return False

            if parsed.port < 1 or parsed.port > 65535:
                return False

            password = unquote(
                parsed.username
            )

            if not password:
                return False

            if any(
                char.isspace()
                for char in password
            ):
                return False

            return True

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            return False

    def validate_hysteria(self, config_str):
        try:
            parsed = urlparse(config_str)

            if parsed.scheme.lower() not in (
                "hysteria",
                "hysteria2",
                "hy2"
            ):
                return False

            if not self.validate_host(
                parsed.hostname or ""
            ):
                return False

            if not parsed.port:
                return False

            if parsed.port < 1 or parsed.port > 65535:
                return False

            return True

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            return False

    def validate_tuic(self, config_str):
        try:
            parsed = urlparse(config_str)

            if parsed.scheme.lower() != "tuic":
                return False

            if not parsed.username:
                return False

            if not self.validate_host(
                parsed.hostname or ""
            ):
                return False

            if not parsed.port:
                return False

            if parsed.port < 1 or parsed.port > 65535:
                return False

            return True

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            return False

    def validate_wireguard(self, config_str):
        try:
            parsed = urlparse(config_str)

            if parsed.scheme.lower() != "wireguard":
                return False

            if not parsed.hostname and not parsed.path:
                return False

            return True

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            return False

    def validate_config(self, config):
        if isinstance(config, dict):
            return self.validate_vmess_dict(
                config
            )

        config_str = self.clean_config(
            config
        )

        if not config_str:
            return False

        if config_str.startswith("vmess://"):
            decoded = self.decode_vmess(
                config_str
            )

            return (
                decoded is not None
                and isinstance(decoded, dict)
                and self.validate_vmess_dict(
                    decoded
                )
            )

        if config_str.startswith("vless://"):
            return self.validate_vless(
                config_str
            )

        if config_str.startswith("trojan://"):
            return self.validate_trojan(
                config_str
            )

        if config_str.startswith("ss://"):
            return self.validate_ss(
                config_str
            )

        if config_str.startswith(
            (
                "hysteria2://",
                "hy2://",
                "hysteria://"
            )
        ):
            return self.validate_hysteria(
                config_str
            )

        if config_str.startswith("tuic://"):
            return self.validate_tuic(
                config_str
            )

        if config_str.startswith(
            "wireguard://"
        ):
            return self.validate_wireguard(
                config_str
            )

        return False

    def validate_ss(self, config_str):
        try:
            config_str = self.standardize_ss(
                config_str
            )

            parsed = urlparse(
                config_str
            )

            if parsed.scheme.lower() != "ss":
                return False

            if not parsed.hostname:
                return False

            if not self.validate_host(
                parsed.hostname
            ):
                return False

            if not parsed.port:
                return False

            if parsed.port < 1 or parsed.port > 65535:
                return False

            if "@" not in parsed.netloc:
                return False

            encoded_method_pass = (
                parsed.username
            )

            if not encoded_method_pass:
                return False

            padding = "=" * (
                (-len(encoded_method_pass)) % 4
            )

            try:
                decoded_mp = (
                    base64.urlsafe_b64decode(
                        encoded_method_pass + padding
                    ).decode("utf-8")
                )

            except (
                ValueError,
                TypeError,
                UnicodeDecodeError
            ):
                return False

            if ":" not in decoded_mp:
                return False

            method, password = (
                decoded_mp.split(":", 1)
            )

            if not method or not password:
                return False

            return True

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            return False

    def encode_fragment(self, fragment):
        if not fragment:
            return ""

        fragment = unquote(
            str(fragment)
        )

        fragment = re.sub(
            r"[\r\n\t]+",
            " ",
            fragment
        )

        fragment = re.sub(
            r"\s+",
            " ",
            fragment
        ).strip()

        fragment = fragment.strip(
            ' "\'<>`'
        )

        if not fragment:
            return ""

        return quote(
            fragment,
            safe=""
        )

    def tag_config(
        self,
        config,
        tag="ARISTA"
    ):
        tag = "ARISTA"

        if isinstance(config, dict):
            config = dict(config)
            config["ps"] = tag

            json_str = json.dumps(
                config,
                separators=(",", ":"),
                ensure_ascii=False
            )

            return (
                "vmess://"
                + base64.b64encode(
                    json_str.encode()
                ).decode()
            )

        config_str = self.clean_config(
            config
        )

        if config_str.startswith("vmess://"):
            decoded = self.decode_vmess(
                config_str
            )

            if decoded and isinstance(
                decoded,
                dict
            ):
                decoded["ps"] = tag

                json_str = json.dumps(
                    decoded,
                    separators=(",", ":"),
                    ensure_ascii=False
                )

                return (
                    "vmess://"
                    + base64.b64encode(
                        json_str.encode()
                    ).decode()
                )

            return config_str

        base = config_str.split(
            "#",
            1
        )[0]

        return f"{base}#{tag}"

    def normalize_config(self, config):
        if isinstance(config, dict):
            return config

        config = self.clean_config(
            config
        )

        if config.startswith("vmess://"):
            vm = self.decode_vmess(
                config
            )

            if vm:
                vm = dict(vm)
                vm.pop("ps", None)
                return vm

            return None

        try:
            parsed = urlparse(config)

            result = {
                "scheme": parsed.scheme.lower(),
                "server": parsed.hostname or "",
                "port": parsed.port or 0,
                "user": unquote(
                    parsed.username or ""
                ),
                "path": unquote(
                    parsed.path or ""
                )
            }

            if parsed.fragment:
                result["fragment"] = unquote(
                    parsed.fragment
                )

            query = parse_qs(
                parsed.query,
                keep_blank_values=True
            )

            for key in sorted(query):
                result[key] = query[key][0]

            return result

        except (
            ValueError,
            TypeError,
            AttributeError
        ):
            return None

    def build_unique_key(self, obj):
        if not obj:
            return ""

        proto = (
            obj.get("scheme")
            or "vmess"
        ).lower()

        if proto == "vmess":
            fields = [
                obj.get("add", ""),
                str(obj.get("port", "")),
                obj.get("id", ""),
                obj.get("net", ""),
                obj.get("host", ""),
                obj.get("path", ""),
                obj.get("tls", ""),
                obj.get("sni", "")
            ]

        elif proto == "vless":
            fields = [
                obj.get("server", ""),
                str(obj.get("port", "")),
                obj.get("user", ""),
                obj.get("security", ""),
                obj.get("type", ""),
                obj.get("host", ""),
                obj.get("path", ""),
                obj.get("sni", ""),
                obj.get("flow", "")
            ]

        elif proto == "trojan":
            fields = [
                obj.get("server", ""),
                str(obj.get("port", "")),
                obj.get("user", ""),
                obj.get("security", ""),
                obj.get("type", ""),
                obj.get("host", ""),
                obj.get("path", ""),
                obj.get("sni", "")
            ]

        elif proto == "ss":
            fields = [
                obj.get("server", ""),
                str(obj.get("port", "")),
                obj.get("user", ""),
                obj.get("method", "")
            ]

        elif proto in ("hysteria2", "hy2"):
            fields = [
                obj.get("server", ""),
                str(obj.get("port", "")),
                obj.get("user", ""),
                obj.get("obfs-password", ""),
                obj.get("sni", "")
            ]

        elif proto == "tuic":
            fields = [
                obj.get("server", ""),
                str(obj.get("port", "")),
                obj.get("user", ""),
                obj.get(
                    "congestion_control",
                    ""
                ),
                obj.get("sni", "")
            ]

        elif proto == "wireguard":
            fields = [
                obj.get("server", ""),
                str(obj.get("port", "")),
                obj.get("user", ""),
                obj.get("key", ""),
                obj.get("address", "")
            ]

        else:
            fields = sorted(
                obj.items()
            )

        return json.dumps(
            fields,
            sort_keys=True,
            ensure_ascii=False
        )

    def deduplicate(self, configs):
        unique = []
        seen = set()

        for config in configs:
            obj = self.normalize_config(
                config
            )

            if obj is None:
                continue

            key = self.build_unique_key(
                obj
            )

            digest = hashlib.sha256(
                key.encode("utf-8")
            ).hexdigest()

            if digest in seen:
                continue

            if self.config_hash_cache.get(
                digest
            ) is not None:
                continue

            seen.add(digest)

            self.config_hash_cache.set(
                digest,
                datetime.now(timezone.utc)
            )

            unique.append(config)

        return unique

    def get_config_hash(self, config):
        obj = self.normalize_config(
            config
        )

        if obj is None:
            return ""

        key = self.build_unique_key(
            obj
        )

        return hashlib.md5(
            key.encode("utf-8")
        ).hexdigest()

    def get_health_protocol(self, config):
        obj = self.normalize_config(
            config
        )

        if not obj:
            return None

        protocol = (
            obj.get("scheme")
            or "vmess"
        ).lower()

        if protocol == "vmess":
            return "vmess"

        if protocol == "vless":
            return "vless"

        if protocol == "trojan":
            return "trojan"

        if protocol == "ss":
            return "ss"

        if protocol in (
            "hysteria",
            "hysteria2",
            "hy2"
        ):
            return None

        if protocol == "tuic":
            return None

        if protocol == "wireguard":
            return None

        return None

    def get_config_endpoint(self, config):
        obj = self.normalize_config(
            config
        )

        if not obj:
            return "", 0

        protocol = (
            obj.get("scheme")
            or "vmess"
        ).lower()

        if protocol == "vmess":
            host = str(
                obj.get("add", "")
            ).strip()

            try:
                port = int(
                    obj.get("port", 0)
                )
            except (
                TypeError,
                ValueError
            ):
                port = 0

        else:
            host = str(
                obj.get("server", "")
            ).strip()

            try:
                port = int(
                    obj.get("port", 0)
                )
            except (
                TypeError,
                ValueError
            ):
                port = 0

        if not host:
            return "", 0

        if port < 1 or port > 65535:
            return "", 0

        return host, port

    async def tcp_health_check(
        self,
        host,
        port
    ):
        try:
            connect_task = asyncio.open_connection(
                host,
                port,
                family=socket.AF_INET
            )

            reader, writer = await asyncio.wait_for(
                connect_task,
                timeout=self.health_timeout
            )

            writer.close()

            try:
                await writer.wait_closed()
            except (
                asyncio.CancelledError,
                ConnectionError,
                OSError
            ):
                pass

            return True, ""

        except asyncio.TimeoutError:
            return False, "timeout"

        except socket.gaierror:
            return False, "dns_error"

        except ConnectionRefusedError:
            return False, "connection_refused"

        except ConnectionResetError:
            return False, "connection_reset"

        except OSError as exc:
            return False, (
                str(exc)
                or "os_error"
            )

        except Exception as exc:
            return False, (
                str(exc)
                or "unknown_error"
            )

    def load_health_state(self):
        if not os.path.exists(
            self.health_file
        ):
            return {}

        try:
            with open(
                self.health_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if not isinstance(data, dict):
                return {}

            return data

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            ValueError
        ):
            return {}

    def save_health_state(self, state):
        try:
            os.makedirs(
                self.health_dir,
                exist_ok=True
            )

            temp_file = (
                self.health_file
                + ".tmp"
            )

            with open(
                temp_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    state,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            os.replace(
                temp_file,
                self.health_file
            )

        except OSError:
            try:
                if os.path.exists(
                    temp_file
                ):
                    os.remove(
                        temp_file
                    )
            except OSError:
                pass

    async def check_config_health(
        self,
        config,
        semaphore
    ):
        config_hash = self.get_config_hash(
            config
        )

        if not config_hash:
            return (
                "",
                None,
                "unchecked",
                "invalid_config"
            )

        protocol = self.get_health_protocol(
            config
        )

        if protocol is None:
            return (
                config_hash,
                None,
                "unchecked",
                "protocol_not_tcp_checked"
            )

        host, port = self.get_config_endpoint(
            config
        )

        if not host or not port:
            return (
                config_hash,
                False,
                protocol,
                "invalid_endpoint"
            )

        async with semaphore:
            success, error = (
                await self.tcp_health_check(
                    host,
                    port
                )
            )

        return (
            config_hash,
            success,
            protocol,
            error
        )

    async def health_check_configs_async(
        self,
        configs
    ):
        state = self.load_health_state()

        if not isinstance(state, dict):
            state = {}

        now = datetime.now(timezone.utc)

        semaphore = asyncio.Semaphore(
            self.health_concurrency
        )

        tasks = [
            self.check_config_health(
                config,
                semaphore
            )
            for config in configs
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True
        )

        healthy_configs = []
        unstable_configs = []
        dead_configs = []
        unchecked_configs = []

        checked = 0
        healthy = 0
        unstable = 0
        dead = 0
        unchecked = 0

        current_hashes = set()

        for config, result in zip(
            configs,
            results
        ):
            if isinstance(
                result,
                Exception
            ):
                config_hash = self.get_config_hash(
                    config
                )

                result = (
                    config_hash,
                    False,
                    self.get_health_protocol(
                        config
                    ),
                    str(result)
                )

            (
                config_hash,
                success,
                protocol,
                error
            ) = result

            if not config_hash:
                unchecked_configs.append(
                    config
                )
                unchecked += 1
                continue

            current_hashes.add(
                config_hash
            )

            entry = state.get(
                config_hash,
                {}
            )

            if not isinstance(
                entry,
                dict
            ):
                entry = {}

            previous_failures = int(
                entry.get(
                    "consecutive_failures",
                    0
                )
                or 0
            )

            total_successes = int(
                entry.get(
                    "total_successes",
                    0
                )
                or 0
            )

            total_failures = int(
                entry.get(
                    "total_failures",
                    0
                )
                or 0
            )

            entry["protocol"] = (
                protocol
                or "unchecked"
            )

            entry["last_check"] = (
                now.isoformat()
            )

            if success is None:
                entry["status"] = "unchecked"
                entry["consecutive_failures"] = (
                    previous_failures
                )
                entry["last_error"] = (
                    error
                    or "unchecked"
                )

                unchecked_configs.append(
                    config
                )
                unchecked += 1

            elif success:
                entry["status"] = "healthy"
                entry["consecutive_failures"] = 0
                entry["total_successes"] = (
                    total_successes + 1
                )
                entry["total_failures"] = (
                    total_failures
                )
                entry["last_success"] = (
                    now.isoformat()
                )
                entry["last_error"] = ""

                healthy_configs.append(
                    config
                )

                checked += 1
                healthy += 1

            else:
                consecutive_failures = (
                    previous_failures + 1
                )

                entry["consecutive_failures"] = (
                    consecutive_failures
                )
                entry["total_successes"] = (
                    total_successes
                )
                entry["total_failures"] = (
                    total_failures + 1
                )
                entry["last_error"] = (
                    error
                    or "health_check_failed"
                )

                checked += 1

                if (
                    consecutive_failures
                    >= self.health_max_failures
                ):
                    entry["status"] = "dead"

                    dead_configs.append(
                        config
                    )

                    dead += 1

                else:
                    entry["status"] = "unstable"

                    unstable_configs.append(
                        config
                    )

                    unstable += 1

            state[config_hash] = entry

        cutoff = (
            now.timestamp()
            - self.health_state_retention
        )

        for config_hash in list(
            state.keys()
        ):
            if config_hash in current_hashes:
                continue

            entry = state.get(
                config_hash
            )

            if not isinstance(
                entry,
                dict
            ):
                del state[config_hash]
                continue

            last_check = entry.get(
                "last_check"
            )

            if not last_check:
                del state[config_hash]
                continue

            try:
                last_timestamp = (
                    datetime.fromisoformat(
                        last_check
                    ).timestamp()
                )

                if last_timestamp < cutoff:
                    del state[config_hash]

            except (
                TypeError,
                ValueError,
                OSError
            ):
                del state[config_hash]

        self.save_health_state(
            state
        )

        self.health_stats = {
            "checked": checked,
            "healthy": healthy,
            "unstable": unstable,
            "dead": dead,
            "unchecked": unchecked
        }

        output_configs = (
            healthy_configs
            + unstable_configs
            + unchecked_configs
        )

        return (
            output_configs,
            healthy_configs,
            unstable_configs,
            dead_configs,
            unchecked_configs,
            self.health_stats,
            state
        )

    def health_check_configs(
        self,
        configs
    ):
        if not configs:
            self.health_stats = {
                "checked": 0,
                "healthy": 0,
                "unstable": 0,
                "dead": 0,
                "unchecked": 0
            }

            return (
                [],
                [],
                [],
                [],
                [],
                self.health_stats,
                self.load_health_state()
            )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(
                self.health_check_configs_async(
                    configs
                )
            )

        finally:
            try:
                loop.run_until_complete(
                    asyncio.sleep(0)
                )
            except RuntimeError:
                pass

            loop.close()

    def categorize(self, configs):
        categories = {
            "vmess": [],
            "vless": [],
            "trojan": [],
            "ss": [],
            "hysteria2": [],
            "hysteria": [],
            "tuic": [],
            "wireguard": [],
            "other": []
        }

        for config in configs:
            if not isinstance(config, str):
                continue

            if config.startswith("vmess://"):
                categories["vmess"].append(config)

            elif config.startswith("vless://"):
                categories["vless"].append(config)

            elif config.startswith("trojan://"):
                categories["trojan"].append(config)

            elif config.startswith("ss://"):
                categories["ss"].append(config)

            elif (
                config.startswith("hysteria2://")
                or config.startswith("hy2://")
            ):
                categories["hysteria2"].append(
                    config
                )

            elif config.startswith(
                "hysteria://"
            ):
                categories["hysteria"].append(
                    config
                )

            elif config.startswith("tuic://"):
                categories["tuic"].append(config)

            elif config.startswith(
                "wireguard://"
            ):
                categories["wireguard"].append(
                    config
                )

            else:
                categories["other"].append(
                    config
                )

        return categories

    async def fetch_channel_async(
        self,
        session,
        url,
        semaphore
    ):
        async with semaphore:
            if self.should_skip_channel(url):
                return None, None, url

            try:
                telegram_url = re.sub(
                    r"^https?://t\.me",
                    "https://telegram.me",
                    url,
                    flags=re.IGNORECASE
                )

                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "(Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36"
                    ),
                    "Accept": (
                        "text/html,application/xhtml+xml,"
                        "application/xml;q=0.9,"
                        "image/webp,*/*;q=0.8"
                    ),
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": (
                        "gzip, deflate, br"
                    ),
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }

                timeout = aiohttp.ClientTimeout(
                    total=20
                )

                async with session.get(
                    telegram_url,
                    headers=headers,
                    timeout=timeout
                ) as response:
                    if response.status != 200:
                        self.update_dead_cache(url)
                        return None, None, url

                    html = await response.text()

                    return html, url, None

            except (
                aiohttp.ClientError,
                asyncio.TimeoutError
            ):
                self.update_dead_cache(url)
                return None, None, url

    async def process_channel_async(
        self,
        session,
        url,
        semaphore,
        limit_per_channel=15
    ):
        html, channel_url, error = (
            await self.fetch_channel_async(
                session,
                url,
                semaphore
            )
        )

        if html is None or error is not None:
            return [], 0

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        last_post_time = self.get_last_post_time(
            soup
        )

        if not last_post_time:
            self.update_dead_cache(url)
            return [], 0

        last_seen = self.last_post_cache.get(
            url
        )

        if (
            last_seen
            and last_post_time == last_seen
        ):
            time_since_last = (
                datetime.now(timezone.utc)
                - last_post_time
            )

            if time_since_last >= timedelta(
                hours=24
            ):
                if (
                    url
                    not in self.temp_suspended_cache
                ):
                    self.temp_suspended_cache[url] = (
                        datetime.now(timezone.utc)
                    )

                    self.save_temp_suspend()

                    print(
                        "  → Channel suspended "
                        f"(no new posts for "
                        f"{int(time_since_last.total_seconds() / 3600)}h)"
                    )

                return [], 0

        self.last_post_cache[url] = (
            last_post_time
        )

        if (
            datetime.now(timezone.utc)
            - last_post_time
            > timedelta(days=2)
        ):
            if (
                url
                not in self.temp_suspended_cache
            ):
                self.temp_suspended_cache[url] = (
                    datetime.now(timezone.utc)
                )

                self.save_temp_suspend()

                print(
                    "  → Channel suspended "
                    "(last post >2 days)"
                )

            return [], 0

        if url in self.temp_suspended_cache:
            del self.temp_suspended_cache[url]
            self.save_temp_suspend()

            print(
                "  → Channel reactivated "
                "(new post detected)"
            )

        raw_configs = self.extract_from_soup(
            soup
        )

        valid_configs = []

        for config in raw_configs:
            config = self.clean_config(
                config
            )

            if not self.validate_config(
                config
            ):
                continue

            tagged_config = self.tag_config(
                config,
                "ARISTA"
            )

            if self.validate_config(
                tagged_config
            ):
                valid_configs.append(
                    tagged_config
                )

        if valid_configs:
            self.failed_counter[url] = 0

        await asyncio.sleep(
            random.uniform(0.1, 0.3)
        )

        valid_configs = valid_configs[
            :limit_per_channel
        ]

        return (
            valid_configs,
            len(valid_configs)
        )

    def process_channels(
        self,
        limit_per_channel=15
    ):
        configs_per_channel = {}
        failed_channels = []
        skipped_channels = []
        dead_cached_skipped = 0

        if not self.channels:
            print(
                "No channels found in "
                "Entry/channels.json"
            )

            return {}, 0, 0, 0, 0

        print(
            f"Processing "
            f"{len(self.channels)} Telegram channels..."
        )

        self.channels = list(
            dict.fromkeys(
                self.channels
            )
        )

        semaphore = asyncio.Semaphore(
            50
        )

        async def process_all():
            nonlocal configs_per_channel
            nonlocal failed_channels
            nonlocal skipped_channels
            nonlocal dead_cached_skipped

            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=50,
                enable_cleanup_closed=True
            )

            async with aiohttp.ClientSession(
                connector=connector
            ) as session:
                tasks = []
                task_urls = []

                for url in self.channels:
                    if self.should_skip_channel(
                        url
                    ):
                        dead_cached_skipped += 1
                        continue

                    tasks.append(
                        self.process_channel_async(
                            session,
                            url,
                            semaphore,
                            limit_per_channel
                        )
                    )

                    task_urls.append(url)

                if not tasks:
                    return configs_per_channel

                results = await asyncio.gather(
                    *tasks,
                    return_exceptions=True
                )

                for url, result in zip(
                    task_urls,
                    results
                ):
                    if isinstance(
                        result,
                        Exception
                    ):
                        self.update_dead_cache(
                            url
                        )
                        failed_channels.append(
                            url
                        )
                        continue

                    valid_configs, config_count = (
                        result
                    )

                    if config_count > 0:
                        configs_per_channel[url] = (
                            valid_configs
                        )

                    elif url not in self.dead_cache:
                        skipped_channels.append(
                            url
                        )

                return configs_per_channel

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            configs_per_channel = (
                loop.run_until_complete(
                    process_all()
                )
            )

        finally:
            try:
                loop.run_until_complete(
                    asyncio.sleep(0)
                )
            except RuntimeError:
                pass

            loop.close()

        self.save_last_seen()
        self.save_dead_cache()
        self.save_temp_suspend()
        self.save_permanent_blacklist()

        latest_configs = []

        for configs in configs_per_channel.values():
            latest_configs.extend(
                configs[:limit_per_channel]
            )

        unique_configs = self.deduplicate(
            latest_configs
        )

        print(
            f"\n🔍 Health checking "
            f"{len(unique_configs)} Telegram configs..."
        )

        (
            output_configs,
            healthy_configs,
            unstable_configs,
            dead_configs,
            unchecked_configs,
            health_stats,
            health_state
        ) = self.health_check_configs(
            unique_configs
        )

        print(
            f"  → Checked: "
            f"{health_stats['checked']}"
        )

        print(
            f"  → Healthy: "
            f"{health_stats['healthy']}"
        )

        print(
            f"  → Unstable: "
            f"{health_stats['unstable']}"
        )

        print(
            f"  → Dead: "
            f"{health_stats['dead']}"
        )

        print(
            f"  → Unchecked: "
            f"{health_stats['unchecked']}"
        )

        categories = self.categorize(
            output_configs
        )

        return (
            categories,
            len(output_configs),
            len(failed_channels),
            len(skipped_channels),
            dead_cached_skipped
        )

    def save_results(
        self,
        categories,
        total_count
    ):
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        output_dir = (
            "configs.txt/telegram"
        )

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        for category, configs in (
            categories.items()
        ):
            if not configs:
                continue

            filename = os.path.join(
                output_dir,
                f"{category}.txt"
            )

            content = (
                f"# Telegram "
                f"{category.upper()} Configurations\n"
            )

            content += (
                f"# Updated: {timestamp}\n"
            )

            content += (
                f"# Count: {len(configs)}\n"
            )

            content += (
                "# Source: Telegram Channels\n"
            )

            content += (
                "# T.ME: @aristapanel\n"
            )

            content += "\n"

            content += "\n".join(
                configs
            )

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(content)

        all_configs = []

        for configs in categories.values():
            all_configs.extend(configs)

        if all_configs:
            filename = os.path.join(
                output_dir,
                "all.txt"
            )

            content = (
                "# All Telegram Configurations\n"
            )

            content += (
                f"# Updated: {timestamp}\n"
            )

            content += (
                f"# Total Count: "
                f"{len(all_configs)}\n"
            )

            content += (
                "# Source: Telegram Channels\n"
            )

            content += (
                "# T.ME: @aristapanel\n"
            )

            content += "\n"

            content += "\n".join(
                all_configs
            )

            with open(
                filename,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(content)

        stats = {
            "source": "telegram",
            "added": len(all_configs),
            "protocols": {
                "vless": len(
                    categories["vless"]
                ),
                "vmess": len(
                    categories["vmess"]
                ),
                "trojan": len(
                    categories["trojan"]
                ),
                "shadowsocks": len(
                    categories["ss"]
                ),
                "hysteria2": len(
                    categories["hysteria2"]
                ),
                "hysteria": len(
                    categories["hysteria"]
                ),
                "tuic": len(
                    categories["tuic"]
                ),
                "wireguard": len(
                    categories["wireguard"]
                ),
                "other": len(
                    categories["other"]
                )
            },
            "health": {
                "checked": self.health_stats.get(
                    "checked",
                    0
                ),
                "healthy": self.health_stats.get(
                    "healthy",
                    0
                ),
                "unstable": self.health_stats.get(
                    "unstable",
                    0
                ),
                "dead": self.health_stats.get(
                    "dead",
                    0
                ),
                "unchecked": self.health_stats.get(
                    "unchecked",
                    0
                )
            }
        }

        with open(
            "stats.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                stats,
                file,
                ensure_ascii=False,
                indent=2
            )

        return len(all_configs)


def main():
    print("=" * 60)
    print(
        "ARISTA TELEGRAM CONFIG EXTRACTOR v2.0"
    )
    print("=" * 60)

    try:
        extractor = TelegramConfigExtractor()

        (
            categories,
            total_count,
            failed_channels,
            skipped_channels,
            dead_cached_skipped
        ) = extractor.process_channels(
            limit_per_channel=15
        )

        saved_count = extractor.save_results(
            categories,
            total_count
        )

        print(
            "\n✅ PROCESSING COMPLETE"
        )

        print(
            f"Total unique configs: "
            f"{total_count}"
        )

        print(
            f"Configs saved: "
            f"{saved_count}"
        )

        print(
            f"Failed channels: "
            f"{failed_channels}"
        )

        print(
            f"Skipped inactive channels: "
            f"{skipped_channels}"
        )

        print(
            f"Skipped dead-cached channels: "
            f"{dead_cached_skipped}"
        )

        print(
            f"Health checked: "
            f"{extractor.health_stats['checked']}"
        )

        print(
            f"Health healthy: "
            f"{extractor.health_stats['healthy']}"
        )

        print(
            f"Health unstable: "
            f"{extractor.health_stats['unstable']}"
        )

        print(
            f"Health dead: "
            f"{extractor.health_stats['dead']}"
        )

        print(
            f"Health unchecked: "
            f"{extractor.health_stats['unchecked']}"
        )

    except Exception as exc:
        print(
            f"\n❌ ERROR: {exc}"
        )


if __name__ == "__main__":
    main()
