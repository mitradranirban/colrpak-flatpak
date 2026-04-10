import json
import os
import hashlib
import glob

def inject():
    target = "runtime-deps.json"
    if not os.path.exists(target):
        print(f"Error: {target} not found.")
        return

    with open(target, "r") as f:
        data = json.load(f)

    # 1. Find the downloaded wheel
    whl_files = glob.glob("pkgconfig-*.whl")
    if not whl_files:
        print("No pkgconfig wheel found to inject.")
        return
    whl_file = whl_files[0]
    
    with open(whl_file, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()

    filename = os.path.basename(whl_file)
    pypi_url = f"https://files.pythonhosted.org/packages/py3/p/pkgconfig/{filename}"

    pkgconfig_source = {
        "type": "file",
        "url": pypi_url,
        "sha256": sha
    }

    # 2. Process modules
    for module in data.get("modules", []):
        # Remove --no-build-isolation from ALL modules to prevent SDK conflicts
        if "build-commands" in module:
            module["build-commands"] = [
                cmd.replace(" --no-build-isolation", "") 
                for cmd in module["build-commands"]
            ]

        # Inject pkgconfig into aiohttp specifically
        if module["name"] == "python3-aiohttp":
            module["sources"].append(pkgconfig_source)
            print(f"Successfully vendored {filename} and enabled isolation for aiohttp.")

    with open(target, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    inject()