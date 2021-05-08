import json
import requests
from re import sub
from typing import Optional
from scrapy.selector import Selector


start_urls = [
    (f"https://diemthi.vnexpress.net/diem-chuan/id/{id}", id) for id in range(5, 504)]
api_endpoint = "https://diemthi.vnexpress.net/diem-chuan/loadData"


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


def scraping(url: tuple) -> dict:
    def get_university_name(full_url):
        return sub(r"\s-\s\d{1,}", "", extract(html=get_response(full_url), query="//h4[@class=\"diemchuan-truong__title\"]/a/text()"))

    def get_benchmark_by_year(id, start_year: Optional[int] = 2015, end_year: Optional[int] = 2020):
        benchmark_by_year = []
        majors_by_years = []
        admissions = []
        for year in range(start_year, end_year + 1):
            response = get_response(
                api_endpoint, "POST", make_payload(year, id))
            majors = Selector(text=response).xpath("//tbody/tr[1]")
            for major in majors:
                admissions.append({
                    "tenNganh": extract(major.get(), "//td[2]/a/text()"),
                    "maNganh": extract(major.get(), "//td[3]/text()"),
                    "khoiXetTuyen": Selector(text=major.get()).xpath("//td[4]//a/text()").getall(),
                    "diemChuan": float(extract(major.get(), "//td[5]/text()")),
                    "ghiChu": extract(major.get(), "//td[7]/text()")
                })
            majors_by_years.append({
                "nam": year,
                "nganhXetTuyen": admissions
            })
        return majors_by_years
    return {
        "tenTruongDH": get_university_name(url[0]),
        "namXetTuyen": get_benchmark_by_year(url[1])
    }


if __name__ == "__main__":
    data = []

    for url in start_urls:
        data.append(scraping(url))

    with open("data.json", "w", encoding="UTF-8") as f:
        json.dump(data, f, ensure_ascii=False)
        f.close()
