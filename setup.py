"""
Sana AI — setup.py
One-command install: python setup.py install
Or just: pip install -r requirements.txt
"""
import subprocess
import sys
from pathlib import Path


BANNER = """
╔══════════════════════════════════════════════════╗
║   Sana AI v1.1.0 — Setup                        ║
║   github.com/saisatwi/MyDataWhisperer           ║
╚══════════════════════════════════════════════════╝
"""


def check_python():
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 11):
        print(f"❌  Python 3.11+ required. You have {major}.{minor}.")
        print("   Download from: https://www.python.org/downloads/")
        sys.exit(1)
    print(f"✅  Python {major}.{minor} detected.")


def install_deps():
    req = Path("requirements.txt")
    if not req.exists():
        print("❌  requirements.txt not found. Re-clone the repository.")
        sys.exit(1)
    print("\n[SETUP] Installing dependencies …")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"],
        check=False,
    )
    if result.returncode != 0:
        print("\n⚠  Some packages failed to install.")
        print("   Try running manually: pip install -r requirements.txt")
    else:
        print("\n✅  All dependencies installed.")


def create_venv():
    venv = Path("venv")
    if venv.exists():
        print("✅  Virtual environment already exists.")
        return
    print("\n[SETUP] Creating virtual environment …")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✅  venv created. The launcher (Start Sana Forever.bat) will activate it.")


def main():
    print(BANNER)
    check_python()
    create_venv()
    install_deps()
    print("""
╔══════════════════════════════════════════════════╗
║   Setup complete!                                ║
║                                                  ║
║   To start Sana:                                 ║
║   • Double-click: Start Sana Forever.bat         ║
║   • Or run:  python "Sana Forever.py"            ║
║                                                  ║
║   Press CapsLock to talk. Ctrl+C to exit.        ║
╚══════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()