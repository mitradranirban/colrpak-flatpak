import json
import os
import hashlib
import glob

def inject():
    target = "runtime-deps.json"
    if not os.path.exists(target):
        return

    with open(target, "r") as f:
        data = json.load(f)

    # Find the downloaded wheel
    whl_files = glob.glob("pkgconfig-*.whl")
    if not whl_files:
        print("No pkgconfig wheel found to inject.")
        return
    whl_file = whl_files[0]
    
    with open(whl_file, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()

    filename = os.path.basename(whl_file)
    # The standard PyPI URL for the source entry
    pypi_url = f"https://files.pythonhosted.org/packages/py3/p/pkgconfig/{filename}"

    pkgconfig_source = {
        "type": "file",
        "url": pypi_url,
        "sha256": sha
    }

    # Locate aiohttp and add pkgconfig to its sources
    for module in data.get("modules", []):
        if module["name"] == "python3-aiohttp":
            # Append pkgconfig so pip finds it via --find-links
            module["sources"].append(pkgconfig_source)
            print(f"Successfully vendored {filename} into aiohttp sources.")
            break

    with open(target, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    inject()