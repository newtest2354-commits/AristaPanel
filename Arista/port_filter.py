import os
import re
import base64
import json
from urllib.parse import urlparse, unquote
from datetime import datetime

class PortFilter:
    def __init__(self):
        self.ports = [80, 8080, 443, 8443, 2096, 2087, 2053, 8880, 2083, 2086, 2095, 2052, 8443, 9443]
        self.categories = ['vmess', 'vless', 'trojan', 'ss', 'hysteria2', 'hysteria', 'tuic', 'wireguard', 'other']
        self.source_dirs = ['telegram', 'github', 'combined']
        self.output_root = 'port.txt'

    def ensure_output_dirs(self):
        os.makedirs(self.output_root, exist_ok=True)
        for source in self.source_dirs:
            os.makedirs(os.path.join(self.output_root, source), exist_ok=True)

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

    def categorize_by_port(self, configs):
        port_dict = {port: [] for port in self.ports}
        other_ports = []
        for config in configs:
            port = self.extract_port(config)
            if port in self.ports:
                port_dict[port].append(config)
            else:
                other_ports.append(config)
        return port_dict, other_ports

    def process_source(self, source_dir, source_name):
        source_path = os.path.join('configs.txt', source_dir)
        if not os.path.exists(source_path):
            return

        all_configs = []
        for category in self.categories:
            cat_dir = os.path.join(source_path, category)
            if os.path.exists(cat_dir):
                for tier_file in os.listdir(cat_dir):
                    if tier_file.endswith('.txt'):
                        filepath = os.path.join(cat_dir, tier_file)
                        configs = self.read_config_file(filepath)
                        all_configs.extend(configs)

        if not all_configs:
            return

        port_dict, other_ports = self.categorize_by_port(all_configs)
        output_base = os.path.join(self.output_root, source_dir)
        os.makedirs(output_base, exist_ok=True)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for port, configs in port_dict.items():
            if configs:
                filename = os.path.join(output_base, f'port_{port}.txt')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f'# {source_name.upper()} - Port {port}\n')
                    f.write(f'# Updated: {timestamp}\n')
                    f.write(f'# Count: {len(configs)}\n\n')
                    f.write('\n'.join(configs))

        if other_ports:
            filename = os.path.join(output_base, 'other_ports.txt')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f'# {source_name.upper()} - Other Ports\n')
                f.write(f'# Updated: {timestamp}\n')
                f.write(f'# Count: {len(other_ports)}\n\n')
                f.write('\n'.join(other_ports))

        all_filename = os.path.join(output_base, 'all_ports.txt')
        with open(all_filename, 'w', encoding='utf-8') as f:
            f.write(f'# {source_name.upper()} - All Ports\n')
            f.write(f'# Updated: {timestamp}\n')
            f.write(f'# Total Configs: {len(all_configs)}\n\n')
            f.write('\n'.join(all_configs))

    def process_all(self):
        self.ensure_output_dirs()
        sources = {
            'telegram': 'TELEGRAM',
            'github': 'GITHUB',
            'combined': 'COMBINED'
        }
        for source_dir, source_name in sources.items():
            self.process_source(source_dir, source_name)

        print('=' * 60)
        print('PORT FILTER PROCESSING COMPLETE')
        print('=' * 60)
        print(f'Output directory: {self.output_root}/')
        for source in sources.keys():
            source_path = os.path.join(self.output_root, source)
            if os.path.exists(source_path):
                files = os.listdir(source_path)
                print(f'  {source}/: {len(files)} files')
        print('=' * 60)

def main():
    try:
        filter = PortFilter()
        filter.process_all()
    except Exception as e:
        print(f'ERROR: {e}')

if __name__ == '__main__':
    main()
