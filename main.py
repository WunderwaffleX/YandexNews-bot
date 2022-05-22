import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import telebot
from bot_token import token
from aiogram.utils.markdown import hbold, hlink

tag = "биткоин"
cNews = 0
lastTag = ""


def get_data(tag):
    ua = UserAgent()
    headers = {
        'user-agent': f'{ua.random}'
    }
    countNews = 0
    project_data_list = []
    project_urls = []
    project_titles = []
    for item in range(1, 3):
        if item == 1:
            url = f'https://newssearch.yandex.ru/news/search?text={tag}'
            req = requests.get(url, headers)
            with open("sait.html", "w", encoding="utf-8") as file:
                file.write(req.text)
            with open("sait.html", encoding="utf-8") as file:
                src = file.read()
            soup = BeautifulSoup(src, "lxml")
            if item == 1:
                reqid = soup.find("head").findAll("script")
                string = str(reqid[0])
                id_index_start = string.find("d=\"")
                id_index_start += 3
                id_index_end = string.find("H")
                id_index_end += 1
                id_tag = string[id_index_start:id_index_end]
            articles = soup.find_all("h3", class_="mg-snippet__url-wrapper")
            imgs = soup.find_all("div", class_="mg-favorites-dot__image mg-snippet__src")
            i = 0
            for article in articles:
                countNews += 1
                project_url = article.find("a", class_="mg-snippet__url").get("href")
                project_title = article.find("a", class_="mg-snippet__url").find("div",
                                                                                 class_="mg-snippet__title").find(
                    "span", role="text").text
                project_urls.append(project_url)
                project_titles.append(project_title)
                try:
                    project_img = imgs[i].find("img").get("src")
                except Exception:
                    project_img = "No logo"

                if countNews > 2 and project_data_list[countNews - 2].get('Заголовок:') == project_title:
                    countNews -= 1
                else:
                    project_data_list.append(
                        {
                            "Номер статьи:": countNews,
                            "Ссылка на статью:": project_url,
                            "Ссылка на logo:": project_img,
                            "Заголовок:": project_title
                        }
                    )
                i += 1
        elif item == 2:
            url = f'https://newssearch.yandex.ru/news/search?p=1&text={tag}&ajax=1&neo_parent_id={id_tag} '
            for cc in range(0, 4):
                req = requests.get(url, headers)
                with open('get.json', 'w', encoding="utf-8") as file:
                    json.dump(req.json(), file, indent=4, ensure_ascii=False)
                data_get = req.json()
                urlNextPage = data_get.get('data').get('nextPage')
                stories = data_get.get('data').get('stories')
                for iGet in stories:
                    url = "https://newssearch.yandex.ru" + urlNextPage
                    countNews += 1
                    urlImage = iGet.get('docs')[0].get('image')
                    urlSource = iGet.get('docs')[0].get('url')
                    titleTemp = ""
                    try:
                        for tit in iGet.get('docs')[0].get('title'):
                            titleTemp = titleTemp + tit.get('text')
                    except Exception:
                        print("end")
                    if project_data_list[countNews - 2].get('Заголовок:') == titleTemp:
                        countNews -= 1
                    else:
                        project_data_list.append(
                            {
                                "Номер статьи:": countNews,
                                "Ссылка на статью:": urlSource,
                                "Ссылка на logo:": urlImage,
                                "Заголовок:": titleTemp
                            })

    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(project_data_list, file, indent=4, ensure_ascii=False)


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет! Введи тег запроса для получения новостей")

    @bot.message_handler(content_types=["text"])
    def send_text(message):
        bot.send_message(
            message.chat.id,
            "Пожалуйста подождите..."
        )
        try:
            global lastTag
            global cNews
            if message.text != lastTag:
                get_data(message.text)
                cNews = 0

            with open("data.json", "r", encoding="utf-8") as file:
                out = json.load(file)
            for j in out:
                if j.get("Номер статьи:") <= cNews:
                    continue
                card = j.get("Ссылка на статью:")
                bot.send_message(
                    message.chat.id,
                    card
                )
                cNews += 1
                if cNews % 5 == 0:
                    break
            lastTag = message.text
        except Exception:
            bot.send_message(
                message.chat.id,
                "Что то пошло не по плану("
            )

    bot.polling()

def main():
    get_data(tag)
    # telegram_bot(token)


if __name__ == '__main__':
    main()

