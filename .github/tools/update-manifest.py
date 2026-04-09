#!/usr/bin/env python3
import os
import sys
import subprocess
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

manifest_file = 'in.atipra.ColrPak.yml'
new_app_tag = os.environ.get('NEW_APP_TAG')


def resolve_tag_and_commit(url, requested_tag):
    candidates = []
    if requested_tag:
        candidates.append(requested_tag)
        if not requested_tag.startswith("v"):
            candidates.append(f"v{requested_tag}")

    seen = set()
    for tag in candidates:
        if tag in seen:
            continue
        seen.add(tag)

        ref = f"refs/tags/{tag}"
        result = subprocess.run(
            ["git", "ls-remote", url, ref, f"{ref}^{{}}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().splitlines()
            resolved_commit = None

            for line in lines:
                if line.endswith("^{}"):
                    resolved_commit = line.split()[0]
                    break

            if not resolved_commit:
                resolved_commit = lines[0].split()[0]

            return tag, resolved_commit

    return None, None


try:
    with open(manifest_file, "r") as f:
        data = yaml.load(f)
except FileNotFoundError:
    print(f"Error: {manifest_file} not found.")
    sys.exit(1)

changed = False

for module in data.get("modules", []):
    if not isinstance(module, dict):
        continue

    for source in module.get("sources", []):
        if not isinstance(source, dict):
            continue
        if source.get("type") != "git":
            continue

        url = source.get("url", "")
        if "colr-pak.git" not in url:
            continue

        if new_app_tag:
            resolved_tag, resolved_commit = resolve_tag_and_commit(url, new_app_tag)
            if not resolved_tag or not resolved_commit:
                print(f"Error: Could not resolve tag '{new_app_tag}' for {url}")
                sys.exit(1)

            if source.get("tag") != resolved_tag:
                print(f"Updating {url} tag to {resolved_tag}")
                source["tag"] = resolved_tag
                changed = True

            if source.get("commit") != resolved_commit:
                print(f"Updating {url} commit from {source.get('commit')} to {resolved_commit}")
                source["commit"] = resolved_commit
                changed = True
        else:
            current_tag = source.get("tag")
            if current_tag:
                resolved_tag, resolved_commit = resolve_tag_and_commit(url, current_tag)
                if not resolved_tag or not resolved_commit:
                    print(f"Error: Could not resolve existing tag '{current_tag}' for {url}")
                    sys.exit(1)

                if source.get("tag") != resolved_tag:
                    print(f"Normalizing {url} tag from {source.get('tag')} to {resolved_tag}")
                    source["tag"] = resolved_tag
                    changed = True

                if source.get("commit") != resolved_commit:
                    print(f"Refreshing {url} commit from {source.get('commit')} to {resolved_commit}")
                    source["commit"] = resolved_commit
                    changed = True

if changed:
    with open(manifest_file, "w") as f:
        yaml.dump(data, f)
    print("Manifest updated successfully.")
else:
    print("All hashes are already up to date.")