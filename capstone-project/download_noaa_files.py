import sys
import requests
from pathlib import Path

BASE_URL = "https://www1.ncdc.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
CSVS_LIST_FILE = "noaa_files_list.txt"
OUT_DIR = Path("raw-data", "noaa_files")


def download_noaa_files() -> None:
    """
    Download the NOAA storm data CSV files listed in noaa_files_list.txt. 
    The downloaded files are compressed as .gz files.
    """
    with open(CSVS_LIST_FILE, "r") as f:
        filenames = f.read().split("\n")

    if not OUT_DIR.is_dir():
        OUT_DIR.mkdir(parents=True)

    for fn in filenames:
        print(f"INFO: Downloading file: {fn}")
        outpath = OUT_DIR / fn
        if outpath.is_file():
            print(f"INFO: File {outpath} already exists!")
            continue

        download_url = BASE_URL + fn
        try:
            rsp = requests.get(download_url)
            rsp.raise_for_status()
            with outpath.open("wb") as outfile:
                outfile.write(rsp.content)
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Failed to download {download_url}: {e}")
            continue

    print(f"INFO: Downloads done: {len(filenames)} files downloaded.")


if __name__ == '__main__':
    download_noaa_files()
    sys.exit(0)
