import os
import sys
import subprocess
import platform
import shutil
import psutil
from pathlib import Path


class SystemTools:
    """Tools for system operations and process management"""
    
    DANGEROUS_COMMANDS = ['rm -rf', 'format', 'del /f', 'shutdown', 'reboot']
    MAX_OUTPUT_SIZE = 1024 * 1024
    
    def __init__(self, sandbox_mode=True):
        self.sandbox_mode = sandbox_mode
        self.command_history = []
    
    def _validate_command(self, command):
        """Validates command for security"""
        command_lower = command.lower()
        for dangerous in self.DANGEROUS_COMMANDS:
            if dangerous in command_lower:
                raise ValueError(f"Dangerous command detected: {dangerous}")
        return command
    
    def run_command(self, command, timeout=60, capture_output=True):
        """Executes a shell command with safety checks"""
        validated_command = self._validate_command(command)
        self.command_history.append({
            'command': command,
            'timestamp': __import__('time').time()
        })
        try:
            result = subprocess.run(
                validated_command,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout[:self.MAX_OUTPUT_SIZE] if result.stdout else '',
                'stderr': result.stderr[:self.MAX_OUTPUT_SIZE] if result.stderr else ''
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out'
            }
    
    def run_python_script(self, script_path, args=None, timeout=60):
        """Executes a Python script"""
        validated_path = Path(script_path).resolve()
        if not validated_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        cmd = [sys.executable, str(validated_path)]
        if args:
            cmd.extend(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout[:self.MAX_OUTPUT_SIZE],
                'stderr': result.stderr[:self.MAX_OUTPUT_SIZE]
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Script execution timed out'}
    
    def get_system_info(self):
        """Returns detailed system information"""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_executable': sys.executable,
            'hostname': platform.node(),
            'cpu_count': os.cpu_count(),
            'current_directory': os.getcwd(),
            'user': os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
        }
    
    def get_memory_info(self):
        """Returns memory usage information"""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percentage': mem.percent,
            'total_gb': round(mem.total / (1024**3), 2),
            'available_gb': round(mem.available / (1024**3), 2)
        }
    
    def get_cpu_info(self):
        """Returns CPU usage information"""
        return {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
        }
    
    def get_disk_info(self, path='/'):
        """Returns disk usage information"""
        usage = psutil.disk_usage(path)
        return {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percentage': usage.percent,
            'total_gb': round(usage.total / (1024**3), 2),
            'free_gb': round(usage.free / (1024**3), 2)
        }
    
    def list_processes(self, name_filter=None):
        """Lists running processes"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
            try:
                pinfo = proc.info
                if name_filter and name_filter.lower() not in pinfo['name'].lower():
                    continue
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'status': pinfo['status'],
                    'cpu_percent': pinfo['cpu_percent'],
                    'memory_percent': pinfo['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    
    def get_process_info(self, pid):
        """Returns detailed information about a specific process"""
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'create_time': proc.create_time(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'memory_info': proc.memory_info()._asdict(),
                'num_threads': proc.num_threads(),
                'username': proc.username(),
                'cmdline': proc.cmdline(),
                'cwd': proc.cwd() if proc.status() != psutil.STATUS_ZOMBIE else None
            }
        except psutil.NoSuchProcess:
            return {'error': f'Process {pid} not found'}
    
    def kill_process(self, pid, force=False):
        """Terminates a process by PID"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            return {'success': True, 'message': f'Process {pid} terminated'}
        except psutil.NoSuchProcess:
            return {'success': False, 'error': f'Process {pid} not found'}
        except psutil.AccessDenied:
            return {'success': False, 'error': f'Access denied for process {pid}'}
    
    def monitor_process(self, pid, duration=5, interval=1):
        """Monitors a process for specified duration"""
        import time
        if not psutil.pid_exists(pid):
            return {'error': f'Process {pid} not found'}
        readings = []
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                proc = psutil.Process(pid)
                readings.append({
                    'timestamp': time.time(),
                    'cpu_percent': proc.cpu_percent(),
                    'memory_percent': proc.memory_percent(),
                    'num_threads': proc.num_threads()
                })
                time.sleep(interval)
            except psutil.NoSuchProcess:
                break
        return {
            'pid': pid,
            'duration': duration,
            'readings': readings,
            'avg_cpu': sum(r['cpu_percent'] for r in readings) / len(readings) if readings else 0,
            'avg_memory': sum(r['memory_percent'] for r in readings) / len(readings) if readings else 0
        }
    
    def get_environment_variables(self):
        """Returns all environment variables"""
        return dict(os.environ)
    
    def set_environment_variable(self, name, value):
        """Sets an environment variable"""
        os.environ[name] = str(value)
        return {'name': name, 'value': value}
    
    def get_network_interfaces(self):
        """Returns network interface information"""
        interfaces = []
        for name, addrs in psutil.net_if_addrs().items():
            interface = {'name': name, 'addresses': []}
            for addr in addrs:
                interface['addresses'].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                })
            interfaces.append(interface)
        return interfaces
    
    def get_network_connections(self):
        """Returns active network connections"""
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            connections.append({
                'fd': conn.fd,
                'family': conn.family,
                'type': conn.type,
                'local_addr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                'remote_addr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                'status': conn.status,
                'pid': conn.pid
            })
        return connections
    
    def get_boot_time(self):
        """Returns system boot time"""
        from datetime import datetime
        boot_time = psutil.boot_time()
        return {
            'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
            'uptime_seconds': __import__('time').time() - boot_time
        }
    
    def create_scheduled_task(self, name, command, schedule_type, schedule_value):
        """Creates a scheduled task (Windows) or cron job (Linux)"""
        system = platform.system()
        if system == 'Windows':
            cmd = f'schtasks /create /tn "{name}" /tr "{command}" /sc {schedule_type} /{schedule_value}'
        elif system == 'Linux':
            cron_entry = f"{schedule_value} {command}"
            cmd = f'(crontab -l 2>/dev/null; echo "{cron_entry}") | crontab -'
        else:
            return {'error': f'Unsupported platform: {system}'}
        return self.run_command(cmd)
    
    def cleanup_temp_files(self, days_old=7):
        """Removes temporary files older than specified days"""
        import time
        temp_dirs = ['/tmp', '/var/tmp']
        if platform.system() == 'Windows':
            temp_dirs = [os.environ.get('TEMP', ''), os.environ.get('TMP', '')]
        removed = []
        current_time = time.time()
        for temp_dir in temp_dirs:
            if not os.path.exists(temp_dir):
                continue
            for item in Path(temp_dir).iterdir():
                try:
                    item_stat = item.stat()
                    age_days = (current_time - item_stat.st_mtime) / 86400
                    if age_days > days_old:
                        if item.is_file():
                            item.unlink()
                            removed.append(str(item))
                        elif item.is_dir():
                            shutil.rmtree(item)
                            removed.append(str(item))
                except (PermissionError, OSError):
                    continue
        return {'removed_count': len(removed), 'files': removed[:100]}
    
    def get_installed_packages(self):
        """Returns list of installed Python packages"""
        import pkg_resources
        packages = []
        for dist in pkg_resources.working_set:
            packages.append({
                'name': dist.project_name,
                'version': dist.version,
                'location': dist.location
            })
        return sorted(packages, key=lambda x: x['name'].lower())
    
    def check_port_availability(self, port, host='localhost'):
        """Checks if a port is available"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        sock.close()
        return {
            'port': port,
            'host': host,
            'available': result != 0,
            'status': 'closed' if result != 0 else 'open'
        }
    
    def get_command_history(self):
        """Returns command execution history"""
        return self.command_history
    
    def clear_command_history(self):
        """Clears command execution history"""
        self.command_history = []
        return {'cleared': True}