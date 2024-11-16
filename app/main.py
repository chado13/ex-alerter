import datetime
import os
from typing import TypedDict

import __main__
import requests
import typer
from bs4 import BeautifulSoup
from discord_webhook import DiscordEmbed, DiscordWebhook
from typing_extensions import Annotated

from app.config import WEBHOOK_URI

app = typer.Typer()

CURRENCY={
    "jp": "JPY",
    "us": "USD"
}

class EXDataDict(TypedDict):
    dt: datetime.datetime
    ex_nm: str
    buy_ex: float
    trade_ex: float
@app.command()
def main(country: Annotated[str, typer.Option()]) -> None:
    currency = CURRENCY[country]
    today = datetime.datetime.today().date()
    html = _get_html(currency=currency, dt=today)
    data = _pasrse(html)
    alert_discord(data)
    
    
def _get_html(currency: str, dt: datetime.datetime) -> BeautifulSoup:
    url = "https://www.kebhana.com/cms/rate/wpfxd651_01i_01.do"
    headers = {
        "referer": "https://www.kebhana.com/cms/rate/index.do?contentUrl=/cms/rate/wpfxd651_01i.do"
    }
    payload = {
        "ajax": True,
        "curCd": currency,
        "tmpInqStrDt": str(dt),
        "pbldDvCd": 3,
        "pbldSqn": "",
        "hid_key_data": "",
        "inqStrDt": int(dt.strftime("%Y%m%d")),
        "inqKindCd": 1,
        "hid_enc_data": "",
        "requestTarget": "searchContentDiv"
    }
    res = requests.post(url=url, headers=headers, data=payload)
    if res.status_code == 200:
        return BeautifulSoup(res.content, "lxml")
    else:
        raise ValueError
    
def _pasrse(html: BeautifulSoup) -> datetime.datetime:
    try:
        tags = html.select("div.printdiv > p.txtRateBox > span.fl")[0]
    except IndexError:
        raise
    date_str = " ".join([tag.text.strip() for tag in tags.find_all("strong")[:2]])
    dt =  datetime.datetime.strptime(date_str, "%Y년%m월%d일 %H시%M분%S초")
    
    try:
        table = html.select("div.printdiv > table > tbody")[0]
    except IndexError:
        raise
    tds = table.find_all("td")
    ex_nm = tds[0].text.strip()
    buy_ex = tds[1].text.strip()
    trade_ex=tds[8].text.strip()
    return EXDataDict(dt=dt, ex_nm=ex_nm, buy_ex=float(buy_ex), trade_ex=float(trade_ex))
    
def alert_discord(data: EXDataDict) -> None:
    """DISCORD 채널에 ALERT 메시지를 보낸다.

    Args:
        message: additional message of card
        should_trace: if True, add traceback to message

    Examples:
        >>> try:
        ...     main()
        ... except Exception:
        ...     alert_discord("Something went wrong")
    """
    title = f"오늘의 {data['ex_nm']} 환율"
    body = f"{data['dt']} 조회 기준 \n 살때: {data['buy_ex']} \n 매매기준율: {data['trade_ex']}"
    embed = DiscordEmbed(description=body, color="03b2f8")
    embed.set_timestamp()
    embed.set_author(
        name=title
    )
    webhook = DiscordWebhook(url=WEBHOOK_URI)
    webhook.add_embed(embed)


    try:
        webhook.execute()
    except Exception:
        raise
        
if __name__ == "__main__":
    app()