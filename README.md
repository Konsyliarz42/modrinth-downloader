# Modrinth-downloader

I am always tired when I return to minecraft and again have to search basic mods like FabricAPI, Sodium, etc. So I created downloader. The program reads [.csv](https://en.wikipedia.org/wiki/Comma-separated_values) file and downloads all mods with their dependencies.

## CSV headers

- `id_or_slug` - **Required** - id of the project from modrinth page or slug from url.
- `version_id` - **Optional** - id of specific version from modrinth page. If you want latest version leave this field alone.

## Dependencies

In addition to the python packages, an account on [modrinth](https://modrinth.com/) is also **required**. In your account settings you can find "PATs" (Personal Access Tokens). You have to create token with at least two scopes:

- Read projects
- Read versions

> Remember: Your token is not forever.

## Usage

1. Create `.env` file from template `example.env`
2. Set variables:

   - `PERSONAL_ACCESS_TOKEN` - Your access token from modrinth
   - `DOWNLOAD_PATH` - Your mods will be downloaded here
   - `MOD_LOADER` - Loader of your mods | _fabric is recommended_
   - `GAME_VERSION` - Minecraft version

3. Install python dependencies
4. Prepare `.csv` file with mods
5. Run code:

   ```bash
   python -m app
   ```
