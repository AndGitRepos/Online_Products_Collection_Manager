import os, sys
import subprocess
import pkg_resources
from pathlib import Path

"""
Checks if any dependencies are missing and installs them
"""
def install_dependencies(requirements_file='requirements.txt'):
    required = set()
    with open(requirements_file, 'r') as f:
        for line in f:
            package = line.strip()
            if package and not package.startswith('#'):
                required.add(package)

    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

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