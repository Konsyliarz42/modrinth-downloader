# Modrinth-downloader

I am always tired when I return to minecraft and again have to search basic mods like FabricAPI, Sodium, etc. So I created downloader. The program reads modrith collection and downloads all mods with their dependencies.

## Dependencies

In addition to the python packages, an account on [modrinth](https://modrinth.com/) is also **required**. In your account settings you can find "PATs" (Personal Access Tokens). You have to create token with at least two scopes:

- Read collections
- Read projects
- Read versions

> Remember: Your token is not forever.

## Usage

1. Install python dependencies
2. Use command:
   ```bash
   python -m app
   ```
