import sys
import os
import subprocess
import pkg_resources
from pathlib import Path

# Get the path to the project root directory
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def install_dependencies(requirements_file='main/requirements.txt'):
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

if __name__ == "__main__":
    requirements_file = Path('main/requirements.txt')
    if not requirements_file.exists():
        print("No requirements file found.")
        sys.exit(1)

    install_dependencies(str(requirements_file))

    # Now that dependencies are installed, we can import and run the Dash app
    from dashApp.app import create_app
    app = create_app()
    app.run_server(debug=True)
