import os
import subprocess
import sys

def main():
    try:
        src_dir = os.path.join(os.path.dirname(__file__), 'src')
        os.chdir(src_dir)
        subprocess.run([sys.executable, "-m", "streamlit", "run", "steganography.py"], check=True)
    except Exception as e:
        print(f"Error launching application: {e}")

if __name__ == "__main__":
    main()