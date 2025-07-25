"""
Summary:
--------
This script downloads the official CLMS HRSI API client script (clms_hrsi_downloader.py) from the European Environment Agency's GitHub repository:
https://github.com/eea/clms-hrsi-api-client-python

It saves the downloaded script locally as 'CLMS_downloader.py' and verifies that the download was successful by checking the file size.

Code with comments:
-------------------
"""

# Import required packages
import requests  # For making HTTP requests to download files
import os        # For file and path operations

# URL of the original CLMS HRSI API client script on GitHub
url = "https://raw.githubusercontent.com/eea/clms-hrsi-api-client-python/refs/heads/main/clms_hrsi_downloader.py"

# Local path where the script will be saved
local_path = "./CLMS_downloader.py"

# Download the file from GitHub
response = requests.get(url)

# Write the downloaded content to the local file
with open(local_path, "wb") as f:
    f.write(response.content)

# Check if the file exists and is not empty to confirm successful download
if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
    print("CLMS_downloader.py was successfully downloaded and verified.")
else:
    print("Download failed or file is empty!")

# Source repository: https://github.com/eea/clms-hrsi-api-client-python



