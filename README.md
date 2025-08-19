# Modrinth-downloader

Automatic downloader collection projects from [Modrinth](https://modrinth.com).

## Features

### Downloading collection projects

The program can download collection projects for specific minecraft version and loaders, with all required project dependencies.

> Projects will be downloaded to directory `download` in this repo, \
> with this file schema: `[<game_version>] <project_slug> <version_number>.<version_suffix>`

### Collision detector

The program automatically find version collisions and allow user to resolve each conflict.

### Preference the stable version

With argument `--releases` the program selects the stable version of the project if it is available or if any other project does not require an experimental version.

### Only client projects

Project allow to filter only client projects.
> Projects without specific client side will be included.

### Only server projects

Project allow to filter only server projects.
> Projects without specific server side will be included.

## Requirements

- [poetry](https://python-poetry.org/) = 1.8.5
- Collection visibility set to `Unlisted` or `Public`

## Usage

1. Download this repo
2. Install python dependencies by poetry
   ```bash
   poetry install
   ```
3. Run `app` module
   ```bash
   python -m app -h
   ```
4. Follow by program
