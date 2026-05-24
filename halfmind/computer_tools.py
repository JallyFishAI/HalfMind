import os
import subprocess
import platform
import webbrowser
import time
from pathlib import Path


class ComputerUseTools:
    """Tools for desktop automation, program launching, and screen interaction"""
    
    ALLOWED_PROGRAMS = {
        'windows': {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'wordpad': 'write.exe',
            'cmd': 'cmd.exe',
            'powershell': 'powershell.exe',
            'explorer': 'explorer.exe',
            'chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'vscode': 'code.exe',
            'task_manager': 'taskmgr.exe',
            'control_panel': 'control.exe',
            'settings': 'ms-settings:',
            'snipping_tool': 'SnippingTool.exe',
            'camera': 'microsoft.windows.camera:',
            'vlc': 'vlc.exe',
            'spotify': 'Spotify.exe',
            'discord': 'Discord.exe',
            'slack': 'slack.exe',
            'teams': 'ms-teams.exe',
            'zoom': 'Zoom.exe',
            'winrar': 'WinRAR.exe',
            '7zip': '7zFM.exe',
        },
        'linux': {
            'terminal': 'gnome-terminal',
            'konsole': 'konsole',
            'nautilus': 'nautilus',
            'dolphin': 'dolphin',
            'firefox': 'firefox',
            'chrome': 'google-chrome',
            'chromium': 'chromium-browser',
            'code': 'code',
            'gedit': 'gedit',
            'kate': 'kate',
            'vim': 'vim',
            'nano': 'nano',
            'calculator': 'gnome-calculator',
            'system_monitor': 'gnome-system-monitor',
            'file_manager': 'xdg-open',
            'vlc': 'vlc',
            'gimp': 'gimp',
            'inkscape': 'inkscape',
            'libreoffice': 'libreoffice',
        },
        'darwin': {
            'terminal': 'Terminal',
            'finder': 'Finder',
            'safari': 'Safari',
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'vscode': 'Visual Studio Code',
            'TextEdit': 'TextEdit',
            'calculator': 'Calculator',
            'preview': 'Preview',
            'photos': 'Photos',
            'music': 'Music',
            'notes': 'Notes',
            'calendar': 'Calendar',
            'mail': 'Mail',
            'slack': 'Slack',
            'zoom': 'zoom.us',
            'discord': 'Discord',
            'iterm2': 'iTerm',
        }
    }
    
    BROWSER_URL_WHITELIST = [
        'https://',
        'http://localhost',
        'http://127.0.0.1',
        'file://',
    ]
    
    def __init__(self, strict_mode=True, allowed_programs=None):
        self.strict_mode = strict_mode
        self.system = platform.system().lower()
        self.command_history = []
        if allowed_programs:
            self.custom_allowed = set(allowed_programs)
        else:
            self.custom_allowed = None
    
    def _get_allowed_programs(self):
        """Gets allowed programs for current platform"""
        if self.custom_allowed:
            return self.custom_allowed
        return set(self.ALLOWED_PROGRAMS.get(self.system, {}).keys())
    
    def _validate_program(self, program_name):
        """Validates if program is allowed to launch"""
        allowed = self._get_allowed_programs()
        if self.strict_mode and program_name not in allowed:
            raise ValueError(f"Program '{program_name}' not in allowed list. Allowed: {list(allowed)}")
        return True
    
    def _get_program_path(self, program_name):
        """Gets the actual program path/command"""
        platform_programs = self.ALLOWED_PROGRAMS.get(self.system, {})
        if program_name in platform_programs:
            return platform_programs[program_name]
        return program_name
    
    def _validate_url(self, url):
        """Validates URL for security"""
        if self.strict_mode:
            allowed = any(url.startswith(prefix) for prefix in self.BROWSER_URL_WHITELIST)
            if not allowed:
                raise ValueError(f"URL must start with: {self.BROWSER_URL_WHITELIST}")
        return True
    
    def list_allowed_programs(self):
        """Lists all allowed programs for current platform"""
        return list(self._get_allowed_programs())
    
    def open_program(self, program_name, arguments=None):
        """Opens a program with optional arguments"""
        self._validate_program(program_name)
        program_path = self._get_program_path(program_name)
        self.command_history.append({
            'action': 'open_program',
            'program': program_name,
            'timestamp': time.time()
        })
        try:
            if self.system == 'darwin':
                if arguments:
                    cmd = ['open', '-a', program_path, '--args'] + arguments
                else:
                    cmd = ['open', '-a', program_path]
            elif self.system == 'windows':
                cmd = [program_path]
                if arguments:
                    cmd.extend(arguments)
            else:
                cmd = [program_path]
                if arguments:
                    cmd.extend(arguments)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            return {
                'success': True,
                'program': program_name,
                'pid': process.pid
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def close_program(self, program_name):
        """Closes a running program by name"""
        self.command_history.append({
            'action': 'close_program',
            'program': program_name,
            'timestamp': time.time()
        })
        try:
            if self.system == 'windows':
                subprocess.run(['taskkill', '/IM', self._get_program_path(program_name), '/F'],
                             capture_output=True)
            elif self.system == 'darwin':
                subprocess.run(['pkill', '-f', program_name], capture_output=True)
            else:
                subprocess.run(['pkill', '-f', program_name], capture_output=True)
            return {'success': True, 'program': program_name}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def open_url(self, url, browser=None):
        """Opens a URL in the default or specified browser"""
        self._validate_url(url)
        self.command_history.append({
            'action': 'open_url',
            'url': url,
            'timestamp': time.time()
        })
        try:
            if browser:
                browser_path = self._get_program_path(browser)
                if self.system == 'darwin':
                    subprocess.Popen(['open', '-a', browser_path, url])
                elif self.system == 'windows':
                    subprocess.Popen([browser_path, url])
                else:
                    subprocess.Popen([browser_path, url])
            else:
                webbrowser.open(url)
            return {'success': True, 'url': url, 'browser': browser or 'default'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def open_urls_batch(self, urls, browser=None):
        """Opens multiple URLs"""
        results = []
        for url in urls:
            result = self.open_url(url, browser)
            results.append(result)
            time.sleep(0.5)
        return {
            'total': len(urls),
            'successful': sum(1 for r in results if r['success']),
            'results': results
        }
    
    def open_file(self, file_path):
        """Opens a file with the default application"""
        resolved = Path(file_path).resolve()
        if not resolved.exists():
            return {'success': False, 'error': f'File not found: {file_path}'}
        self.command_history.append({
            'action': 'open_file',
            'file': str(resolved),
            'timestamp': time.time()
        })
        try:
            if self.system == 'darwin':
                subprocess.Popen(['open', str(resolved)])
            elif self.system == 'windows':
                os.startfile(str(resolved))
            else:
                subprocess.Popen(['xdg-open', str(resolved)])
            return {'success': True, 'file': str(resolved)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def open_folder(self, folder_path):
        """Opens a folder in file explorer"""
        resolved = Path(folder_path).resolve()
        if not resolved.exists():
            return {'success': False, 'error': f'Folder not found: {folder_path}'}
        self.command_history.append({
            'action': 'open_folder',
            'folder': str(resolved),
            'timestamp': time.time()
        })
        try:
            if self.system == 'darwin':
                subprocess.Popen(['open', str(resolved)])
            elif self.system == 'windows':
                subprocess.Popen(['explorer', str(resolved)])
            else:
                subprocess.Popen(['xdg-open', str(resolved)])
            return {'success': True, 'folder': str(resolved)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def draw_image(self, width=800, height=600, output_path='drawing.png', shapes=None):
        """Draws an image with basic shapes using PIL"""
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        if shapes:
            for shape in shapes:
                shape_type = shape.get('type')
                color = shape.get('color', 'black')
                if shape_type == 'rectangle':
                    draw.rectangle(shape['coords'], outline=color, width=shape.get('width', 2))
                elif shape_type == 'ellipse':
                    draw.ellipse(shape['coords'], outline=color, width=shape.get('width', 2))
                elif shape_type == 'line':
                    draw.line(shape['coords'], fill=color, width=shape.get('width', 2))
                elif shape_type == 'polygon':
                    draw.polygon(shape['coords'], outline=color, fill=shape.get('fill'))
                elif shape_type == 'text':
                    draw.text(shape['position'], shape['text'], fill=color)
                elif shape_type == 'point':
                    draw.point(shape['coords'], fill=color)
        img.save(output_path)
        return {'success': True, 'path': output_path, 'width': width, 'height': height}
    
    def draw_with_canvas(self, output_path='canvas.png', width=800, height=600, background='white'):
        """Creates a canvas for drawing and returns it"""
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (width, height), color=background)
        return {
            'image': img,
            'draw': ImageDraw.Draw(img),
            'path': output_path,
            'save': lambda: img.save(output_path)
        }
    
    def screenshot(self, output_path='screenshot.png'):
        """Takes a screenshot of the current screen"""
        try:
            if self.system == 'darwin':
                subprocess.run(['screencapture', '-x', output_path])
            elif self.system == 'windows':
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                screenshot.save(output_path)
            else:
                subprocess.run(['gnome-screenshot', '-f', output_path])
            return {'success': True, 'path': output_path}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_screen_size(self):
        """Gets the current screen resolution"""
        try:
            if self.system == 'windows':
                import ctypes
                user32 = ctypes.windll.user32
                return {'width': user32.GetSystemMetrics(0), 'height': user32.GetSystemMetrics(1)}
            else:
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                return {'width': screenshot.width, 'height': screenshot.height}
        except Exception:
            return {'width': 1920, 'height': 1080}
    
    def type_text(self, text):
        """Types text using keyboard simulation"""
        try:
            if self.system == 'darwin':
                subprocess.run(['osascript', '-e', f'tell application "System Events" to keystroke "{text}"'])
            elif self.system == 'windows':
                import pyautogui
                pyautogui.typewrite(text)
            else:
                import pyautogui
                pyautogui.typewrite(text)
            return {'success': True, 'text': text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def press_key(self, key):
        """Presses a keyboard key"""
        try:
            if self.system == 'darwin':
                subprocess.run(['osascript', '-e', f'tell application "System Events" to key code {key}'])
            else:
                import pyautogui
                pyautogui.press(key)
            return {'success': True, 'key': key}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def hotkey(self, *keys):
        """Presses a hotkey combination"""
        try:
            if self.system == 'darwin':
                key_map = {'ctrl': 'control', 'alt': 'option', 'cmd': 'command'}
                mapped_keys = [key_map.get(k, k) for k in keys]
                key_str = ' down, '.join(mapped_keys) + ' down'
                subprocess.run(['osascript', '-e', f'tell application "System Events" to keystroke "{keys[-1]}" using {{{key_str}}}'])
            else:
                import pyautogui
                pyautogui.hotkey(*keys)
            return {'success': True, 'keys': keys}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def click_at(self, x, y, button='left'):
        """Clicks at specific coordinates"""
        try:
            import pyautogui
            pyautogui.click(x, y, button=button)
            return {'success': True, 'x': x, 'y': y, 'button': button}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def double_click_at(self, x, y):
        """Double clicks at specific coordinates"""
        try:
            import pyautogui
            pyautogui.doubleClick(x, y)
            return {'success': True, 'x': x, 'y': y}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def right_click_at(self, x, y):
        """Right clicks at specific coordinates"""
        try:
            import pyautogui
            pyautogui.rightClick(x, y)
            return {'success': True, 'x': x, 'y': y}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def drag_to(self, start_x, start_y, end_x, end_y, duration=0.5):
        """Drags from one position to another"""
        try:
            import pyautogui
            pyautogui.moveTo(start_x, start_y)
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            return {'success': True, 'from': (start_x, start_y), 'to': (end_x, end_y)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scroll(self, amount, x=None, y=None):
        """Scrolls the mouse wheel"""
        try:
            import pyautogui
            if x and y:
                pyautogui.scroll(amount, x=x, y=y)
            else:
                pyautogui.scroll(amount)
            return {'success': True, 'amount': amount}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_mouse_position(self):
        """Gets current mouse position"""
        try:
            import pyautogui
            x, y = pyautogui.position()
            return {'x': x, 'y': y}
        except Exception as e:
            return {'error': str(e)}
    
    def move_mouse(self, x, y, duration=0.2):
        """Moves mouse to coordinates"""
        try:
            import pyautogui
            pyautogui.moveTo(x, y, duration=duration)
            return {'success': True, 'x': x, 'y': y}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def copy_to_clipboard(self, text):
        """Copies text to clipboard"""
        try:
            if self.system == 'darwin':
                subprocess.run(['pbcopy'], input=text.encode())
            elif self.system == 'windows':
                subprocess.run(['clip'], input=text.encode())
            else:
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode())
            return {'success': True, 'copied': len(text)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_clipboard(self):
        """Gets text from clipboard"""
        try:
            if self.system == 'darwin':
                result = subprocess.run(['pbpaste'], capture_output=True, text=True)
            elif self.system == 'windows':
                result = subprocess.run(['powershell', '-command', 'Get-Clipboard'], capture_output=True, text=True)
            else:
                result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], capture_output=True, text=True)
            return {'text': result.stdout.strip()}
        except Exception as e:
            return {'error': str(e)}
    
    def get_running_processes(self):
        """Gets list of running processes"""
        try:
            import psutil
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return processes
        except Exception as e:
            return {'error': str(e)}
    
    def is_program_running(self, program_name):
        """Checks if a program is currently running"""
        processes = self.get_running_processes()
        if isinstance(processes, dict) and 'error' in processes:
            return processes
        for proc in processes:
            if program_name.lower() in proc.get('name', '').lower():
                return {'running': True, 'pid': proc['pid']}
        return {'running': False}
    
    def wait_for_program(self, program_name, timeout=30):
        """Waits for a program to start"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.is_program_running(program_name)
            if result.get('running'):
                return {'success': True, 'program': program_name, 'pid': result['pid']}
            time.sleep(0.5)
        return {'success': False, 'error': 'Timeout waiting for program'}
    
    def get_command_history(self):
        """Returns history of executed commands"""
        return self.command_history
    
    def clear_history(self):
        """Clears command history"""
        self.command_history = []
        return {'cleared': True}
