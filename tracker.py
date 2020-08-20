import requests
import time
import smtplib
from bs4 import BeautifulSoup

# Items to be tracked
XIAOMI_LAPTOP = {
    'url': 'https://www.gearbest.com/ultrabooks/pp_3008693117937832.html',
    'title_classes': ["goodsIntro_title"],
    'price_classes': ["goodsIntro_price", "js-currency", "js-panelIntroPrice"],
    'target_price': 650,
    'currency': 'Euro',
}

HUAWEI_P30_PRO = {
    'url': 'https://www.technopolis.bg/bg/Mobilni-telefoni/Smartfon-GSM-HUAWEI-P30-PRO-DS-BLACK/p/536838',
    'title_classes': ["product-name"],
    'price_classes': ["price-value"],
    'target_price': 700,
    'currency': 'BGN',
}

LG_TV_32 = {
    'url': 'https://www.technopolis.bg/bg/Televizori/Televizor-LG-32LK510BPLD-LED/p/16435',
    'title_classes': ["product-name"],
    'price_classes': ["price-value"],
    'target_price': 300,
    'currency': 'BGN',
}


def match_class(target):
    def do_match(tag):
        classes = tag.get('class', [])
        return all(c in classes for c in target)

    return do_match


def check_price(**kwargs):
    url = kwargs['url']
    title_classes = kwargs['title_classes']
    price_classes = kwargs['price_classes']
    target_price = kwargs['target_price']
    currency = kwargs['currency']

    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/84.0.4147.125 Safari/537.36'}

    page = requests.get(url, headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    title = soup.findAll(match_class(title_classes))
    price = soup.findAll(match_class(price_classes))

    if title is None or len(title) == 0:
        return
    elif price is None or len(price) == 0:
        return

    title = title[0].get_text().strip()
    price = price[0].get_text().strip()

    # remove cents from price
    price_separator = '.'
    price = price.split(price_separator, 1)[0]
    # remove empty spaces from price if any
    price = ''.join(price.split(' '))
    # convert price from string to float
    converted_price = float(price)

    if converted_price < target_price:
        send_mail(title, url, price, currency)


def send_mail(title, url, price, currency):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('greengoones@gmail.com', 'cnganxedtryqirsn')

    title = title.encode('ascii', 'ignore')
    subject = f"Price for {title[0:95]} fell down to {price} {currency}!"
    body = f'Check this link for more information - {url}'

    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail(
        'greengoones@gmail.com',
        'vask_o@abv.bg',
        msg
    )

    server.quit()


# Start tracking
while (True):
    check_price(**XIAOMI_LAPTOP)
    check_price(**HUAWEI_P30_PRO)
    check_price(**LG_TV_32)
    # Check if the price has fallen down twice a day
    time.sleep(60 * 60 * 12)
