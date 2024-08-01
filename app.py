import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.scrolledtext as scrolledtext
import json
import winreg as reg
import os
import sys
from dpi import DPIjob
from PIL import Image
from pystray._base import MenuItem as item
import pystray._win32




def add_to_startup():
    try:
        pth = sys.executable
        name = "WinDPI"

        key = reg.HKEY_CURRENT_USER
        key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'
        
        open_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(open_key, name, 0, reg.REG_SZ, pth)
        reg.CloseKey(open_key)
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add to startup: {e}")

def remove_from_startup():
    try:
        name = "WinDPI"

        key = reg.HKEY_CURRENT_USER
        key_value = r'Software\Microsoft\Windows\CurrentVersion\Run'

        open_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        reg.DeleteValue(open_key, name)
        reg.CloseKey(open_key)

    except FileNotFoundError:
        messagebox.showinfo("Information", "Application not found in startup")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to remove from startup: {e}")

# Create the main application window
class Application(tk.Tk):
    def __init__(self, dpi):
        super().__init__()

        self.dpi = dpi

        # Configure the main window
        self.title("WinDPI")
        self.geometry("500x600")
        self.resizable(False, False)
        self.iconbitmap(sys.executable)

        # Define main button frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(pady=20)

        # Start/Stop button
        if self.dpi.is_running:
            self.state_button = ttk.Button(self.main_frame, text="Stop", command=self.toggle_state)
        else:
            self.state_button = ttk.Button(self.main_frame, text="Start", command=self.toggle_state)
        self.state_button.pack(pady=10, ipadx=50, ipady=20)

        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)

        # Add a settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")

        self.create_settings_widgets()

        # Load existing config or create a new one
        self.config_path = "config.json"
        self.load_config()

    def create_settings_widgets(self):
        # Launch on startup checkbox
        self.launch_on_startup_var = tk.BooleanVar()
        self.launch_on_startup_checkbox = ttk.Checkbutton(self.settings_tab, text="Launch on Startup", variable=self.launch_on_startup_var, command=self.launch_on_startup_func)
        self.launch_on_startup_checkbox.pack(anchor='w', pady=15, padx=10)

        # Folder Picker
        self.folder_frame = tk.Frame(self.settings_tab)
        self.folder_frame.pack(anchor='w', pady=5, padx=10, fill=tk.X)
        self.folder_label = ttk.Label(self.folder_frame, text="Folder Location:")
        self.folder_label.pack(side=tk.LEFT, padx=5)
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_path, width=40)
        self.folder_entry.pack(side=tk.LEFT, padx=5)
        self.folder_button = ttk.Button(self.folder_frame, text="Choose..", command=self.select_folder)
        self.folder_button.pack(side=tk.LEFT, padx=5)

        # File Edit Section
        self.blacklist_frame = ttk.LabelFrame(self.settings_tab, text="Edit Blacklist")
        self.blacklist_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.blacklist_text = scrolledtext.ScrolledText(self.blacklist_frame, height=7)
        self.blacklist_text.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        self.save_blacklist_button = ttk.Button(self.settings_tab, text="Save Blacklist", command=self.save_blacklist)
        self.save_blacklist_button.pack(anchor='w', pady=5, padx=10)

        # Config Field Edit
        self.field_label = ttk.Label(self.settings_tab, text="Edit arguments (GoodbyeDPI):")
        self.field_label.pack(anchor='w', pady=15, padx=10)
        self.field_value = tk.StringVar()
        self.field_entry = ttk.Entry(self.settings_tab, textvariable=self.field_value, width=50)
        self.field_entry.pack(anchor='w', pady=5, padx=10)

        self.save_config_field_button = ttk.Button(self.settings_tab, text="Save args", command=self.save_config_field)
        self.save_config_field_button.pack(anchor='w', pady=5, padx=10)

        self.load_blacklist()

    def toggle_state(self):
        if not self.dpi.is_running:
            self.dpi.run_cmd_script(config_path=self.config_path)
            self.state_button.config(text="Stop")
        else:
            self.dpi.stop_cmd_script()
            print("stopped")
            self.state_button.config(text="Start")

    def launch_on_startup_func(self):
        if self.launch_on_startup_var.get():
            add_to_startup()
            self.save_config()
        else:
            remove_from_startup()
            self.save_config()

    def select_folder(self):
        if self.dpi.is_running:
            messagebox.showerror("Error", "Cannot save config while script is running")
            return
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.save_config()

    def save_config(self):
        if self.dpi.is_running:
            messagebox.showerror("Error", "Cannot save config while script is running")
            return
        config_data = {
            "folder_path": self.folder_path.get(),
            "arguments": self.field_value.get(),
            "launch_on_startup": self.launch_on_startup_var.get()
        }
        with open(self.config_path, 'w') as config_file:
            json.dump(config_data, config_file, indent=4)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as config_file:
                config_data = json.load(config_file)
                self.folder_path.set(config_data.get("folder_path", ""))
                self.field_value.set(config_data.get("arguments", ""))
                self.launch_on_startup_var.set(config_data.get("launch_on_startup", False))

    def load_blacklist(self):
        if os.path.exists("blacklist.txt"):
            with open("blacklist.txt", 'r') as file:
                self.blacklist_text.insert(tk.END, file.read())

    def save_blacklist(self):
        if self.dpi.is_running:
            messagebox.showerror("Error", "Cannot save config while script is running")
            return
        try:
            with open("blacklist.txt", 'w') as file:
                file.write(self.blacklist_text.get("1.0", tk.END))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save blacklist: {e}")

    def save_config_field(self):
        self.save_config()


def on_exit(icon, dpi):
    dpi.stop_cmd_script()  # Clean up any running process
    icon.stop()
    os._exit(0)

def open_ui(dpi):
    # Create an instance of Tk
    app = Application(dpi)
    app.mainloop()

def create_icon(icon_path):
    icon = Image.open(icon_path)
    return icon

# Main execution
if __name__ == "__main__":
    dpi = DPIjob()
    dpi.run_cmd_script(config_path="config.json")

    # Load the tray icon from a file
    icon_path = "icon.ico"
    icon_image = create_icon(icon_path)

    # Create a system tray icon
    icon = pystray.Icon("cmd_script_runner", icon_image)
    icon.menu = pystray.Menu(
        item('Open', lambda: open_ui(dpi)),
        item('Exit', lambda: on_exit(icon, dpi))
    )

    # Start the icon
    icon.run()