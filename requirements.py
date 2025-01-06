import subprocess
import sys
import os

def install_requirements():
    print("Installing PyExeForge requirements...")
    
    requirements = [
        'PyQt5==5.15.9',
        'pyinstaller==6.1.0'
    ]
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # Install each requirement
        for requirement in requirements:
            print(f"Installing {requirement}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement])
            
        print("\nAll requirements installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    install_requirements()