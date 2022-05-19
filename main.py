import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from aiogram import Bot, executor, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.markdown import hlink
from bot_token import token
from states.city import Select_City
from states.datetime import Select_Time
import calendar
import time
from datetime import datetime
cNews = 0
lastTag = ""
flag = False

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

async def get_data(tag, city, id, TS, TE):
    ua = UserAgent()
    headers = {
        'user-agent': f'{ua.random}'
    }
    countNews = 0
    project_data_list = []
    project_urls = []
    project_titles = []
    Edate = None
    Sdate = None
    if TE is None:
        url = f'https://newssearch.yandex.ru/news/search?text={tag + "+" + city}'
    else:
        Edate = datetime.fromtimestamp(TE).strftime('%Y%m%d')
        TE = TE*1000
        if TS is None:
            url = f'https://newssearch.yandex.ru/news/search?text={tag + "+" + city + "date%3A" + Edate + "&filter_date="+ str(TE)}'
        else:
            Sdate = datetime.fromtimestamp(TS).strftime('%Y%m%d')
            TS = TS*1000
            url = f'https://newssearch.yandex.ru/news/search?text={tag + "+" + city + "date%3A" + Sdate + ".." + Edate +"&filter_date=" + str(TS) + "%2C" + str(TE)}'
    req = requests.get(url, headers)
    with open("sait.html", "w", encoding="utf-8") as file:
        file.write(req.text)
    with open("sait.html", encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
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
        # if (countNews > 19):
        #     break
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
    for item in range(2):
        if TE is None:
            url = f'https://newssearch.yandex.ru/news/search?p=1&text={tag + "+" + city}&ajax=1&neo_parent_id={id_tag} '
        else:
            if TS is None:
                url = f'https://newssearch.yandex.ru/news/search?p=1&text={tag + "+" + city + "date%3A" + Edate + "&filter_date="+ str(TE)}&ajax=1&neo_parent_id={id_tag} '
            else:
                url = f'https://newssearch.yandex.ru/news/search?p=1&text={tag + "+" + city + "date%3A" + Sdate + ".." + Edate +"&filter_date=" + str(TS) + "%2C" + str(TE)}&ajax=1&neo_parent_id={id_tag} '
        for cc in range(0, 4):
            req = requests.get(url, headers)
            with open('get.json', 'w', encoding="utf-8") as file:
                json.dump(req.json(), file, indent=4, ensure_ascii=False)
            data_get = req.json()
            urlNextPage = data_get.get('data').get('nextPage')
            stories = data_get.get('data').get('stories')
            if urlNextPage != None:
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
    with open(str(id) + ".json", "w", encoding="utf-8") as file:
        json.dump(project_data_list, file, indent=4, ensure_ascii=False)

###############################################################################################
async def news(city):
    url = "https://yandex.ru/news"
    if city == 'Санкт-Петербург':
        url = "https://yandex.ru/news/region/saint_petersburg"
    if city == 'Москва':
        url = "https://yandex.ru/news/region/moscow"
    if city == 'Екатеринбург':
        url = "https://yandex.ru/news/region/yekaterinburg"
    ua = UserAgent()
    headers = {
        'user-agent': f'{ua.random}'
    }
    req = requests.get(url, headers)
    with open("sait1.html", "w", encoding="utf-8") as file:
        file.write(req.text)
    with open("sait1.html", encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")

    block_top = soup.find("div", class_="mg-grid__row mg-grid__row_gap_8 news-top-flexible-stories news-app__top")
    project_urls = []
    project_titles = []
    project_times = []
    project_imgs = []

    project_data1 = []
    first_data1 = []

    count = 1
    first = block_top.find("div", class_="mg-grid__col mg-grid__col_xs_8")
    first_href = first.find("h2", class_="mg-card__title").find("a").get("href")
    first_title = first.find("h2", class_="mg-card__title").find("a").text.strip()
    first_time = first.find("span", class_="mg-card-source__time")
    first_img = first.find("img", class_="neo-image neo-image_loaded").get("src")
    # print(first_time.text, "-", first_title, ":", first_href, " - ", first_img)

    project_data1.append(
        {
            "Номер статьи:": count,
            "Ссылка на статью:": first_href,
            "Ссылка на logo:": first_img,
            "Заголовок:": first_title
        }
    )

    # project_urls.append(first_href)
    # project_titles.append(first_title)
    # project_times.append(first_time)
    # project_imgs.append(first_img)

    full_project = []
    articles = block_top.find_all("div", class_="mg-grid__col mg-grid__col_xs_4")

    for item in articles:
        count = count + 1
        project_url = item.find("h2", class_="mg-card__title").find("a").get("href")
        project_title = item.find("h2", class_="mg-card__title").find("a").text.strip()
        project_time = item.find("span", class_="mg-card-source__time")
        #project_img = item.find("div", class_="mg-card__media-block mg-card__media-block_type_image").get("style")
        # l = len(project_img) - 1;
        # print(project_time.text, "-", project_title, ":", project_url, " - ", project_img[21:l])
        # project_urls.append(project_url)
        # project_titles.append(project_title)
        # project_times.append(project_time)
        # project_imgs.append(project_img)

        project_data1.append(
            {
                "Номер статьи:": count,
                "Ссылка на статью:": project_url,
                # "Ссылка на logo:": project_img,
                "Заголовок:": project_title
            }
        )

        # full_project.extend(project_url).extend(project_title).extend(project_img)
    with open("news_dict.json", "w", encoding="utf-8") as file:
        # json.dump(first_data1, file, indent=4, ensure_ascii=False)
        json.dump(project_data1, file, indent=4, ensure_ascii=False)


##############################################################################################

@dp.message_handler(commands='start')
async def start_message(message: types.Message):
    start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'По городу', 'Период']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    # await bot.send_message(message.from_user.id, text = hlink('VK', 'https://vk.com'), parse_mode="HTML")
    await bot.send_message(message.from_user.id,
                           "Привет! Введи тег запроса для получения новостей, либо выбери параметр подбора новостей",
                           reply_markup=keyboard)


@dp.message_handler(Text(equals='Последние 5 новостей'))
async def five_last(message: types.message, state: FSMContext):
    data = await state.get_data()
    city = data.get(f'{str(message.from_user.id)+"c"}')
    await news(city)
    with open("news_dict.json", encoding="utf-8") as file:
        news_dict = json.load(file)
    for j in news_dict:
        # print(j)
        card1 = j.get("Ссылка на статью:")
        card2 = j.get("Заголовок:")
        await bot.send_message(message.from_user.id, text = hlink(card2, card1), parse_mode="HTML")


@dp.message_handler(Text(equals='По городу'))
async def enter_city(message: types.message):
    start_buttons = ['Москва', 'Санкт-Петербург', 'Екатеринбург']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await bot.send_message(message.from_user.id, 'Введите город', reply_markup=keyboard)
    await Select_City.city_set.set()

@dp.message_handler(state=Select_City.city_set)
async def choice_city(message: types.Message, state: FSMContext):
    # await state.update_data(city=message.text)
    data = await state.get_data()
    # lastTag = data.get(str(message.from_user.id))
    data[f'{str(message.from_user.id)+"c"}'] = message.text
    await state.reset_data()
    await state.update_data(data)
    if f'{str(message.from_user.id)+"e"}' in data:
        if data[f'{str(message.from_user.id) +"e"}'] is None:
            start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'Удалить город', 'Период']
        else:
            start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'Удалить город', 'Удалить период']
    else:
        start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'Удалить город', 'Период']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await bot.send_message(message.from_user.id, "Принято", reply_markup=keyboard)
    await state.reset_state(with_data=False)

