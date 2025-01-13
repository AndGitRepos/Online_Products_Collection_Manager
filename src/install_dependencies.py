import os
import sys
import subprocess
from pathlib import Path

def install_dependencies(requirements_file='requirements.txt'):
    # Read required packages from requirements.txt
    required = set()
    with open(requirements_file, 'r') as f:
        for line in f:
            package = line.strip()
            if package and not package.startswith('#'):
                required.add(package)

    # Try to import each package to check if it's installed
    missing = set()
    for package in required:
        # Remove version specifiers if present (e.g., "package>=1.0.0" -> "package")
        package_name = package.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0]
        try:
            __import__(package_name)
        except ImportError:
            missing.add(package)

    if missing:
        python = sys.executable
        subprocess.check_call([python, '-m', 'pip', 'install', '-r', requirements_file], stdout=subprocess.DEVNULL)
        print(f"Installed missing dependencies: {', '.join(missing)}")
    else:
        print("All dependencies are already installed.")

""" - MAIN - """
if __name__ == "__main__":
    requirements_file = Path('requirements.txt')
    if requirements_file.exists():
        install_dependencies(str(requirements_file))
    else:
        print(f"Requirements file not found: {requirements_file}")
