# Colr Pak Flatpak

This repository contains the Flatpak manifest and metadata to build **[Colr Pak](https://mitradranirban.github.io/colr-pak)**, a standalone desktop font editor for authoring COLRv0 and COLRv1 color fonts.

## Repository Structure

* `in.atipra.ColrPak.yml`: The main Flatpak manifest.
* `in.atipra.ColrPak.desktop`: The desktop entry file.
* `in.atipra.ColrPak.metainfo.xml`: AppStream metadata file for app stores.
* `pypi-dependencies.json`: Generated Python dependencies using `flatpak-pip-generator`.
* `.github/workflows/`: Automation scripts to keep Git hashes up to date.

## Prerequisites

To build this Flatpak locally, you will need `flatpak` and `flatpak-builder` installed on your system. 

You also need to install the required runtimes, SDKs, and BaseApps from Flathub:

```bash
# Add the Flathub repository if you haven't already
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

# Install the Freedesktop runtime and SDK
flatpak install flathub org.freedesktop.Platform//25.08 org.freedesktop.Sdk//25.08

# Install the Node.js extension required by Fontra
flatpak install flathub org.freedesktop.Sdk.Extension.node22//25.08

# Install the PyQt BaseApp
flatpak install flathub com.riverbankcomputing.PyQt.BaseApp//6.9
```

## Building Locally

To build and install the application for your current user:

```bash
flatpak-builder --user --install --force-clean build-dir in.atipra.ColrPak.yml
```

*Note: The `build-dir` is a temporary directory created during the build process. The `--force-clean` flag ensures a fresh build.*

## Running the App

Once installed, you can launch Colr Pak from your desktop application menu, or run it via the terminal:

```bash
flatpak run in.atipra.ColrPak
```

## Updating Python Dependencies

If the `requirements.txt` of Colr Pak changes, you need to update the `pypi-dependencies.json` file. This repository uses the PyQt BaseApp, so Qt-related packages should be omitted from the generator.

Use the `flatpak-pip-generator` tool:
```bash
python3 flatpak-pip-generator.py --requirements-file requirements-pypi.txt --output pypi-dependencies
```

## Automated Updates

This repository is configured with GitHub Actions to automatically update the commit hashes of all Git sources (including Fontra dependencies) whenever a new release tag is published to the main [colr-pak](https://github.com/mitradranirban/colr-pak) repository via a `repository_dispatch` event.

## License

* Colr Pak inherits the GPL-3.0 license.
* The Flatpak packaging metadata in this repository is licensed under CC0-1.0.
