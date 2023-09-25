import re
from bs4 import BeautifulSoup
import mechanize
import datetime


class Announcements:
    def __init__(self):
        self.browser = mechanize.Browser()

        self.browser.set_handle_robots(False)
        self.browser.set_handle_equiv(True)
        self.browser.set_handle_gzip(True)
        self.browser.set_handle_refresh(False)
        self.browser.set_handle_redirect(True)
        self.browser.set_handle_referer(True)

        self.browser.addheaders = [
            (
                "User-Agent",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
            ),
            ("Accept-Language", "en-GB,en;q=0.9"),
            ("Accept-Encoding", "gzip, deflate, br"),
            (
                "Accept",
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            ),
            ("Connection", "keep-alive"),
        ]

    def open_announcements(self):
        self.browser.open(
            "https://www.handelsregister.de/rp_web/bekanntmachungen.xhtml", timeout=10
        )

    def filter_announcements(self):
        current_date = datetime.datetime.now().date()
        yesterday = current_date - datetime.timedelta(days=1)

        self.browser.select_form(name="formId")
        self.browser["formId:datum_von_input"] = yesterday.strftime("%d.%m.%Y")
        self.browser["formId:datum_bis_input"] = current_date.strftime("%d.%m.%Y")

        self.browser["formId:land_input"] = ["BE"]

        # 2 = Registerbekanntmachung nach dem Umwandlungsgesetz
        self.browser["formId:kategorie_input"] = ["2"]

        response = self.browser.submit()

        html = response.read().decode("utf-8")

        return get_comanies_from_announcements(html)


def get_comanies_from_announcements(html):
    soup = BeautifulSoup(html, "html.parser")

    datalist = soup.find(id="formId:datalistId_list")

    companies = set()

    for row in datalist.find_all("a"):
        row_text = row.find("label").text
        # Regex pattern
        pattern = r"HR[AB][\d+\s+]*([\w\s.,:&()–-]+)– Berlin"

        # Extracting matches
        match = re.search(pattern, row_text)
        if match:
            company_name = match.group(1)
            companies.add(company_name.strip())
        else:
            print("No match", row)

    return companies


if __name__ == "__main__":
    a = Announcements()
    a.open_announcements()
    announced_companies = a.filter_announcements()

    for company in announced_companies:
        print(company)
        # use HandelsregisterAPI to get the company data
