from bs4 import BeautifulSoup


def get_info_vacancy(html_text: str):
    soup = BeautifulSoup(html_text)
    all_tags = soup.find_all("div", {"class": "root--ImnXG"})
    info = {}
    for tag in all_tags:
        count = tag.find("div", {"class": "count--BrEqy"}).find(string=True)
        name = tag["title"]
        info[name] = count
    return info
