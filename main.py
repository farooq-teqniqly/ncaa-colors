import json
import sys
import re
import os
from functools import partial
from typing import Dict, Tuple, List

from tqdm import tqdm

from bs4 import BeautifulSoup
from tq_scroll_scrape.scroll_and_scrape import ScrollAndScrape

ROOT_URL = "https://teamcolorcodes.com/ncaa-color-codes/"
OUTPUT_FOLDER = os.path.join(os.getcwd(), "output")


def process_schools() -> List[Tuple[str, List[str]]]:
    all_schools = []
    input_folder = os.path.join(os.getcwd(), "output")
    files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if os.path.basename(f) != "root.html"]

    for file in tqdm(files):
        soup = BeautifulSoup(open(file, encoding="utf-8").read(), "html.parser")
        colorblock_divs = soup.find_all("div", class_="colorblock")
        colors = []

        for div in colorblock_divs:
            color = div.contents[0].text.lower().strip()
            colors.append(color)

        all_schools.append((os.path.basename(file).replace(".html", ""), colors))

    return all_schools


def save_html_file(path: str, source: str):
    with open(path, "w", encoding="utf-8") as file:
        file.write(source)
        tqdm.write(f"File saved - {path}")


def main(argv):
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    driver_path = os.path.join(os.getcwd(), "geckodriver.exe")

    if argv[0] == "--download-root":
        scroll_scraper = ScrollAndScrape(driver_path)
        scroll_scraper.download(ROOT_URL,
                                partial(save_html_file, os.path.join(OUTPUT_FOLDER, "root.html")),
                                sleep_after_scroll_seconds=1, scroll_by=1000)
        scroll_scraper.driver.close()
        scroll_scraper.driver.quit()
    elif argv[0] == "--download-schools":
        with open(os.path.join(OUTPUT_FOLDER, "root.html"), "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        links = [a.get("href") for a in soup.find_all("a")][144:431]
        scroll_scraper = ScrollAndScrape(driver_path)

        for link in tqdm(links):
            output_filename = os.path.join(OUTPUT_FOLDER, f"{link.split('/')[-2]}.html")

            if os.path.exists(output_filename):
                tqdm.write(f"File exists - {output_filename}")
                continue

            scroll_scraper.download(link,
                                    partial(save_html_file, output_filename))
            scroll_scraper.driver.close()

        scroll_scraper.driver.quit()
    elif argv[0] == "--process-schools":
        all_school_colors = process_schools()

        with open(os.path.join(os.getcwd(), "output", "all_schools.json"), "w", encoding="utf-8") as file:
            file.write(json.dumps(all_school_colors))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