@dp.message_handler(Text(equals='Период'))
async def enter_time(message: types.message):
    start_buttons = ['За сегодня', 'За вчера', 'За прошлую неделю', 'За прошлый месяц']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await bot.send_message(message.from_user.id, 'Выберете промежуток времени', reply_markup=keyboard)
    await Select_Time.time_set.set()

@dp.message_handler(state=Select_Time.time_set)
async def choice_time(message: types.Message, state: FSMContext):
    # await state.update_data(city=message.text)
    data = await state.get_data()
    # lastTag = data.get(str(message.from_user.id))
    time2 = calendar.timegm(time.gmtime())
    time1 = None
    if message.text == 'За вчера':
        time2 = calendar.timegm(time.gmtime()) - 86400
    if message.text == 'За прошлую неделю':
        time2 = calendar.timegm(time.gmtime()) - 7 * 86400
        time1 = time2 - 7 * 86400
    if message.text == 'За прошлый месяц':
        time2 = calendar.timegm(time.gmtime()) - 30 * 86400
        time1 = time2 - 30 * 86400

    data[f'{str(message.from_user.id) + "s"}'] = time1
    data[f'{str(message.from_user.id) + "e"}'] = time2
    await state.reset_data()
    await state.update_data(data)
    if f'{str(message.from_user.id)+"c"}' in data:
        if data[f'{str(message.from_user.id)+"c"}'] is None:
            start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'По городу', 'Удалить период']
        else:
            start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'Удалить город', 'Удалить период']
    else:
        start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'По городу', 'Удалить период']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await bot.send_message(message.from_user.id, "Принято", reply_markup=keyboard)
    await state.reset_state(with_data=False)



