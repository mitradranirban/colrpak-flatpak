import json
import os
import hashlib
import glob
import subprocess
import sys

def get_wheel_info(name):
    """Downloads and extracts metadata for universal wheels."""
    print(f"Fetching universal wheel for {name}...")
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

def modify(target_json):
    if not os.path.exists(target_json):
        print(f"Error: {target_json} not found.")
        sys.exit(1)

    with open(target_json, "r") as f:
        original_data = json.load(f)

    # 1. Start with a fresh module list
    flat_modules = []

    # 2. Add build hooks first (setuptools and wheel)
    for tool in ["setuptools", "wheel"]:
        name, fname, url, sha = get_wheel_info(tool)
        flat_modules.append({
            "name": f"python3-{name}",
            "buildsystem": "simple",
            "build-commands": [
                f"pip3 install --verbose --exists-action=i --no-index --find-links=\".\" --prefix=/app {fname}"
            ],
            "sources": [{"type": "file", "url": url, "sha256": sha}]
        })

    # 3. Add the original generator output (like pkgconfig)
    # If the generator put pkgconfig as the top-level name, we move its data to the list
    if "sources" in original_data:
        # Move the top-level module into our list
        flat_modules.append({
            "name": original_data.get("name", "python3-pkgconfig"),
            "buildsystem": original_data.get("buildsystem", "simple"),
            "build-commands": original_data.get("build-commands", []),
            "sources": original_data.get("sources", [])
        })
    
    # Also grab any modules the generator actually managed to include
    if "modules" in original_data:
        flat_modules.extend(original_data["modules"])

    # 4. Final Clean Output Structure
    new_data = {
        "name": "build-tools",
        "buildsystem": "simple",
        "build-commands": [],
        "modules": flat_modules
    }
    
    with open(target_json, "w") as f:
        json.dump(new_data, f, indent=4)
    print(f"Successfully modified {target_json} with a flattened module structure.")

if __name__ == "__main__":
    # We target build-tools.json which was created by the generator
    modify("build-tools.json")