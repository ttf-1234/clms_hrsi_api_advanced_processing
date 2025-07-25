import os

# List of scripts to run in order (relative to this main.py)
scripts = [
    "scripts/01_download_orig_repos.py",
    "scripts/02_determine_tile.py",
    "scripts/03_download_data.py",
    "scripts/04_unzip_downloads.py",
    "scripts/05_mosaic.py",
    "scripts/06_reclassify.py",
    "scripts/07_resample.py",
    "scripts/08_filter_cloud_coverage.py"
]

for script in scripts:
    print(f"\n--- Running {script} ---")
    exit_code = os.system(f"python {script}")
    if exit_code != 0:
        print(f"Script {script} failed with exit code {exit_code}. Stopping pipeline.")
        break