import datetime
import logging
from typing import Dict

import azure.functions as func
from bs4 import BeautifulSoup
import requests
import json

URL = "https://pogoda.onet.pl/prognoza-pogody/gdansk-287788"


def get_page(url: str) -> str:
    return requests.get(url).content


def extract_data(url: str) -> Dict[str, str]:
    data = get_page(url)
    soup = BeautifulSoup(data, "html.parser")
    return {"temperature": soup.select_one("div.temp").text}


def transform_data(data: Dict[str, str], date: str) -> Dict[str, int]:
    data["temperature"] = int(data["temperature"].strip("°"))
    data["date"] = date
    return data


def main(mytimer: func.TimerRequest, out: func.Out[func.Document]) -> None:
    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    if mytimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function ran at %s", utc_timestamp)
    data = transform_data(extract_data(URL), utc_timestamp)
    logging.info("Data: %s", data)
    out.set(func.Document.from_json(json.dumps(data)))
