import pyautogui
import subprocess
import os
import webbrowser
import json
import datetime
from config import CUSTOM_APPS

class CommandParser:
    def __init__(self, audio_engine):
        self.audio = audio_engine
        # Load saved custom commands from disk
        self.custom_commands_file = os.path.join(os.path.dirname(__file__), '..', 'custom_commands.json')
        self.custom_commands = self._load_custom_commands()
        # Volume level tracking
        self._volume_steps = 10

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load_custom_commands(self):
        if os.path.exists(self.custom_commands_file):
            with open(self.custom_commands_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_custom_commands(self):
        with open(self.custom_commands_file, 'w') as f:
            json.dump(self.custom_commands, f, indent=2)

    # ── Main dispatch ─────────────────────────────────────────────────────────

    def execute(self, text):
        text = text.lower().strip()

        # Try user-defined custom commands first
        for trigger, action in self.custom_commands.items():
            if trigger in text:
                self.audio.speak(f"Running {trigger}.")
                os.system(action)
                return True

        # Route to the appropriate skill
        if self._app_control(text):      return True
        if self._web_skill(text):        return True
        if self._media_skill(text):      return True
        if self._window_skill(text):     return True
        if self._keyboard_skill(text):   return True
        if self._system_skill(text):     return True
        if self._file_skill(text):       return True
        if self._dictation_skill(text):  return True
        if self._screenshot_skill(text): return True
        if self._time_skill(text):       return True

        return False  # Nothing matched

    # ── Skills ────────────────────────────────────────────────────────────────

    def _app_control(self, text):
        """Open or close ANY application."""
        # Closing
        if "close " in text or "kill " in text or "quit " in text:
            app = text.replace("close ", "").replace("kill ", "").replace("quit ", "").strip()
            exe = CUSTOM_APPS.get(app, app)
            # Clean exe name
            exe_name = os.path.basename(exe).replace(".exe", "")
            self.audio.speak(f"Closing {app}.")
            os.system(f'taskkill /F /IM {exe_name}.exe /T 2>nul')
            return True

        # Opening
        if text.startswith("open ") or text.startswith("launch ") or text.startswith("start "):
            app = (text.replace("open ", "")
                       .replace("launch ", "")
                       .replace("start ", "")
                       .strip())
            exe = CUSTOM_APPS.get(app, app)
            self.audio.speak(f"Opening {app}.")
            # Try start command first (handles ms-settings: URIs, paths, names)
            os.system(f'start "" "{exe}"')
            return True

        return False

    def _web_skill(self, text):
        """Browser and search commands."""
        if text.startswith("search for ") or text.startswith("google ") or text.startswith("search "):
            query = (text.replace("search for ", "")
                        .replace("google ", "")
                        .replace("search ", "")
                        .strip())
            self.audio.speak(f"Searching for {query}.")
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            return True

        if "open youtube" in text or "go to youtube" in text:
            query_match = text.replace("open youtube", "").replace("go to youtube", "").strip()
            if query_match:
                self.audio.speak(f"Searching YouTube for {query_match}.")
                webbrowser.open(f"https://www.youtube.com/results?search_query={query_match.replace(' ', '+')}")
            else:
                self.audio.speak("Opening YouTube.")
                webbrowser.open("https://www.youtube.com")
            return True

        if text.startswith("go to ") or "open website" in text:
            site = text.replace("go to ", "").replace("open website", "").strip()
            if "." not in site:
                site = site + ".com"
            self.audio.speak(f"Opening {site}.")
            webbrowser.open(f"https://{site}")
            return True

        return False

    def _media_skill(self, text):
        """Music and media playback controls."""
        if "play" in text and "pause" not in text:
            self.audio.speak("Playing.")
            pyautogui.press('playpause')
            return True
        if "pause" in text or "stop music" in text:
            self.audio.speak("Pausing.")
            pyautogui.press('playpause')
            return True
        if "next track" in text or "next song" in text or "skip" in text:
            self.audio.speak("Next track.")
            pyautogui.press('nexttrack')
            return True
        if "previous track" in text or "previous song" in text or "go back" in text:
            self.audio.speak("Previous track.")
            pyautogui.press('prevtrack')
            return True
        if "volume up" in text or "turn it up" in text or "louder" in text:
            self.audio.speak("Turning up the volume.")
            for _ in range(self._volume_steps):
                pyautogui.press('volumeup')
            return True
        if "volume down" in text or "turn it down" in text or "quieter" in text:
            self.audio.speak("Turning down the volume.")
            for _ in range(self._volume_steps):
                pyautogui.press('volumedown')
            return True
        if "mute" in text:
            self.audio.speak("Muting.")
            pyautogui.press('volumemute')
            return True
        if "unmute" in text:
            self.audio.speak("Unmuting.")
            pyautogui.press('volumemute')
            return True
        return False

    def _window_skill(self, text):
        """Window management commands."""
        if "minimize all" in text or "show desktop" in text:
            self.audio.speak("Showing desktop.")
            pyautogui.hotkey('win', 'd')
            return True
        if "minimize" in text:
            self.audio.speak("Minimizing window.")
            pyautogui.hotkey('win', 'down')
            return True
        if "maximize" in text:
            self.audio.speak("Maximizing window.")
            pyautogui.hotkey('win', 'up')
            return True
        if "switch window" in text or "alt tab" in text:
            self.audio.speak("Switching window.")
            pyautogui.hotkey('alt', 'tab')
            return True
        if "snap left" in text:
            self.audio.speak("Snapping left.")
            pyautogui.hotkey('win', 'left')
            return True
        if "snap right" in text:
            self.audio.speak("Snapping right.")
            pyautogui.hotkey('win', 'right')
            return True
        if "close window" in text or "close this" in text:
            self.audio.speak("Closing window.")
            pyautogui.hotkey('alt', 'f4')
            return True
        if "new tab" in text:
            self.audio.speak("Opening new tab.")
            pyautogui.hotkey('ctrl', 't')
            return True
        if "close tab" in text:
            self.audio.speak("Closing tab.")
            pyautogui.hotkey('ctrl', 'w')
            return True
        return False

    def _keyboard_skill(self, text):
        """Generic keyboard shortcut commands."""
        shortcuts = {
            "copy":          ('ctrl', 'c'),
            "paste":         ('ctrl', 'v'),
            "cut":           ('ctrl', 'x'),
            "undo":          ('ctrl', 'z'),
            "redo":          ('ctrl', 'y'),
            "select all":    ('ctrl', 'a'),
            "save":          ('ctrl', 's'),
            "save as":       ('ctrl', 'shift', 's'),
            "find":          ('ctrl', 'f'),
            "zoom in":       ('ctrl', '='),
            "zoom out":      ('ctrl', '-'),
            "refresh":       ('f5',),
            "go back":       ('alt', 'left'),
            "go forward":    ('alt', 'right'),
            "full screen":   ('f11',),
            "escape":        ('esc',),
            "enter":         ('enter',),
            "print":         ('ctrl', 'p'),
        }
        for phrase, keys in shortcuts.items():
            if phrase in text:
                self.audio.speak(f"{phrase.capitalize()}.")
                pyautogui.hotkey(*keys)
                return True
        return False

    def _system_skill(self, text):
        """PC power and system commands."""
        if "shut down" in text or "shutdown" in text:
            self.audio.speak("Shutting down. Goodbye, sir.")
            os.system("shutdown /s /t 5")
            return True
        if "restart" in text or "reboot" in text:
            self.audio.speak("Restarting the system.")
            os.system("shutdown /r /t 5")
            return True
        if "sleep" in text or "hibernate" in text:
            self.audio.speak("Going to sleep.")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return True
        if "lock" in text:
            self.audio.speak("Locking your PC, sir.")
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return True
        if "task manager" in text:
            self.audio.speak("Opening Task Manager.")
            os.system("start taskmgr")
            return True
        if "empty recycle bin" in text:
            self.audio.speak("Emptying the recycle bin.")
            subprocess.run(
                ['powershell', '-Command', 'Clear-RecycleBin -Confirm:$false'],
                capture_output=True
            )
            return True
        if "check battery" in text:
            result = subprocess.run(
                ['powershell', '-Command',
                 '(Get-WmiObject -Class Win32_Battery).EstimatedChargeRemaining'],
                capture_output=True, text=True
            )
            level = result.stdout.strip()
            if level:
                self.audio.speak(f"Battery is at {level} percent.")
            else:
                self.audio.speak("I couldn't determine the battery level. You may be on AC power.")
            return True
        return False

    def _file_skill(self, text):
        """File and folder operations."""
        if "open downloads" in text:
            self.audio.speak("Opening your Downloads folder.")
            os.system("start %USERPROFILE%\\Downloads")
            return True
        if "open documents" in text:
            self.audio.speak("Opening your Documents folder.")
            os.system("start %USERPROFILE%\\Documents")
            return True
        if "open desktop" in text:
            self.audio.speak("Opening your Desktop.")
            os.system("start %USERPROFILE%\\Desktop")
            return True
        if "open pictures" in text:
            self.audio.speak("Opening your Pictures folder.")
            os.system("start %USERPROFILE%\\Pictures")
            return True
        if "open music" in text:
            self.audio.speak("Opening your Music folder.")
            os.system("start %USERPROFILE%\\Music")
            return True
        if "open videos" in text:
            self.audio.speak("Opening your Videos folder.")
            os.system("start %USERPROFILE%\\Videos")
            return True
        return False

    def _dictation_skill(self, text):
        """Type text via voice."""
        if text.startswith("type "):
            content = text.replace("type ", "").strip()
            self.audio.speak("Typing.")
            pyautogui.write(content, interval=0.03)
            return True
        return False

    def _screenshot_skill(self, text):
        """Take a screenshot."""
        if "screenshot" in text or "take a screenshot" in text:
            path = os.path.join(os.path.expanduser("~"), "Desktop",
                                f"tars_screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            self.audio.speak("Screenshot saved to your Desktop, sir.")
            return True
        return False

    def _time_skill(self, text):
        """Tell the current time or date."""
        if "what time" in text or "current time" in text:
            now = datetime.datetime.now().strftime("%I:%M %p")
            self.audio.speak(f"The current time is {now}.")
            return True
        if "what day" in text or "today's date" in text or "what date" in text:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.audio.speak(f"Today is {today}.")
            return True
        return False
