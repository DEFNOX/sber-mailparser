import email
from email.utils import parseaddr
from email.header import decode_header, make_header
import imaplib
from bs4 import BeautifulSoup
import re
import requests
from datetime import datetime
import zipfile
import configparser
import json
import argparse

'''
Python 3 program for parsing Sberbank-specific email with file link.
Variables below should be adjusted before using
Program uses IMAP to retrieve messages, so make sure account is allowed to connect with IMAP

Requirements:
requests, bs4 (beautifulsoup 4), imaplib, re, datetime, email, zipfile

Author: Ivan Tyurin
tyurin.su | tg: @san3ko
'''
# cfg = 'D:/Prog/sber/config.ini'


parser = argparse.ArgumentParser()
parser.add_argument("-cfg", "--config", help="full path to config file")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read(str(args.config))
# config.read(str(cfg))

# mail settings
server = config.get('mail', 'server')
user = config.get('mail', 'user')
pwd = config.get('mail', 'pwd')

# program settings
sender = config.get('program', 'sender')
match_regex = config.get('program', 'match_regex')
file_path = config.get('program', 'file_path')
extract_dir = config.get('program', 'extract_dir')
file_prefix = config.get('program', 'file_prefix')
target_file = config.get('program', 'target_file')
use_proxy = config.get('program', 'use_proxy')

# telegram settings
notify_admin = config.get('telegram', 'notify_admin')             # Set False for disabling notifications
notify_tg = json.loads(config.get('telegram', 'notify_tg'))         # List of chat_id's (make sure it is a list)
notify_tg_botkey = config.get('telegram', 'notify_tg_botkey')      # bot key


def admin_notify(message):
    """
    Telegram notification for admins
    """
    a = {'ok' : False}
    if notify_admin:
        msg = "*Авто-загрузка | Сбербанк*  \n" + message
        # msg = re.sub("_", "\_", msg)
        if len(notify_tg) > 1:
            for tg_user in notify_tg:
                params = {
                    'chat_id': tg_user,
                    'text': msg,
                    'parse_mode': 'Markdown'
                }
                url = "https://api.telegram.org/bot{}/sendMessage".format(notify_tg_botkey)
                tg = requests.get(url, proxies=tg_proxy, data=params)
                a = json.loads(tg.content.decode())
        else:
            params = {
                'chat_id': notify_tg[0],
                'text': msg,
                'parse_mode': 'Markdown'
            }
            url = "https://api.telegram.org/bot{}/sendMessage".format(notify_tg_botkey)
            tg = requests.get(url, proxies=tg_proxy, data=params)
            a = json.loads(tg.content.decode())
        if not a['ok']:
            print("Telegram error:\n{}".format(a))


def parse_html(mail):
    """
    Parser for HTML part of message
    """
    link = ""
    soup = BeautifulSoup(mail, "lxml")
    # print(soup.prettify())
    for item in soup.find_all('a'):
        link = re.findall(match_regex, str(item.get('href')))
        if len(link) != 0:
            return [True, item.get('href')]
    if len(link) == 0:
        return [False, None]


def get_messages():
    """
    Retrieving unread messages
    """
    m.select('INBOX')
    resp, items = m.search(None, '(UNSEEN)')
    items = items[0].split()
    # print(items)
    return items


def download_file(url):
    """
    File downloading
    """
    name = file_path + file_prefix + "_" + datetime.today().strftime('%Y-%m-%d') + '.zip'
    header = headers = {'User-Agent': str(config.get('other', 'user_agent'))}
    try:
        if use_proxy:
            proxy = {'https': 'socks5://{}:{}@{}:{}'.format(config.get('proxy', 'proxy_user'),
                                                            config.get('proxy', 'proxy_password'),
                                                            config.get('proxy', 'proxy_server'),
                                                            config.get('proxy', 'proxy_port'))}
            response = requests.get(url, allow_redirects=True, headers=header, proxies=proxy)
        else:
            response = requests.get(url, allow_redirects=True, headers=header)
    except Exception:
        # admin_notify("‼ *Ошибка!* `Ссылка недоступна для скачивания.`")
        return [False, None]
    else:
        open(name, 'wb').write(response.content)
        # print(name)
        return [True, name]


def extract(file):
    """
    Extracting file from archive
    """
    name = file_prefix + "_" + datetime.today().strftime('%Y-%m-%d') + '.txt'
    zip = zipfile.ZipFile(file, 'r')
    for finfo in zip.infolist():
        if finfo.filename == target_file:
            finfo.filename = name
            try:
                zip.extract(finfo, path=extract_dir)
            except Exception:
                return [False, None]
            else:
                return [True, "{}{}".format(extract_dir, name)]


if __name__ == "__main__":
    m = imaplib.IMAP4_SSL(server)
    m.login(user, pwd)
    items = get_messages()

    if len(items) != 0:
        for item in items:
            resp, data = m.fetch(item, '(RFC822)')
            mail_full = email.message_from_bytes(data[0][1])
            if mail_full.is_multipart():
                for part in mail_full.get_payload():
                    mail = mail_full.get_payload()[0].get_payload(decode=True).decode()
            else:
                mail = mail_full.get_payload(decode=True).decode()
            parse = parse_html(mail)
            mail_from = parseaddr(mail_full['From'])[1]
            mail_from = mail_full['X-Envelope-From']
            mail_subj = str(make_header(decode_header(mail_full['Subject'])))
            if mail_from == sender:
                if parse[0]:
                    download_res, name = download_file(parse[1])
                    if download_res:
                        extract_res, txt_name = extract(name)
                        if extract_res:
                            admin_notify("✅ Файл-выписка успешно загружена и распакована!  \n`{}  \n{}`".format(str(name), str(txt_name)))
                        else:
                            admin_notify("‼ *Ошибка!* `Не удалось распаковать файл.`")
                    else:
                        admin_notify("‼ *Ошибка!* `Ссылка недоступна для скачивания.`")
                else:
                    admin_notify("❌ `Ссылка не найдена в последнем обработанном письме.`")
            else:
                admin_notify("📧  Новое сообщение от {}  \n`Тема: {}`".format(mail_from, mail_subj))
    else:
        admin_notify('❌  Новых сообщений не найдено')
