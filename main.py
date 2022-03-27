import json
import sys
import re
from functools import partial

from bs4 import BeautifulSoup
from tq_scroll_scrape.scroll_and_scrape import ScrollAndScrape

ROOT_URL = "https://teamcolorcodes.com/ncaa-color-codes/"


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


def save_root_html_file(source: str):
    with open("root.html", "w") as file:
        file.write(source)
    print("File saved to root.html.")


def main(argv):
    if argv[0] == "--process-root":
        scroll_scraper = ScrollAndScrape()
        scroll_scraper.download(ROOT_URL, save_root_html_file, sleep_after_scroll_seconds=1, scroll_by=500)
        scroll_scraper.driver.close()
        scroll_scraper.driver.quit()
    elif argv[0] == "--process-schools":
        process_schools()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
