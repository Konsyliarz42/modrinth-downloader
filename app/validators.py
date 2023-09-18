from pathlib import Path


def download_folder_validator(download_folder: Path) -> None:
    if not download_folder.exists():
        raise ValueError(f"{download_folder} not exists")
    elif not download_folder.is_dir():
        raise ValueError(f"{download_folder} is not a directory")


def csv_file_validator(csv_file: Path) -> None:
    if not csv_file.exists():
        raise ValueError(f"{csv_file} not exists")
    elif not csv_file.is_file():
        raise ValueError(f"{csv_file} is not a file")
