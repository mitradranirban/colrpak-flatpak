#!/usr/bin/env python3
import os
import sys
import subprocess
from ruamel.yaml import YAML

yaml = YAML()
yaml.preserve_quotes = True

manifest_file = 'in.atipra.ColrPak.yml'
new_app_tag = os.environ.get('NEW_APP_TAG')

def resolve_ref_commit(url, ref_name, is_tag=False):
    """Resolves the latest commit hash for a branch or tag."""
    # Prefix based on whether it's a branch or a tag
    prefix = "refs/tags/" if is_tag else "refs/heads/"
    full_ref = f"{prefix}{ref_name}"
    
    # We also check for the dereferenced tag (commit it points to) using ^{}
    cmd = ["git", "ls-remote", url, full_ref]
    if is_tag:
        cmd.append(f"{full_ref}^{{}}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 and result.stdout.strip():
        lines = result.stdout.strip().splitlines()
        # For tags, prioritize the dereferenced commit hash (the ^{} line)
        if is_tag and len(lines) > 1:
            for line in lines:
                if line.endswith("^{}"):
                    return line.split()[0]
        return lines[0].split()[0]
    return None

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
        if not isinstance(source, dict) or source.get("type") != "git":
            continue

        url = source.get("url", "")
        current_commit = source.get("commit")
        resolved_commit = None

# Logic for Main App (ColrPak)
        if "colr-pak.git" in url:
            tag_to_use = new_app_tag
            if not tag_to_use:
                # Auto-fetch latest tag if no tag provided via dispatch
                result = subprocess.run(
                    ["git", "ls-remote", "--tags", "--sort=-version:refname", url],
                    capture_output=True, text=True
                )
                tag_to_use = next(
                    (line.split("\t")[1].replace("refs/tags/", "").replace("^{}", "")
                     for line in result.stdout.splitlines()
                     if "^{}" in line),
                    None
                )
            if tag_to_use:
                resolved_commit = resolve_ref_commit(url, tag_to_use, is_tag=True)
                if resolved_commit and (source.get("tag") != tag_to_use or resolved_commit != current_commit):
                    source["tag"] = tag_to_use
                    source["commit"] = resolved_commit
                    changed = True
                    print(f"Updating ColrPak to tag {tag_to_use}")
            continue  # skip the generic update block below

        # Logic for all other Git sources (Dependencies)
        else:
            if "tag" in source:
                resolved_commit = resolve_ref_commit(url, source["tag"], is_tag=True)
            elif "branch" in source:
                resolved_commit = resolve_ref_commit(url, source["branch"], is_tag=False)
            else:
                # Default to 'main' or 'master' if no ref is specified
                resolved_commit = resolve_ref_commit(url, "main", is_tag=False)

        # Apply changes if the commit hash has changed
        if resolved_commit and resolved_commit != current_commit:
            print(f"Updating {url}: {current_commit[:7]} -> {resolved_commit[:7]}")
            source["commit"] = resolved_commit
            changed = True

if changed:
    with open(manifest_file, "w") as f:
        yaml.dump(data, f)
    print("Manifest updated successfully.")
else:
    print("All hashes are already up to date.")