from bs4 import BeautifulSoup


def get_info_vacancy(html_text: str):
    res = BeautifulSoup(html_text)
    print(res)
