import json
import os
import hashlib
import glob

def get_source_entry(file_path):
    with open(file_path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    
    filename = os.path.basename(file_path)
    pkg_name = filename.split('-')[0].replace('_', '-')
    
    # Logic to switch URL structure based on file type
    if filename.endswith(".whl"):
        url = f"https://files.pythonhosted.org/packages/py3/{pkg_name[0]}/{pkg_name}/{filename}"
    else:
        # Standard PyPI source URL structure
        url = f"https://files.pythonhosted.org/packages/source/{pkg_name[0]}/{pkg_name}/{filename}"
    
    return {
        "type": "file",
        "url": url,
        "sha256": sha
    }

def inject():
    target = "runtime-deps.json"
    if not os.path.exists(target):
        return

    with open(target, "r") as f:
        data = json.load(f)

    # Find BOTH wheels and source tarballs
    vendor_files = glob.glob("*.whl") + glob.glob("*.tar.gz")
    # Filter out the main packages that are already in the JSON to avoid duplicates
    vendor_sources = [get_source_entry(f) for f in vendor_files if "aiohttp" not in f and "frozenlist" not in f]

    for module in data.get("modules", []):
        if "build-commands" in module:
            module["build-commands"] = [
                cmd.replace(" --no-build-isolation", "") for cmd in module["build-commands"]
            ]

        if module["name"] == "python3-aiohttp":
            module["sources"].extend(vendor_sources)
            print(f"Vendored {len(vendor_sources)} build tools into aiohttp.")

    with open(target, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    inject()