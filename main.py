import json
import sys
import re
import os
from functools import partial
from tqdm import tqdm

from bs4 import BeautifulSoup
from tq_scroll_scrape.scroll_and_scrape import ScrollAndScrape

ROOT_URL = "https://teamcolorcodes.com/ncaa-color-codes/"
OUTPUT_FOLDER = os.path.join(os.getcwd(), "output")


def process_schools():
    all_schools = {}

    def save_school(url: str, source: str):
        with open(url.split("/")[-2], "w", encoding="utf-8") as school_file:
            school_file.write(source)

    def get_colors(source: str):
        colors_soup = BeautifulSoup(source, "html.parser")

        school_name = colors_soup.select("h4 > strong")[1].text
        colors = []

        colorblock_divs = colors_soup.find_all("div", class_="colorblock")

        for div in colorblock_divs:
            color = None
            hex_code = None

            match = re.search(r"'*(?P<color>\w+)PANTONE", div.text)

            if match:
                color = match.group("color")

            match = re.search(r"Hex COLOR:\s+#(?P<hex_code>\w{6})", div.text)

            if match:
                hex_code = match.group("hex_code")

            colors.append((color, hex_code))

        all_schools[school_name] = colors

    with open("root.html", "r") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

    links = [a.get("href") for a in soup.find_all("a")][82:431]

    for link in links:
        scroll_scraper = ScrollAndScrape()
        scroll_scraper.download(link, partial(save_school, link))
        scroll_scraper.driver.close()
        scroll_scraper.driver.quit()

    with open("all_schools.json", "w") as file:
        file.write(json.dumps(all_schools))


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


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
