import json
import os
import hashlib
import glob

def get_source_entry(whl_path):
    with open(whl_path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    
    filename = os.path.basename(whl_path)
    # Split filename to get the package name for the URL structure
    pkg_name = filename.split('-')[0]
    
    return {
        "type": "file",
        "url": f"https://files.pythonhosted.org/packages/py3/{pkg_name[0]}/{pkg_name}/{filename}",
        "sha256": sha
    }

def inject():
    target = "runtime-deps.json"
    if not os.path.exists(target):
        return

    with open(target, "r") as f:
        data = json.load(f)

    # Find all downloaded wheels (pkgconfig, setuptools, etc.)
    whl_files = glob.glob("*.whl")
    vendor_sources = [get_source_entry(f) for f in whl_files]

    if not vendor_sources:
        print("No wheels found to vendor.")
        return

    for module in data.get("modules", []):
        # 1. Strip the --no-build-isolation flag if it exists
        if "build-commands" in module:
            module["build-commands"] = [
                cmd.replace(" --no-build-isolation", "") for cmd in module["build-commands"]
            ]

        # 2. Inject all vendor tools into aiohttp
        if module["name"] == "python3-aiohttp":
            module["sources"].extend(vendor_sources)
            print(f"Vendored {len(vendor_sources)} tools into aiohttp.")

    with open(target, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    inject()