@dp.message_handler(Text(equals='Удалить город'))
async def delete_city(message: types.message, state: FSMContext):
    data = await state.get_data()
    # lastTag = data.get(str(message.from_user.id))
    data[f'{str(message.from_user.id)+"c"}'] = None
    await state.reset_data()
    await state.update_data(data)
    if f'{str(message.from_user.id) + "e"}' in data:
        if data[f'{str(message.from_user.id )+ "e"}'] is None:
            start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'По городу', 'Период']
        else:
            start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'По городу', 'Удалить период']
    else:
        start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'По городу', 'Период']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    # await message.send_message(message.from_user.id, "Привет! Введи тег запроса для получения новостей, либо выбери параметр подбора новостей", reply_markup=keyboard)
    await bot.send_message(message.from_user.id, "Город удален", reply_markup=keyboard)

@dp.message_handler(Text(equals='Удалить период'))
async def delete_city(message: types.message, state: FSMContext):
    data = await state.get_data()
    # lastTag = data.get(str(message.from_user.id))
    data[f'{str(message.from_user.id) + "e"}'] = None
    data[f'{str(message.from_user.id )+"s"}'] = None
    await state.reset_data()
    await state.update_data(data)
    if f'{str(message.from_user.id)+"c"}' in data:
        if data[f'{str(message.from_user.id)+"c"}'] is None:
            start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'По городу', 'Период']
        else:
            start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'Удалить город', 'Период']
    else:
        start_buttons = ['Последние 5 новостей', 'Еще 5 новостей', 'По городу', 'Период']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    # await message.send_message(message.from_user.id, "Привет! Введи тег запроса для получения новостей, либо выбери параметр подбора новостей", reply_markup=keyboard)
    await bot.send_message(message.from_user.id, "Период удален", reply_markup=keyboard)


@dp.message_handler()
async def your_news(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Пожалуйста подождите")
    try:
        data = await state.get_data()
        global cNews
        if message.text != 'Еще 5 новостей':
            city = data.get(f'{str(message.from_user.id)+"c"}')
            times = data.get(f'{str(message.from_user.id)+"s"}')
            timee = data.get(f'{str(message.from_user.id)+"e"}')
            await state.update_data(lastTag=message.text)
            if city is None:
                city = ''
            else:
                city = city + '+'
            await get_data(message.text, city, message.from_user.id, times, timee)
            cNews = 0
        with open(str(message.from_user.id) + ".json", "r", encoding="utf-8") as file:
            out = json.load(file)
        for j in out:
            if j.get("Номер статьи:") <= cNews:
                continue
            # print(j)
            card = j.get("Ссылка на статью:")
            card2 = j.get("Заголовок:")
            await bot.send_message(message.from_user.id, text=hlink(card2, card), parse_mode="HTML")
            # await bot.send_message(message.chat.id, card)
            cNews += 1
            if cNews % 5 == 0:
                break
    except Exception:
        await bot.send_message(message.chat.id, "Что-то пошло не по плану(")


if __name__ == '__main__':
    print(time.gmtime())
    executor.start_polling(dp)
