import json
from re import sub
from typing import Optional

import requests
from scrapy.selector import Selector

start_urls = [
    (f"https://diemthi.vnexpress.net/diem-chuan/id/{id}", id) for id in range(5, 504)]
api_endpoint = "https://diemthi.vnexpress.net/diem-chuan/loadData"


admissions = []


def get_response(url: str, method: Optional[str] = "GET", payload: Optional[dict] = {}) -> str:
    if method == "POST":
        return requests.post(url=url, data=payload).json().get("html")
    return requests.get(url=url).text


def make_payload(year: int, idcollege: int) -> dict:
    return {
        "year": str(year),
        "idcollege": str(idcollege),
        "bmk": "abc",
        "sid": ""
    }


def extract(html: str, query: str) -> str:
    return Selector(text=html).xpath(query).get()


def scraping(url: str, id: int, start_year: Optional[int] = 2015, end_year: Optional[int] = 2020) -> None:
    university_name = sub(r"\s*?-\s*?\d{4}.*", "", extract(html=get_response(
        url), query="//h4[@class=\"diemchuan-truong__title\"]/a/text()"))
    for year in range(start_year, end_year + 1):
        response = get_response(api_endpoint, "POST", make_payload(year, id))
        majors = Selector(text=response).xpath("//tbody/tr[1]")
        if (not len(majors) == 0):
            for major in majors:
                admissions.append({
                    "tenTruongDH": university_name,
                    "namXetTuyen": year,
                    "tenNganh": extract(major.get(), "//td[2]/a/text()"),
                    "maNganh": extract(major.get(), "//td[3]/text()"),
                    "khoiXetTuyen": ";".join(Selector(text=major.get()).xpath("//td[4]//a/text()").getall()),
                    "diemChuan": float(extract(major.get(), "//td[5]/text()")),
                    "ghiChu": extract(major.get(), "//td[7]/text()")
                })
        else:
            admissions.append({
                "tenTruongDH": university_name,
                "namXetTuyen": year,
                "tenNganh": None,
                "maNganh": None,
                "khoiXetTuyen": None,
                "diemChuan": None,
                "ghiChu": None
            })


if __name__ == "__main__":
    for url in start_urls:
        scraping(url=url[0], id=url[1])

    with open("data.json", "w", encoding="UTF-8") as f:
        json.dump(admissions, f, ensure_ascii=False)
        f.close()
