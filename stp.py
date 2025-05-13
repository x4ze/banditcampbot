import subprocess
import sys
import os


# ---------- Step 1: Install Required Packages ----------
required_packages = [
    "seleniumbase",
    "requests",
    "pywin32",
]

# Flag to detect if we’ve already restarted and avoid infinite loop
RESTART_FLAG = "--postinstall"

def install_packages():
    for package in required_packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
def restart_script():
    print("🔁 Restarting setup to complete installation...")
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)
    os.execv(python_exe, [python_exe, script_path, RESTART_FLAG])

# ---------- Step 2: Create Desktop Shortcut ----------
def create_shortcut():
    print("Creating Desktop shortcut...")
    from win32com.client import Dispatch
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
    script_dir = os.path.abspath(os.path.dirname(__file__))
    main_py = os.path.join(script_dir, "main.py")
    
    shortcut_path = os.path.join(desktop, "x4ze's bandit.camp bot.lnk")
    
    # Use Windows cmd to run Python script
    target = r"C:\Windows\System32\cmd.exe"
    arguments = f'/c python "{main_py}"'

    # Optional icon - update this path if you have an icon file
    icon_path = os.path.join(script_dir, "icon.ico")  # Optional
    if not os.path.exists(icon_path):
        icon_path = None  # Fallback to default

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = target
    shortcut.Arguments = arguments
    shortcut.WorkingDirectory = script_dir
    if icon_path:
        shortcut.IconLocation = icon_path
    shortcut.save()
    print("Created 'bandit.camp bot' shortcut on Desktop!")


def create_users_json():
    users_json_path = os.path.join(os.path.dirname(__file__), "users.json")
    if not os.path.exists(users_json_path):
        with open(users_json_path, "w") as f:
            f.write("""[
    {
        "name": "your_name",
        "token": "your_jwt_token",
        "cashout_limit": 3
    }
]""")
        print("Created 'users.json' file.")
    else:
        print("'users.json' file already exists. Skipping creation.")

# ---------- Step 3: Run Setup ----------
if __name__ == "__main__":
    print("Running setup...")
    if RESTART_FLAG not in sys.argv:
        install_packages()
        restart_script()
    create_shortcut()
    print("Creating users.json file...")
    create_users_json()
    print("Setup complete! You can now run the bot from your Desktop.")
