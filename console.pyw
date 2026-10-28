import numpy as np
import tkinter as tk
from tkinter import font as tkfont
from threading import Thread
import datetime
import logging
import pygame
import sys
import os
import time

class Console:
    def __init__(self, root):
        self.setup_logging()
        self.logger.info("="*50)
        self.logger.info("SESSION STARTED")
        self.logger.info("="*50)
        
        self.root = root
        self.root.title("Console BETA 1.1")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#000000")
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        self.playlist = []
        self.buffer = []
        self.key_states = {}
        self.keysounds = False
        self.toggle = False
        self.pause = False
        self.volume = 0.3
        self.current_track_index = 0
        self.is_playing = False
        self.auto_play_next = True
        self.track_length = 0
        self.start_time = 0
        self.last_update_time = 0
        self.repeat = False
        self.Loading = False
        self.enable = True
        
        self.console = tk.Text(
            root, 
            font=("Courier New", 12), 
            bg="#000000", 
            fg="#00FF00",
            wrap=tk.WORD, 
            state="disabled",
            selectbackground="#006600",
            selectforeground="#FFFFFF",
            inactiveselectbackground="#006600",
            insertbackground="#00FF00",
            insertwidth=2
        )
        self.console.grid(row=0, column=0, columnspan=100, sticky="nsew", padx=5, pady=5)
        ##############################
        self.progress_frame = None
        self.progress_label = None
        self.progress_slider = None
        self.progress_canvas = None
        self.progress_bar = None
        ##############################
        self.progress_remaining = None
        ##############################
                
        self.music_folder = "music"
        self.supported_formats = ('.mp3', '.wav', '.ogg') #//add more formats
        self.TRACK_END = pygame.USEREVENT + 1
                
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(self.TRACK_END)
        self.load_sounds()
        self.load_tracks()
        self.set_volume(self.volume)
        
        self.entry = tk.Entry(
            root, 
            font=("Courier New", 12), 
            bg="#000000", 
            fg="#00FF00", 
            insertbackground="#00FF00", 
            selectbackground="#008000",
            selectforeground="#FFFFFF"
        )
        self.entry.grid(row=100, column=0, columnspan=100, sticky="ew", padx=5, pady=5)
        
        self.control_frame = tk.Frame(root, bg="#000000")
        self.control_frame.grid(row=1, column=0, columnspan=100, sticky="ew", padx=5, pady=5)
        
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(100, weight=0)
    
        self.entry.bind("<Return>", self.process_input)
        self.key_sounds()
        self.root.after(100, self.check_events)
        self.root.after(100, self.update_progress)
        
        button_style = {
            "bg": "#003300",
            "fg": "#00FF00",
            "activebackground": "#006600",
            "activeforeground": "#00FF00",
            "relief": tk.RAISED,
            "borderwidth": 2,
            "font": ("Courier New", 10)
        }
        
        self.commands = {
            "help": {
                "func": self.cmd_help,
                "desc": "displays a list of available commands"
            },
            "clear": {
                "func": self.cmd_clear,
                "desc": "clears the console"
            },
            "echo": {
                "func": self.cmd_echo,
                "desc": "prints the given text"
            },
            "exit": {
                "func": self.cmd_exit,
                "desc": "exits the program"
            },
            "forcedexit": {
                "func": self.cmd_forced_exit,
                "desc": "force exits the program"
            },
            "mediaplayer": {
                "func": self.cmd_mediaplayer,
                "desc": "call media player"
            },
            "playlist": {
                "func": self.cmd_playlist,
                "desc": "show current playlist"
            },
            "playtracks": {
                "func": self.cmd_play_tracks,
                "desc": "plays tracks"
            },
            "stoptrack": {
                "func": self.cmd_stop_track,
                "desc": "stops playing track"
            },
            "pause": {
                "func": self.cmd_pause,
                "desc": "pauses the track"
            },
            "unpause": {
                "func": self.cmd_unpause,
                "desc": "unpauses the track"
            },
            "nexttrack": {
                "func": self.cmd_next_track,
                "desc": "plays the next track"
            },
            "previoustrack": {
                "func": self.cmd_previous_track,
                "desc": "plays previous music"
            },
            "repeattrack": {
                "func": self.cmd_repeat_track,
                "desc": "repeats the current track"
            },
            "reloadtracks": {
                "func": self.cmd_reload_tracks,
                "desc": "reloads tracks from folder"
            },
            "closemediaplayer": {
                "func": self.cmd_close_mediaplayer,
                "desc": "closes the media player"
            },
            "enablekeysounds": {
                "func": self.cmd_enable_key_sounds,
                "desc": "enables key sounds"
            },
            "disablekeysounds": {
                "func": self.cmd_disable_key_sounds,
                "desc": "disables key sounds"
            },
            "setvolume": {
                "func": self.cmd_set_volume,
                "desc": "sets volume level"
            },
        }
        
        self.print_message("hi, this is console version 1.1!. type \"/help\" for help", "info")
        self.play_sound('welcome')
        
        #self.cmd_mediaplayer() //test
        #self.cmd_playtracks() //test
        #self.enablekeysounds() //test
        
    #################################################################################################
    # ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! #
    #################################################################################################
    
    def setup_logging(self):
        try:
            os.makedirs('logs', exist_ok=True)

            self.logger = logging.getLogger('ConsoleLogger')
            self.logger.setLevel(logging.DEBUG)

            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S')

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_handler = logging.FileHandler(f'logs/console_{timestamp}.log',encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)

            latest_handler = logging.FileHandler('logs/latest.log', mode='w', encoding='utf-8')
            latest_handler.setFormatter(formatter)
            latest_handler.setLevel(logging.DEBUG)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(latest_handler)
        
        except Exception as e:
            print(f"logging setup error: {e}")
        
    def create_progress_bar(self):
        if self.progress_frame is None:
            self.progress_frame = tk.Frame(self.root, bg="#000000", height = 0)
            self.progress_frame.grid(row=1, column=0, columnspan=100, sticky="ew", padx=5, pady=0)
            self.progress_frame.grid_propagate(False)
            
            self.progress_label = tk.Label(
                self.progress_frame, 
                text="00:00 / 00:00", 
                font=("Courier New", 10), 
                bg="#000000", 
                fg="#00FF00"
            )
            self.progress_label.pack(side=tk.RIGHT, padx=5)
            
            self.progress_canvas = tk.Canvas(
                self.progress_frame, 
                height=10, 
                bg="#000000", 
                highlightthickness=0
            )
            self.progress_canvas.pack(fill=tk.X, expand=True)

            self.progress_bar = self.progress_canvas.create_rectangle(
                0, 0, 0, 10, 
                fill="#006600", 
                outline="#006600"
            )
            self.progress_remaining = self.progress_canvas.create_rectangle(
                0, 0, 600, 10, 
                fill="#000000", 
                outline="#000000"
            )
            
            self.entry.grid(row=2, column=0, columnspan=100, sticky="ew", padx=5, pady=5)
            
            self.update_progress()

    ##############################################################################################
    
    def destroy_progress_bar(self):
        if self.progress_frame is not None:
            self.progress_frame.destroy()
            self.progress_frame = None
            self.progress_label = None
            self.progress_canvas = None
            self.progress_bar = None
            self.progress_remaining = None
            
            self.entry.grid(row=1, column=0, columnspan=100, sticky="ew", padx=5, pady=5)

    ##############################################################################################
    
    ##############################################################################################     
    def update_progress(self):
        if self.is_playing and not self.pause:
            current_time = pygame.mixer.music.get_pos() / 1000
            if current_time > 0 and self.track_length > 0:
                progress = min(current_time / self.track_length, 1.0)
                width = self.progress_canvas.winfo_width()
                progress_width = int(width * progress)
                
                self.progress_canvas.coords(self.progress_bar, 0, 0, progress_width, 10)
                self.progress_canvas.coords(self.progress_remaining, progress_width, 0, width, 10)
                
                current_str = time.strftime('%M:%S', time.gmtime(current_time))
                length_str = time.strftime('%M:%S', time.gmtime(self.track_length))
                self.progress_label.config(text=f"{current_str} / {length_str}")

        if self.toggle:
            self.root.after(100, self.update_progress)
    ##############################################################################################
    
    ##############################################################################################
    
    def key_sounds(self):
        if self.keysounds:
            self.root.bind("<KeyPress>", self.on_key_press)
            self.root.bind("<KeyRelease>", self.on_key_release)
        else:
            self.root.unbind("<KeyPress>")
            self.root.unbind("<KeyRelease>")
    
    def on_key_press(self, event):
        if event.keysym not in ("Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R", "Meta_L", "Meta_R"):
            if not self.key_states.get(event.keysym, False):
                self.key_states[event.keysym] = True
                self.play_sound('press_down')

    def on_key_release(self, event):
        if event.keysym not in ("Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R", "Meta_L", "Meta_R"):
            if self.key_states.get(event.keysym, False):
                self.key_states[event.keysym] = False
                self.play_sound('press_up')
            
    ############################################################################
    def print_message(self, text, log_level="info"):
        log_text = text.strip()
        
        self.console.config(state="normal")
        self.console.insert(tk.END," " + text + "\n")
        self.console.config(state="disabled")
        self.console.see(tk.END)
        
        if log_text:
            clean_text = log_text.replace(" > error:", "").replace(" >", "").strip()
            
            if log_level.lower() == "debug":
                self.logger.debug(clean_text)
            elif log_level.lower() == "info":
                self.logger.info(clean_text)
            elif log_level.lower() == "warning":
                self.logger.warning(clean_text)
            elif log_level.lower() == "error":
                self.logger.error(clean_text)
            elif log_level.lower() == "critical":
                self.logger.critical(clean_text)
            else:
                self.logger.info(clean_text)
    ############################################################################
    
    def process_input(self, event):
        user_input = self.entry.get().strip()
        
        if not user_input:
            self.entry.delete(0, tk.END)
            return

        if user_input.startswith("/"):
            cmd_with_args = user_input[1:].split()
            if not cmd_with_args:
                self.print_message(" > error: command expected after \"/\"", "error")
                self.play_sound('error')
                self.entry.delete(0, tk.END)
                return
                
            if any(char.isupper() for char in str(cmd_with_args)):
                number = 0
                correct_command = cmd_with_args[number].lower()
                number += 1
                self.print_message(f" > error: did you mean \"/{correct_command}\"?", "error")
                self.play_sound('error')
                self.entry.delete(0, tk.END)
                return
                
            cmd = cmd_with_args[0]
            args = cmd_with_args[1:]
            
            if cmd in self.commands:
                self.print_message(f"executing command: /{cmd} {args}", "debug")
                self.commands[cmd]["func"](*args)
            else:
                self.print_message(f" > unknown command: \"/{cmd}\". type \"/help\" for help", "error")
                self.play_sound('error')
        else:
            self.print_message(f"> {user_input}", "info")
        
        self.entry.delete(0, tk.END)
        
    def load_sounds(self):
        self.sounds = {
            'press_down': None,
            'press_up': None,
            'error': None,
            'enable': None,
            'disable': None,
            'welcome': None,
            'done': None,
            'cleared': None,
            'shutdown': None,
            'notification': None,
        }
        
        sound_files = {
            'press_down': "sounds/keys/press_down.wav",
            'press_up': "sounds/keys/press_up.wav",
            'error': "sounds/error.wav",
            'enable': "sounds/enable.wav",
            'disable': "sounds/disable.wav",
            'welcome': "sounds/welcome.wav",
            'done': "sounds/done.wav",
            'cleared': "sounds/cleared.wav",
            'shutdown': "sounds/shutdown.wav",
            'notification': "sounds/notification.wav",
        }
        
        for sound_name, file_path in sound_files.items():
            try:
                if os.path.exists(file_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                    self.logger.info(f"sound loaded: {sound_name}", "debug")
                else:
                    self.print_message(f"sound file not found: {file_path}", "warning")
                self.logger.info(f"loaded {len(self.sounds)} sounds", "info")
            except Exception as e:
                self.print_message(f" > error loading sound {file_path}: {e}", "error")
                self.play_sound('error')
                
    def load_tracks(self):
        self.playlist = []
        if not os.path.exists(self.music_folder):
            self.print_message(f" > error: {self.music_folder} is missing", "error")
            self.play_sound('error')
        else:
            try:
                for filename in os.listdir(self.music_folder):
                    if filename.lower().endswith(self.supported_formats):
                        filepath = os.path.join(self.music_folder, filename)
                        self.playlist.append(filepath)
                        self.logger.info(f"track added: {filename}", "debug")
                if not self.playlist:
                    self.print_message(f" > error: no tracks found in '{self.music_folder}' folder", "warning")
                    self.play_sound('error')
                else:
                    self.logger.info(f"loaded {len(self.playlist)} tracks", "info")
                    
            except Exception as e:
                self.print_message(f" > error loading tracks: {str(e)}", "error")
                self.play_sound('error')
                
    def check_events(self):
        for event in pygame.event.get():
            if event.type == self.TRACK_END and self.toggle and self.is_playing:
                if not pygame.mixer.music.get_busy():
                    if self.repeat:
                        self.play_current_track()
                    else:
                        self.play_next_track()
        self.root.after(100, self.check_events)
    
    def play_next_track(self):
        if not self.playlist or not self.toggle:
            return  
        self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
        self.play_current_track()
        
    #########################################################################################
    #########################################################################################
    
    def play_current_track(self):
        if not self.playlist or not self.toggle:
            return
        
        try:
            self.pause = False
            file_path = self.playlist[self.current_track_index]
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self.is_playing = True
            
    #########################################################################################
            sound = pygame.mixer.Sound(file_path)
            self.track_length = sound.get_length()
            self.start_time = time.time()
            
            track_name = os.path.basename(file_path)
            if self.repeat:
                self.print_message(f"now playing: {track_name} - on repeat", "info")
            else:
                self.print_message(f"now playing: {track_name}", "info")
            
            self.play_sound('notification')
        except Exception as e:
            self.print_message(f" > error: {str(e)}", "error")
            self.play_sound('error')
            
    #########################################################################################
    #########################################################################################

    def set_volume(self, volume=0.5):
        self.volume = max(0.0, min(1.0, float(volume)))
        pygame.mixer.music.set_volume(self.volume)
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)
                
    def play_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].play()

    def cmd_help(self, *args):
        self.print_message("available commands:", "info")
        self.play_sound('done')
        for cmd, data in self.commands.items():
            self.print_message(f" > /{cmd.ljust(2)} — {data['desc']}", "info")
    
    def cmd_clear(self, *args):
        self.console.config(state="normal")
        self.console.delete(1.0, tk.END)
        self.console.config(state="disabled")
        self.play_sound('cleared')
    
    def cmd_echo(self, *args):
        if args:
            self.print_message(" ".join(args), "info")
        else:
            self.print_message("error: text after command is required", "error")
            self.print_message("usage: /echo <text>", "info")
            self.play_sound('error')
        
    def cmd_mediaplayer(self, *args):
        if self.toggle == False:
            self.toggle = True
            self.create_progress_bar()
            self.print_message("media player launched", "info")
            self.play_sound('done')
        else:
            self.print_message(" (!) media player is already running", "warning")
            self.play_sound("notification")
        
    def cmd_close_mediaplayer(self, *args):
        if self.toggle:
            if self.is_playing:
                self.cmd_stop_track()
            else:
                pygame.mixer.music.stop()
                self.current_track_index = 0
            
            self.toggle = False
            self.destroy_progress_bar()
            self.print_message("media player is closed", "info")
        else:
            self.print_message(" (!) media player is already closed", "warning")
            self.play_sound("notification")

    def cmd_playlist(self, *args):
        if self.toggle:
            if not self.playlist:
                self.print_message(" (!) playlist is empty", "warning")
                self.play_sound('notification')
                return
            else:
                self.play_sound('done')
                self.print_message("playlist: ", "info")
                for i, track in enumerate(self.playlist):
                    prefix = ">" if i == self.current_track_index else " "
                    self.print_message(f" {prefix} {i+1}. {os.path.basename(track)}", "info")
                                
        else:
            self.print_message(" > error: media player not running", "error")
            self.play_sound('error')
            
    def cmd_play_tracks(self, *args):
        if self.toggle:
            if not self.playlist:
                self.print_message(" (!) playlist is empty", "warning")
                self.play_sound('notification')
                return

            if args:
                try:
                    track_num = int(args[0]) - 1
                    if 0 <= track_num < len(self.playlist):
                        self.current_track_index = track_num
                        self.play_current_track()
                    else:
                        self.print_message(f" > error: track number must be between 1 and {len(self.playlist)}", "error")
                        self.play_sound('error')
                except ValueError:
                    found = False
                    search_term = " ".join(args).lower()
                    for i, track in enumerate(self.playlist):
                        if search_term in os.path.basename(track).lower():
                            self.current_track_index = i
                            self.play_current_track()
                            found = True
                            break
                    if not found:
                        self.print_message(f" > error: track '{' '.join(args)}' not found", "error")
                        self.play_sound('error')
            else:
                self.play_current_track()
        else:
            self.print_message(" > error: media player not running", "error")
            self.play_sound('error')
    
    def cmd_stop_track(self, *args):
        if self.toggle:
            pygame.mixer.music.stop()
            self.current_track_index = 0
            self.is_playing = False
            self.print_message("track stopped", "info")
            self.play_sound('done')
            ###########################################################
            if self.progress_canvas:
                self.progress_canvas.coords(self.progress_bar, 0, 0, 0, 10)
                self.progress_label.config(text="00:00 / 00:00")
        else:
            self.print_message(" > error: media player not running", "error")
            self.play_sound('error')
            
    def cmd_pause(self, *args):
        if self.toggle:
            if self.pause == False:
                self.pause = True
                pygame.mixer.music.pause()
                self.is_playing = False
                self.print_message("track paused", "info")
                self.play_sound('done')
            elif self.pause:
                self.print_message(" (!) the current track is already paused", "warning")
                self.play_sound('notification')
            else:
                self.print_message(" (!) the track is not playing", "warning")
                self.play_sound('notification')
        else:
            self.print_message(" > error: media player not running", "error")
            self.play_sound('error')
            
    def cmd_unpause(self, *args):
        if self.toggle:
            if self.pause:
                self.pause = False
                pygame.mixer.music.unpause()
                self.update_progress()
                self.is_playing = True
                self.print_message("track unpaused", "info")
                self.play_sound('done')
            elif self.pause == False:
                self.print_message(" (!) the current track is not paused", "warning")
                self.play_sound('notification')
            else:
                self.print_message(" > error: the track is not playing", "error")
                self.play_sound('error')
        else:
            self.print_message(" > error: media player not running", "error")
            self.play_sound('error')

    def cmd_next_track(self, *args):
        if self.toggle:
            self.current_track_index = (self.current_track_index + 1) % len(self.playlist)
            self.play_current_track()
            if self.pause:
                self.pause = False
        else:
            self.print_message(" > error: media player not running", "error")
            self.play_sound('error')
            
    def cmd_previous_track(self, *args):
        if self.toggle:
            self.current_track_index = (self.current_track_index - 1) % len(self.playlist)
            self.play_current_track()
            if self.pause:
                self.pause = False
        else:
            self.print_message(" > error: media player not running", "error")
            self.play_sound('error')
            
    def cmd_repeat_track(self, *args):
        if self.toggle:
            self.repeat = not self.repeat
            status = "enabled" if self.repeat else "disabled"
            self.print_message(f"repeat {status}", "info")
            self.play_sound('done')
        else:
            self.print_message(" > error: media player not running", "error")
            self.play_sound('error')
            
    def cmd_reload_tracks(self, *args):
        self.print_message("reloading tracks from folder...", "info")
        self.root.after(3000, self.load_tracks)
        self.print_message(f"reloaded {len(self.playlist)} tracks from \"{self.music_folder}\" folder", "info")
        if self.toggle and self.playlist:
            self.current_track_index = 0
        self.play_sound('done')
     
    def cmd_exit(self, *args):
        self.print_message("system shutdown initiated", "info")
        self.play_sound('shutdown')
        self.enable = False
        
        self.shutdown_label = tk.Label(
            self.console,
            text="system shutdown initiated",
            font=("Courier New", 12),
            bg="#000000",
            fg="#00FF00"
        )
        self.console.window_create("end", window=self.shutdown_label)
        self.console.insert("end", "\n")
        self.console.see("end")

        def loading(dots_count=0):
            if dots_count < 4:
                dots = "." * dots_count
                self.shutdown_label.config(text=f"system shutdown initiated{dots}")
                self.root.after(300, loading, dots_count + 1)
            loading()
        self.root.after(150, loading)
        self.current_track_index = 0
        if self.keysounds:
            self.keysounds = False
        if self.toggle or self.is_playing:
            pygame.mixer.music.stop()
            self.toggle = False
            self.is_playing = False
        
        self.root.after(5000, self.cleanup_exit)
        
    def cleanup_exit(self):
        self.logger.info("="*50)
        self.logger.info("SESSION COMLETED")
        self.logger.info("="*50)
        self.root.destroy()
        
    def cmd_forced_exit(self, *args):
        self.root.destroy()
        os._exit(0)
        
    def cmd_enable_key_sounds(self, *args):
        self.keysounds = True
        self.play_sound('enable')
        self.print_message("key sounds enabled", "info")
        self.key_sounds()
   
    def cmd_disable_key_sounds(self, *args):
        self.keysounds = False
        self.play_sound('disable')
        self.print_message("key sounds disabled", "info")
        self.key_sounds()
        
    def cmd_set_volume(self, *args):
        if args:
            try:
                volume = round(float(args[0]) / 100, 2)
                if 0 <= volume <= 1:
                    self.play_sound('enable')
                    self.set_volume(volume)
                    self.print_message(f"volume: {int(volume * 100)}%", "info")
                else:
                    self.print_message(" > error: volume must be between 0 and 100", "error")
                    self.play_sound('error')
            except ValueError:
                self.print_message(" > error: volume must be a number between 0 and 100", "error")
                self.play_sound('error')
        else:
            self.print_message(" > error: a value must be set", "error")
            self.print_message("   > usage: /setvolume <level>", "info")
            self.play_sound('error')
        
if __name__ == "__main__":
    if not os.path.exists('logs'):
        os.makedirs('logs')
    root = tk.Tk()
    app = Console(root)
    root.mainloop()