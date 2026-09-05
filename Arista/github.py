import requests
import re
import json
import hashlib
import base64
import uuid
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, unquote
import os
import asyncio
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


class GitHubConfigExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.sources = self.load_sources()

        self.health_file = "health/github_health.json"
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

        if os.path.exists("stats.json"):
            os.remove("stats.json")

    def load_sources(self):
        repo_json = os.environ.get('REPO_JSON')

        if repo_json:
            try:
                data = json.loads(repo_json)

                if isinstance(data, list):
                    return data

                if isinstance(data, dict) and 'sources' in data:
                    return data['sources']

            except Exception:
                pass

        try:
            sources_file = "Entry/repo.json"

            if os.path.exists(sources_file):
                with open(sources_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    if isinstance(data, list):
                        return data

                    if isinstance(data, dict) and 'sources' in data:
                        return data['sources']

            return []

        except Exception:
            return []

    def fetch_content(self, url):
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception:
            return ""

    def extract_configs(self, content):
        patterns = [
            r'(vmess://[A-Za-z0-9+/=_-]+)',
            r'(vless://[^\s<>"\'`]+)',
            r'(trojan://[^\s<>"\'`]+)',
            r'(ss://[^\s<>"\'`]+)',
            r'(hysteria2://[^\s<>"\'`]+)',
            r'(hysteria://[^\s<>"\'`]+)',
            r'(hy2://[^\s<>"\'`]+)',
            r'(tuic://[^\s<>"\'`]+)'
        ]

        configs = []

        for pattern in patterns:
            configs.extend(re.findall(pattern, content, re.IGNORECASE))

        cleaned = []

        for config in configs:
            config = config.strip().rstrip('.,;')

            if not config:
                continue

            if config.lower().startswith('ss://{'):
                continue

            cleaned.append(config)

        return cleaned

    def standardize_ss(self, config_str):
        try:
            if not config_str.lower().startswith('ss://'):
                return config_str

            config_str = config_str.strip()

            parts = config_str.split('#', 1)
            base_part = parts[0][5:]

            if not base_part:
                return config_str

            if '@' in base_part:
                encoded_method_pass, server_part = base_part.split('@', 1)

                try:
                    padding = '=' * (-len(encoded_method_pass) % 4)
                    decoded_mp = base64.urlsafe_b64decode(
                        encoded_method_pass + padding
                    ).decode('utf-8')

                    if ':' in decoded_mp:
                        encoded_mp = base64.urlsafe_b64encode(
                            decoded_mp.encode()
                        ).decode().rstrip('=')

                        result = f"ss://{encoded_mp}@{server_part}"

                        if len(parts) == 2:
                            result += f"#{unquote(parts[1])}"

                        return result

                except Exception:
                    pass

                if len(parts) == 2:
                    return f"{parts[0]}#{unquote(parts[1])}"

                return parts[0]

            try:
                padding = '=' * (-len(base_part) % 4)

                decoded = base64.urlsafe_b64decode(
                    base_part + padding
                ).decode('utf-8')

                if '@' in decoded:
                    method_pass, server = decoded.split('@', 1)

                    encoded_mp = base64.urlsafe_b64encode(
                        method_pass.encode()
                    ).decode().rstrip('=')

                    result = f"ss://{encoded_mp}@{server}"

                    if len(parts) == 2:
                        result += f"#{unquote(parts[1])}"

                    return result

            except Exception:
                pass

            return config_str

        except Exception:
            return config_str

    def decode_vmess(self, config_str):
        try:
            if not config_str.startswith('vmess://'):
                return None

            base64_part = config_str[8:].strip()

            padding = '=' * (-len(base64_part) % 4)

            decoded = base64.urlsafe_b64decode(
                base64_part + padding
            ).decode('utf-8')

            return json.loads(decoded)

        except Exception:
            try:
                base64_part = config_str[8:].strip()
                padding = '=' * (-len(base64_part) % 4)

                decoded = base64.b64decode(
                    base64_part + padding
                ).decode('utf-8')

                return json.loads(decoded)

            except Exception:
                return None

    def validate_vmess_dict(self, config_dict):
        if not isinstance(config_dict, dict):
            return False

        required_keys = ['v', 'ps', 'add', 'port', 'id', 'aid']

        if not all(k in config_dict for k in required_keys):
            return False

        try:
            address = str(config_dict.get('add', '')).strip()

            if not address:
                return False

            port = int(config_dict.get('port'))

            if port < 1 or port > 65535:
                return False

            uuid.UUID(str(config_dict.get('id')))

            int(config_dict.get('aid'))

        except Exception:
            return False

        return True

    def validate_url_config(self, config_str, scheme):
        try:
            if not config_str.lower().startswith(f'{scheme}://'):
                return False

            parsed = urlparse(config_str)

            if parsed.scheme.lower() != scheme:
                return False

            if not parsed.hostname:
                return False

            if not parsed.port or parsed.port < 1 or parsed.port > 65535:
                return False

            if not parsed.username:
                return False

            return True

        except Exception:
            return False

    def validate_ss(self, config_str):
        try:
            config_str = self.standardize_ss(config_str)

            if not config_str.startswith('ss://'):
                return False

            parts = config_str.split('#', 1)
            base_part = parts[0][5:]

            if not base_part:
                return False

            if '@' not in base_part:
                try:
                    padding = '=' * (-len(base_part) % 4)

                    decoded = base64.urlsafe_b64decode(
                        base_part + padding
                    ).decode('utf-8')

                    if '@' not in decoded:
                        return False

                    method_pass, server_part = decoded.split('@', 1)

                    if ':' not in method_pass:
                        return False

                    if ':' not in server_part:
                        return False

                    host, port_str = server_part.rsplit(':', 1)

                    if not host:
                        return False

                    port = int(port_str)

                    return 1 <= port <= 65535

                except Exception:
                    return False

            encoded_method_pass, server_part = base_part.split('@', 1)

            if not encoded_method_pass:
                return False

            padding = '=' * (-len(encoded_method_pass) % 4)

            try:
                decoded_mp = base64.urlsafe_b64decode(
                    encoded_method_pass + padding
                ).decode('utf-8')

                if ':' not in decoded_mp:
                    return False

            except Exception:
                return False

            if server_part.startswith('['):
                match = re.match(
                    r'^\[([^\]]+)\]:(\d+)$',
                    server_part
                )

                if not match:
                    return False

                port = int(match.group(2))

            else:
                if ':' not in server_part:
                    return False

                server, port_str = server_part.rsplit(':', 1)

                if not server:
                    return False

                port = int(port_str)

            return 1 <= port <= 65535

        except Exception:
            return False

    def validate_config(self, config):
        if isinstance(config, dict):
            return self.validate_vmess_dict(config)

        if not isinstance(config, str):
            return False

        config_str = config.strip()

        if config_str.startswith('vmess://'):
            decoded = self.decode_vmess(config_str)

            return (
                decoded is not None
                and isinstance(decoded, dict)
                and self.validate_vmess_dict(decoded)
            )

        if config_str.startswith('vless://'):
            return self.validate_url_config(
                config_str,
                'vless'
            )

        if config_str.startswith('trojan://'):
            return self.validate_url_config(
                config_str,
                'trojan'
            )

        if config_str.startswith('ss://'):
            return self.validate_ss(config_str)

        if config_str.startswith('hysteria2://'):
            return self.validate_url_config(
                config_str,
                'hysteria2'
            )

        if config_str.startswith('hy2://'):
            return self.validate_url_config(
                config_str,
                'hy2'
            )

        if config_str.startswith('hysteria://'):
            return self.validate_url_config(
                config_str,
                'hysteria'
            )

        if config_str.startswith('tuic://'):
            return self.validate_url_config(
                config_str,
                'tuic'
            )

        return False

    def tag_config(self, config, tag="T.ME: @aristapanel"):
        if isinstance(config, dict):
            config = dict(config)
            config['ps'] = tag

            json_str = json.dumps(
                config,
                separators=(',', ':'),
                ensure_ascii=False
            )

            encoded = base64.urlsafe_b64encode(
                json_str.encode()
            ).decode().rstrip('=')

            return 'vmess://' + encoded

        config_str = config.strip()

        if config_str.startswith('vmess://'):
            decoded = self.decode_vmess(config_str)

            if decoded and isinstance(decoded, dict):
                decoded = dict(decoded)
                decoded['ps'] = tag

                json_str = json.dumps(
                    decoded,
                    separators=(',', ':'),
                    ensure_ascii=False
                )

                encoded = base64.urlsafe_b64encode(
                    json_str.encode()
                ).decode().rstrip('=')

                return 'vmess://' + encoded

            return config_str

        base = config_str.split('#', 1)[0]

        return f"{base}#{tag}"

    def normalize_config(self, config):
        if isinstance(config, dict):
            normalized = dict(config)

            normalized.pop("ps", None)

            return normalized

        if not isinstance(config, str):
            return None

        config = config.strip()

        if config.startswith("vmess://"):
            vm = self.decode_vmess(config)

            if vm:
                vm = dict(vm)
                vm.pop("ps", None)
                return vm

            return None

        try:
            clean_config = config.split('#', 1)[0]

            p = urlparse(clean_config)

            result = {
                "scheme": p.scheme.lower(),
                "server": p.hostname or "",
                "port": p.port or 0,
                "user": unquote(p.username or ""),
                "path": unquote(p.path or "")
            }

            query = parse_qs(
                p.query,
                keep_blank_values=True
            )

            for k in sorted(query):
                result[k] = query[k][0]

            return result

        except Exception:
            return None

    def build_unique_key(self, obj):
        if not obj:
            return ""

        proto = str(
            obj.get("scheme") or "vmess"
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

        elif proto == "hysteria":
            fields = [
                obj.get("server", ""),
                str(obj.get("port", "")),
                obj.get("user", ""),
                obj.get("auth", ""),
                obj.get("obfs", ""),
                obj.get("sni", "")
            ]

        elif proto == "tuic":
            fields = [
                obj.get("server", ""),
                str(obj.get("port", "")),
                obj.get("user", ""),
                obj.get("congestion_control", ""),
                obj.get("sni", "")
            ]

        else:
            fields = sorted(obj.items())

        return json.dumps(
            fields,
            sort_keys=True,
            ensure_ascii=False
        )

    def get_config_hash(self, config):
        obj = self.normalize_config(config)

        if obj is None:
            return hashlib.md5(
                str(config).encode('utf-8')
            ).hexdigest()

        key = self.build_unique_key(obj)

        return hashlib.md5(
            key.encode('utf-8')
        ).hexdigest()

    def deduplicate(self, configs):
        unique = []
        seen = set()

        for config in configs:
            obj = self.normalize_config(config)

            if obj is None:
                continue

            key = self.build_unique_key(obj)

            md5 = hashlib.md5(
                key.encode('utf-8')
            ).hexdigest()

            if md5 not in seen:
                seen.add(md5)
                unique.append(config)

        return unique

    def categorize(self, configs):
        categories = {
            'vmess': [],
            'vless': [],
            'trojan': [],
            'ss': [],
            'hysteria2': [],
            'hysteria': [],
            'tuic': [],
            'other': []
        }

        for config in configs:
            if not isinstance(config, str):
                continue

            config_lower = config.lower()

            if config_lower.startswith('vmess://'):
                categories['vmess'].append(config)

            elif config_lower.startswith('vless://'):
                categories['vless'].append(config)

            elif config_lower.startswith('trojan://'):
                categories['trojan'].append(config)

            elif config_lower.startswith('ss://'):
                categories['ss'].append(config)

            elif (
                config_lower.startswith('hysteria2://')
                or config_lower.startswith('hy2://')
            ):
                categories['hysteria2'].append(config)

            elif config_lower.startswith('hysteria://'):
                categories['hysteria'].append(config)

            elif config_lower.startswith('tuic://'):
                categories['tuic'].append(config)

            else:
                categories['other'].append(config)

        return categories

    def get_health_protocol(self, config):
        obj = self.normalize_config(config)

        if not obj:
            return None

        proto = str(
            obj.get("scheme") or "vmess"
        ).lower()

        if proto in (
            "vmess",
            "vless",
            "trojan",
            "ss"
        ):
            return proto

        return None

    def get_config_endpoint(self, config):
        obj = self.normalize_config(config)

        if not obj:
            return None, None, None

        proto = str(
            obj.get("scheme") or "vmess"
        ).lower()

        if proto == "vmess":
            host = str(
                obj.get("add", "")
            ).strip()

            port = obj.get("port", 0)

        else:
            host = str(
                obj.get("server", "")
            ).strip()

            port = obj.get("port", 0)

        if not host:
            return None, None, None

        try:
            port = int(port)
        except Exception:
            return None, None, None

        if port < 1 or port > 65535:
            return None, None, None

        return host, port, proto

    async def tcp_health_check(self, host, port):
        writer = None

        try:
            connect_task = asyncio.open_connection(
                host,
                port,
                family=socket.AF_INET
            )

            _, writer = await asyncio.wait_for(
                connect_task,
                timeout=self.health_timeout
            )

            if writer:
                writer.close()

                try:
                    await writer.wait_closed()
                except Exception:
                    pass

            return True, ""

        except asyncio.TimeoutError:
            if writer:
                try:
                    writer.close()
                except Exception:
                    pass

            return False, "timeout"

        except ConnectionRefusedError:
            if writer:
                try:
                    writer.close()
                except Exception:
                    pass

            return False, "connection_refused"

        except socket.gaierror:
            if writer:
                try:
                    writer.close()
                except Exception:
                    pass

            return False, "dns_error"

        except ConnectionResetError:
            if writer:
                try:
                    writer.close()
                except Exception:
                    pass

            return False, "connection_reset"

        except OSError as e:
            if writer:
                try:
                    writer.close()
                except Exception:
                    pass

            error_code = getattr(e, "errno", None)

            if error_code is not None:
                return False, f"os_error_{error_code}"

            return False, "os_error"

        except Exception:
            if writer:
                try:
                    writer.close()
                except Exception:
                    pass

            return False, "unknown_error"

    def load_health_state(self):
        if not os.path.exists(self.health_file):
            return {}

        try:
            with open(
                self.health_file,
                'r',
                encoding='utf-8'
            ) as f:
                data = json.load(f)

            if isinstance(data, dict):
                return data

        except Exception:
            pass

        return {}

    def save_health_state(self, state):
        directory = os.path.dirname(
            self.health_file
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        temp_file = f"{self.health_file}.tmp"

        with open(
            temp_file,
            'w',
            encoding='utf-8'
        ) as f:
            json.dump(
                state,
                f,
                ensure_ascii=False,
                indent=2
            )

        os.replace(
            temp_file,
            self.health_file
        )

    async def check_config_health(
        self,
        config,
        semaphore
    ):
        config_hash = self.get_config_hash(config)
        protocol = self.get_health_protocol(config)

        if protocol is None:
            return (
                config_hash,
                None,
                "unchecked",
                ""
            )

        host, port, _ = self.get_config_endpoint(
            config
        )

        if not host or not port:
            return (
                config_hash,
                False,
                "invalid_endpoint",
                "invalid_endpoint"
            )

        async with semaphore:
            success, error = await self.tcp_health_check(
                host,
                port
            )

        return (
            config_hash,
            success,
            protocol,
            error
        )

    async def health_check_configs_async(self, configs):
        state = self.load_health_state()

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

        results = []

        if tasks:
            results = await asyncio.gather(
                *tasks,
                return_exceptions=True
            )

        now = int(
            datetime.now(timezone.utc).timestamp()
        )

        healthy = []
        unstable = []
        dead = []
        unchecked = 0

        for config, result in zip(
            configs,
            results
        ):
            config_hash = self.get_config_hash(
                config
            )

            if isinstance(result, Exception):
                success = False
                protocol = "error"
                error = "health_check_exception"
            else:
                (
                    result_hash,
                    success,
                    protocol,
                    error
                ) = result

                config_hash = result_hash

            entry = state.get(
                config_hash,
                {}
            )

            if not isinstance(entry, dict):
                entry = {}

            entry["last_check"] = now

            if protocol == "unchecked":
                unchecked += 1

                entry["status"] = "unchecked"
                entry["protocol"] = (
                    self.normalize_config(config) or {}
                ).get(
                    "scheme",
                    "unknown"
                )
                entry["failures"] = 0
                entry["last_error"] = ""

                state[config_hash] = entry

                healthy.append(config)
                continue

            if success:
                entry["failures"] = 0
                entry["successes"] = int(
                    entry.get("successes", 0)
                ) + 1
                entry["status"] = "healthy"
                entry["last_success"] = now
                entry["protocol"] = protocol
                entry["last_error"] = ""

                healthy.append(config)

            else:
                failures = int(
                    entry.get("failures", 0)
                ) + 1

                entry["failures"] = failures
                entry["failures_total"] = int(
                    entry.get("failures_total", 0)
                ) + 1
                entry["protocol"] = protocol
                entry["last_error"] = error

                if failures >= self.health_max_failures:
                    entry["status"] = "dead"
                    dead.append(config)
                else:
                    entry["status"] = "unstable"
                    unstable.append(config)

            state[config_hash] = entry

        current_hashes = {
            self.get_config_hash(config)
            for config in configs
        }

        stale_limit = (
            now - self.health_state_retention
        )

        cleaned_state = {}

        for config_hash, entry in state.items():
            if not isinstance(entry, dict):
                continue

            last_check = int(
                entry.get("last_check", 0) or 0
            )

            if (
                config_hash in current_hashes
                or last_check >= stale_limit
            ):
                cleaned_state[config_hash] = entry

        self.save_health_state(
            cleaned_state
        )

        return {
            "healthy": healthy,
            "unstable": unstable,
            "dead": dead,
            "unchecked": unchecked,
            "checked": len(configs),
            "health_state": cleaned_state
        }

    def health_check_configs(self, configs):
        try:
            return asyncio.run(
                self.health_check_configs_async(
                    configs
                )
            )

        except RuntimeError:
            loop = asyncio.new_event_loop()

            try:
                return loop.run_until_complete(
                    self.health_check_configs_async(
                        configs
                    )
                )
            finally:
                loop.close()

    def process_sources(self):
        all_configs = []
        failed_sources = []

        if not self.sources:
            print(
                "No sources found in Entry/repo.json"
            )

            return {}, 0, 0, 0

        print(
            f"Processing {len(self.sources)} GitHub sources..."
        )

        for i, url in enumerate(
            self.sources,
            1
        ):
            print(
                f"[{i}/{len(self.sources)}] {url}"
            )

            content = self.fetch_content(url)

            if content:
                configs = self.extract_configs(
                    content
                )

                all_configs.extend(
                    configs
                )

            else:
                failed_sources.append(url)

        processed_configs = []
        failed_configs = 0

        for config in all_configs:
            try:
                if config.lower().startswith(
                    'ss://'
                ):
                    standard_ss = self.standardize_ss(
                        config
                    )

                    if self.validate_config(
                        standard_ss
                    ):
                        processed_configs.append(
                            self.tag_config(
                                standard_ss
                            )
                        )
                    else:
                        failed_configs += 1

                elif config.lower().startswith(
                    'vmess://'
                ):
                    decoded = self.decode_vmess(
                        config
                    )

                    if (
                        decoded
                        and isinstance(decoded, dict)
                        and self.validate_config(decoded)
                    ):
                        processed_configs.append(
                            self.tag_config(
                                decoded
                            )
                        )
                    else:
                        failed_configs += 1

                else:
                    if self.validate_config(
                        config
                    ):
                        processed_configs.append(
                            self.tag_config(
                                config
                            )
                        )
                    else:
                        failed_configs += 1

            except Exception:
                failed_configs += 1

        unique_configs = self.deduplicate(
            processed_configs
        )

        print(
            f"Unique configs before health check: {len(unique_configs)}"
        )

        health = self.health_check_configs(
            unique_configs
        )

        healthy_configs = health["healthy"]
        unstable_configs = health["unstable"]
        dead_configs = health["dead"]
        unchecked_configs = health["unchecked"]

        print(
            f"Health checked: {health['checked']}"
        )

        print(
            f"Healthy configs: {len(healthy_configs)}"
        )

        print(
            f"Unstable configs: {len(unstable_configs)}"
        )

        print(
            f"Dead configs removed: {len(dead_configs)}"
        )

        if unchecked_configs > 0:
            print(
                f"Configs without TCP health check: {unchecked_configs}"
            )

        categories = self.categorize(
            healthy_configs
        )

        self.health_stats = {
            "checked": health["checked"],
            "healthy": len(healthy_configs),
            "unstable": len(unstable_configs),
            "dead": len(dead_configs),
            "unchecked": unchecked_configs,
            "max_failures": self.health_max_failures,
            "timeout": self.health_timeout,
            "concurrency": self.health_concurrency
        }

        return (
            categories,
            len(healthy_configs),
            len(failed_sources),
            failed_configs
        )

    def save_results(
        self,
        categories,
        total_count
    ):
        timestamp = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'
        )

        os.makedirs(
            'configs.txt/github',
            exist_ok=True
        )

        for category, configs in categories.items():
            if configs:
                filename = (
                    f"configs.txt/github/{category}.txt"
                )

                content = (
                    f"# GitHub {category.upper()} Configurations\n"
                )

                content += (
                    f"# Updated: {timestamp}\n"
                )

                content += (
                    f"# Count: {len(configs)}\n"
                )

                content += (
                    "# Source: GitHub Repositories\n\n"
                )

                content += "\n".join(
                    configs
                )

                with open(
                    filename,
                    'w',
                    encoding='utf-8'
                ) as f:
                    f.write(content)

        all_configs = []

        for configs in categories.values():
            all_configs.extend(
                configs
            )

        if all_configs:
            filename = (
                "configs.txt/github/all.txt"
            )

            content = (
                "# All GitHub Configurations\n"
            )

            content += (
                f"# Updated: {timestamp}\n"
            )

            content += (
                f"# Total Count: {len(all_configs)}\n"
            )

            content += (
                "# Source: GitHub Repositories\n\n"
            )

            content += "\n".join(
                all_configs
            )

            with open(
                filename,
                'w',
                encoding='utf-8'
            ) as f:
                f.write(content)

        health_stats = getattr(
            self,
            "health_stats",
            {
                "checked": 0,
                "healthy": len(all_configs),
                "unstable": 0,
                "dead": 0,
                "unchecked": 0
            }
        )

        stats = {
            "source": "github",
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
                "other": len(
                    categories["other"]
                )
            },
            "health": health_stats
        }

        with open(
            "stats.json",
            'w',
            encoding='utf-8'
        ) as f:
            json.dump(
                stats,
                f,
                ensure_ascii=False,
                indent=2
            )

        return len(all_configs)


def main():
    print("=" * 60)
    print("ARISTA GITHUB CONFIG EXTRACTOR")
    print("=" * 60)

    try:
        extractor = GitHubConfigExtractor()

        (
            categories,
            total_count,
            failed_sources,
            failed_configs
        ) = extractor.process_sources()

        saved_count = extractor.save_results(
            categories,
            total_count
        )

        print("\n✅ PROCESSING COMPLETE")

        print(
            f"Total unique configs: {total_count}"
        )

        print(
            f"Configs saved: {saved_count}"
        )

        if failed_sources > 0:
            print(
                f"Failed sources: {failed_sources}"
            )

        if failed_configs > 0:
            print(
                f"Failed configs: {failed_configs}"
            )

    except Exception as e:
        print(
            f"\n❌ ERROR: {e}"
        )


if __name__ == "__main__":
    main()
