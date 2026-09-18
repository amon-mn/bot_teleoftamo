from __future__ import annotations

from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def build_driver(headless: bool, download_dir: Path) -> webdriver.Chrome:
    download_dir.mkdir(parents=True, exist_ok=True)

    options = Options()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(download_dir.resolve()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    if headless:
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": str(download_dir.resolve())},
        )

    return driver
