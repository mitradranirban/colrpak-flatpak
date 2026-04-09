import json
import os
import hashlib
import glob
import subprocess
import sys

def get_wheel_info(name):
    """Downloads and extracts metadata for universal wheels."""
    # Force download of universal wheels (py3-none-any)
    subprocess.check_call([
        sys.executable, "-m", "pip", "download", 
        "--dest", ".", "--only-binary=:all:", name
    ])
    
    files = glob.glob(f"{name}-*.whl")
    if not files:
        raise Exception(f"Failed to download {name}")
    
    wheel_file = files[0]
    with open(wheel_file, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    
    filename = os.path.basename(wheel_file)
    # Generic PyPI path for Flatpak sources
    url = f"https://files.pythonhosted.org/packages/py3/{name[0]}/{name}/{filename}"
    return name, filename, url, sha

def inject(target_json):
    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found.")
        sys.exit(1)

    with open(target_json, "r") as f:
        data = json.load(f)

    new_modules = []
    # We must inject these because the generator strips them
    for tool in ["setuptools", "wheel"]:
        name, fname, url, sha = get_wheel_info(tool)
        new_modules.append({
            "name": f"python3-{name}",
            "buildsystem": "simple",
            "build-commands": [
                f"pip3 install --verbose --exists-action=i --no-index --find-links=\".\" --prefix=/app {fname}"
            ],
            "sources": [{"type": "file", "url": url, "sha256": sha}]
        })

    # Prepend to ensure they are installed before any other modules
    data["modules"] = new_modules + data.get("modules", [])
    
    with open(target_json, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Successfully injected build tools into {target_json}")

if __name__ == "__main__":
    inject("build-tools.json")  