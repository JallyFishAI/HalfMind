import socket
import subprocess
import struct
import time
import threading
from collections import defaultdict


class NetworkTools:
    """Tools for network diagnostics and operations"""
    
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.scan_results = {}
    
    def ping(self, host, count=4):
        """Pings a host and returns statistics"""
        system = subprocess.run(['uname'], capture_output=True, text=True).stdout.strip()
        param = '-n' if system.lower() == 'windows' else '-c'
        cmd = ['ping', param, str(count), host]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout * count)
            output = result.stdout
            stats = {
                'host': host,
                'success': result.returncode == 0,
                'output': output
            }
            if result.returncode == 0:
                if 'windows' in system.lower():
                    lines = output.split('\n')
                    for line in lines:
                        if 'Average' in line:
                            parts = line.split(',')
                            for part in parts:
                                if 'Average' in part:
                                    stats['avg_ms'] = int(part.strip().split('=')[-1].replace('ms', ''))
                else:
                    lines = output.split('\n')
                    for line in lines:
                        if 'avg' in line.lower():
                            parts = line.split('/')
                            if len(parts) >= 4:
                                stats['avg_ms'] = float(parts[4].split('=')[-1].strip())
            return stats
        except subprocess.TimeoutExpired:
            return {'host': host, 'success': False, 'error': 'Timeout'}
    
    def dns_lookup(self, hostname):
        """Resolves hostname to IP addresses"""
        try:
            results = socket.getaddrinfo(hostname, None)
            addresses = list(set([r[4][0] for r in results]))
            return {
                'hostname': hostname,
                'addresses': addresses,
                'ipv4': [a for a in addresses if ':' not in a],
                'ipv6': [a for a in addresses if ':' in a]
            }
        except socket.gaierror as e:
            return {'hostname': hostname, 'error': str(e)}
    
    def reverse_dns(self, ip_address):
        """Performs reverse DNS lookup"""
        try:
            hostname, aliases, _ = socket.gethostbyaddr(ip_address)
            return {
                'ip': ip_address,
                'hostname': hostname,
                'aliases': aliases
            }
        except socket.herror:
            return {'ip': ip_address, 'error': 'No reverse DNS found'}
    
    def scan_port(self, host, port):
        """Scans a single port on a host"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            result = sock.connect_ex((host, port))
            sock.close()
            return {
                'host': host,
                'port': port,
                'open': result == 0
            }
        except socket.error as e:
            return {'host': host, 'port': port, 'error': str(e)}
    
    def scan_ports(self, host, ports, max_threads=50):
        """Scans multiple ports on a host"""
        results = []
        lock = threading.Lock()
        
        def scan_single(port):
            result = self.scan_port(host, port)
            with lock:
                results.append(result)
        
        threads = []
        for port in ports:
            t = threading.Thread(target=scan_single, args=(port,))
            threads.append(t)
            t.start()
            if len(threads) >= max_threads:
                for t in threads:
                    t.join()
                threads = []
        
        for t in threads:
            t.join()
        
        return sorted(results, key=lambda x: x['port'])
    
    def scan_common_ports(self, host):
        """Scans commonly used ports"""
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139,
            143, 443, 445, 993, 995, 1433, 1521, 3306,
            3389, 5432, 5900, 8080, 8443
        ]
        return self.scan_ports(host, common_ports)
    
    def scan_port_range(self, host, start_port, end_port, max_threads=100):
        """Scans a range of ports"""
        ports = list(range(start_port, end_port + 1))
        return self.scan_ports(host, ports, max_threads)
    
    def get_service_name(self, port, protocol='tcp'):
        """Gets the service name for a port"""
        try:
            return socket.getservbyport(port, protocol)
        except OSError:
            return 'unknown'
    
    def traceroute(self, host, max_hops=30):
        """Performs traceroute to a host"""
        system = subprocess.run(['uname'], capture_output=True, text=True).stdout.strip()
        if 'windows' in system.lower():
            cmd = ['tracert', '-h', str(max_hops), host]
        else:
            cmd = ['traceroute', '-m', str(max_hops), host]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return {
                'host': host,
                'success': result.returncode == 0,
                'output': result.stdout
            }
        except subprocess.TimeoutExpired:
            return {'host': host, 'error': 'Traceroute timed out'}
    
    def whois_lookup(self, domain):
        """Performs WHOIS lookup"""
        try:
            import whois
            w = whois.whois(domain)
            return {
                'domain': domain,
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'name_servers': w.name_servers,
                'status': w.status,
                'emails': w.emails
            }
        except Exception as e:
            return {'domain': domain, 'error': str(e)}
    
    def get_local_ip(self):
        """Gets the local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return {'local_ip': ip}
        except Exception as e:
            return {'error': str(e)}
    
    def get_public_ip(self):
        """Gets the public IP address"""
        import requests
        try:
            response = requests.get('https://api.ipify.org?format=json', timeout=self.timeout)
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_mac_address(self):
        """Gets the MAC address of the primary network interface"""
        import uuid
        mac = uuid.getnode()
        mac_str = ':'.join(f'{(mac >> i) & 0xff:02x}' for i in range(0, 48, 8))
        return {'mac_address': mac_str}
    
    def check_proxy(self, proxy_url):
        """Checks if a proxy is working"""
        import requests
        try:
            proxies = {'http': proxy_url, 'https': proxy_url}
            response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=self.timeout)
            return {
                'proxy': proxy_url,
                'working': True,
                'response': response.json()
            }
        except Exception as e:
            return {'proxy': proxy_url, 'working': False, 'error': str(e)}
    
    def tcp_connect(self, host, port, message=None):
        """Establishes TCP connection and optionally sends message"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((host, port))
            if message:
                sock.sendall(message.encode())
                response = sock.recv(4096).decode()
            else:
                response = None
            sock.close()
            return {
                'host': host,
                'port': port,
                'connected': True,
                'response': response
            }
        except Exception as e:
            return {'host': host, 'port': port, 'connected': False, 'error': str(e)}
    
    def udp_send(self, host, port, message):
        """Sends UDP message"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        try:
            sock.sendto(message.encode(), (host, port))
            sock.close()
            return {'host': host, 'port': port, 'sent': True}
        except Exception as e:
            return {'host': host, 'port': port, 'sent': False, 'error': str(e)}
    
    def get_network_interfaces(self):
        """Gets all network interfaces and their addresses"""
        import psutil
        interfaces = []
        for name, addrs in psutil.net_if_addrs().items():
            interface = {'name': name, 'addresses': []}
            for addr in addrs:
                interface['addresses'].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask
                })
            interfaces.append(interface)
        return interfaces
    
    def get_bandwidth_usage(self):
        """Gets current bandwidth usage"""
        import psutil
        counters = psutil.net_io_counters()
        return {
            'bytes_sent': counters.bytes_sent,
            'bytes_recv': counters.bytes_recv,
            'packets_sent': counters.packets_sent,
            'packets_recv': counters.packets_recv
        }
    
    def monitor_bandwidth(self, duration=5, interval=1):
        """Monitors bandwidth usage over time"""
        import psutil
        import time
        readings = []
        start = psutil.net_io_counters()
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(interval)
            current = psutil.net_io_counters()
            readings.append({
                'timestamp': time.time(),
                'bytes_sent': current.bytes_sent - start.bytes_sent,
                'bytes_recv': current.bytes_recv - start.bytes_recv,
                'send_rate': (current.bytes_sent - start.bytes_sent) / (time.time() - start_time),
                'recv_rate': (current.bytes_recv - start.bytes_recv) / (time.time() - start_time)
            })
        return readings
    
    def is_port_available(self, port, host='localhost'):
        """Checks if a port is available"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0
    
    def find_available_port(self, start_port=8000, end_port=9000):
        """Finds an available port in range"""
        for port in range(start_port, end_port + 1):
            if self.is_port_available(port):
                return port
        return None
    
    def create_socket_server(self, host, port, handler, max_connections=5):
        """Creates a simple TCP socket server"""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(max_connections)
        return server
    
    def http_request(self, method, url, headers=None, data=None):
        """Makes an HTTP request"""
        import requests
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                data=data,
                timeout=self.timeout
            )
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text
            }
        except Exception as e:
            return {'error': str(e)}
    
    def websocket_connect(self, url):
        """Connects to a WebSocket"""
        try:
            import websocket
            ws = websocket.create_connection(url, timeout=self.timeout)
            return {'connected': True, 'url': url}
        except Exception as e:
            return {'connected': False, 'error': str(e)}