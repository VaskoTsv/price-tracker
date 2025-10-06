import requests
import smtplib
from bs4 import BeautifulSoup
import os

# Items to be tracked
# XIAOMI_LAPTOP = {
#     'url': 'https://www.gearbest.com/ultrabooks/pp_3008693117937832.html',
#     'title_classes': ["goodsIntro_title"],
#     'price_classes': ["goodsIntro_price", "js-currency", "js-panelIntroPrice"],
#     'target_price': 650,
#     'currency': 'Euro',
# }

# LG_TV_32 = {
#     'url': 'https://www.technopolis.bg/bg/Televizori/Televizor-LG-32LK510BPLD-LED/p/16435',
#     'title_classes': ["product-name"],
#     'price_classes': ["price-value"],
#     'target_price': 300,
#     'currency': 'BGN',
# }

VANTRUE_DASHCAM = {
    'url': 'https://www.amazon.de/dp/B0DB59W7FW?ref=ppx_yo2ov_dt_b_fed_asin_title',
    'title_classes': ["a-size-large", "product-title-word-break"],
    'price_classes': ["a-price-whole", "aok-offscreen"],
    'target_price': 200,
    'currency': 'EURO',
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
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/84.0.4147.125 Safari/537.36"
        )
    }

    try:
        page = requests.get(url, headers=headers, timeout=15)
        page.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.findAll(match_class(title_classes))
    price = soup.findAll(match_class(price_classes))

    if not title or not price:
        print(f"[WARN] Could not find title or price for {url}: {title}/{title_classes} - {price}/{price_classes}")
        return


    title = title[0].get_text().strip()
    price_text = price[0].get_text().strip()

    try:
        price_value = float(''.join(price_text.split(' ')).split('.', 1)[0])
    except ValueError:
        print(f"[WARN] Failed to parse price: '{price_text}'")
        return

    if price_value < target_price:
        send_mail(title, url, price_value, currency)
    else:
        print(f"[INFO] {title} is {price_value} {currency}, above target {target_price}.")


def send_mail(title, url, price, currency):
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    if not email_user or not email_pass:
        print("[ERROR] Missing email credentials.")
        return

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_user, email_pass)

        subject = f"Price for {title[:90]} fell to {price} {currency}!"
        body = f"Check this link: {url}"
        msg = f"Subject: {subject}\n\n{body}"

        server.sendmail(email_user, "vask_o@abv.bg", msg)
        server.quit()
        print(f"[EMAIL] Notification sent for {title}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")


# Run checks
# check_price(**LG_TV_32)
check_price(**VANTRUE_DASHCAM)
