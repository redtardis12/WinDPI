import subprocess
import json
import os


class DPIjob:
    def __init__(self):
        self.process = None
        self.is_running = False

    def run_cmd_script(self, config_path="config.json"):
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
            script_path = os.path.abspath(os.path.join(config_data.get("folder_path", ""), "goodbyedpi.exe"))
            arguments = config_data.get("arguments", "")

        print(f"Running script: {script_path} {arguments}")
        blacklist_path = "blacklist.txt"

        # Create startup info to hide the window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        command = f'{script_path} {arguments} --blacklist {blacklist_path}'

        # Start the script in a hidden mode
        self.process = subprocess.Popen(command, startupinfo=startupinfo)
        self.is_running = True

    def stop_cmd_script(self):
        if self.process:
            self.process.terminate()  # Terminate the process if it is running
            self.process = None
            self.is_running = False
