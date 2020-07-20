import copy
import logging
import re

from prettytable import PrettyTable
from requests_html import HTMLSession

logging.basicConfig(level=logging.WARNING)


class YandexZen:
    channel_api_url = 'https://zen.yandex.ru/api/v3/launcher/more?country_code=ru&channel_name='
    req = HTMLSession()
    req.headers.update(
        {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.1 Mobile/15E148 Safari/604.1'}
    )


class Channel(YandexZen):

    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.channel_url = "{}{}".format(self.channel_api_url, self.channel_name)
        self.response = self.req.get(self.channel_url)

    def name(self):
        return self.response.json()['header']['source']['title']

    def publication(self):
        self.publication_list = []
        self.__response = copy.deepcopy(self.response)
        for self.pub in self.__response.json()['items']:
            self.publication_list.append(self.pub['link'])
        try:
            while self.__response.json()['more']['link']:
                self.__response = self.req.get(self.__response.json()['more']['link'])
                for self.pub in self.__response.json()['items']:
                    self.publication_list.append(self.pub['link'])
        except ValueError:
            logging.info("Сбор статей с использованием пагинации завершен.")
        return self.publication_list

    def subscribers(self):
        try:
            return self.response.json()['header']['source']['subscribers']
        except ValueError:
            return 0

    def audience(self):
        try:
            return self.response.json()['header']['source']['audience']
        except ValueError:
            return 0

    def description(self):
        try:
            return self.response.json()['header']['source']['description']
        except ValueError:
            return None


class Post(YandexZen):

    def __init__(self, post_url) -> None:
        self.post_url = post_url
        self.response = self.req.get(self.post_url)
        self.response.html.render()

    def title(self):
        self.title = re.findall(r'(?<=<meta\ property="og:title"\ content=")[\w\W]*?(?="/>)', self.response.text)[0]
        return self.title

    def post_type(self):
        return 0

    def hashtag(self):
        self.hashtag = self.response.html.find('.zen-tag-publishers__title')
        self.hashtag = str([i.text for i in self.hashtag]).replace('\'', '').replace(']', '').replace('[', '')
        return self.hashtag

    def comment(self):
        try:
            self.comment = self.response.html.find('.ui-lib-comments-icon__bubble', first=True).text
            if not self.comment:
                raise AttributeError
            else:
                self.comment = int(self.comment)
        except AttributeError:
            self.comment = 0
        return self.comment

    def like(self):
        try:
            self.like = int(self.response.html.find('.likes-count-minimal__count', first=True).text)
        except AttributeError:
            self.like = 0
        return self.like

    def viewed(self):
        try:
            self.viewed = self.response.html.find('.article-stat-tip__value', first=True).text
            self.viewed = self.viewed.split()
            if ',' in self.viewed[0] and 'тыс.' in self.viewed[1]:
                self.viewed = round(float(self.viewed[0].replace(',', '.')) * 1000)
            elif 'тыс.' in self.viewed[1]:
                self.viewed = int(self.viewed[0]) * 1000
            else:
                self.viewed = int(self.viewed[0])
        except (AttributeError, IndexError):
            self.viewed = 0
        return self.viewed

    def reading(self):
        try:
            self.reading = self.response.html.find('.article-stat__count', first=True).text
            self.reading = self.reading.split()
            if ',' in self.reading[0] and 'тыс.' in self.reading[1]:
                self.reading = round(float(self.reading[0].replace(',', '.')) * 1000)
            elif 'тыс.' in self.reading[1]:
                self.reading = int(self.reading[0]) * 1000
            elif '<' in self.reading[0]:
                self.reading = int(self.reading[1])
            else:
                self.reading = int(self.reading[0])
        except (AttributeError, IndexError):
            self.reading = 0
        return self.reading

    def time_reading(self):
        try:
            self.time_reading = self.response.html.find('.article-stat__count')[1].text
            self.time_reading = self.time_reading.split()
            if ',' in self.time_reading[0] and 'мин.' in self.time_reading[1]:
                self.time_reading = round(float(self.time_reading[0].replace(',', '.')) * 60)
            elif 'мин.' in self.time_reading[1]:
                self.time_reading = int(self.time_reading[0]) * 60
            else:
                self.time_reading = int(self.time_reading[0])
        except (AttributeError, IndexError):
            self.time_reading = 0
        return self.time_reading

    def reading_percentage(self, viewed, reading):
        try:
            return round(int(reading) / int(viewed) * 100)
        except ZeroDivisionError:
            return 0

    def date(self):
        try:
            self.date = re.findall(r'(?<=<span\ class="article-stat__date">)[\w\W]*?(?=</span>)', self.response.text)[0]
        except IndexError:
            self.date = 0
        return self.date


class Report():
    def __init__(self, name, sortby) -> None:
        self.name = name
        self.table = PrettyTable(border=True, header=True)
        self.table.format = True
        self.table.field_names = ["№", "Дата", "Название", "Тип", "Лайки", "Комментарии", "Просмотры", "Дочитано", "%", "Время", "Хештеги"]
        self.table.align["Название"] = "l"
        self.table.align["Дата"] = "l"
        self.sortby = sortby
        if self.sortby == 'likes':
            self.table.sortby = "Лайки"
        elif self.sortby == 'comments':
            self.table.sortby = "Комментарии"
        elif self.sortby == 'views':
            self.table.sortby = "Просмотры"
        elif self.sortby == 'reads':
            self.table.sortby = "Дочитано"
        self.table.reversesort = True
        self.row_count = 1

    def add_row(self, date, title, post_type, like, comment, viewed, reading, reading_percentage, time_reading, hashtag):
        self.date = date
        self.title = title
        self.post_type = post_type
        self.like = like
        self.comment = comment
        self.viewed = viewed
        self.reading = reading
        self.reading_percentage = reading_percentage
        self.time_reading = time_reading
        self.hashtag = hashtag
        self.table.add_row([self.row_count, self.date, self.title, self.post_type, self.like, self.comment, self.viewed, self.reading, "{}%".format(self.reading_percentage), self.time_reading, self.hashtag])
        self.row_count += 1

    def output(self, o_format, header):
        self.o_format = o_format
        self.header = header
        if self.o_format == 'asci':
            print(self.header)
            print(self.table)
        elif self.o_format == 'html':
            self.html = self.table.get_html_string()
            with open('{}.html'.format(self.name), '+w') as self.file:
                self.file.write(self.html)
            print("Отчет сохранен в файл {}.html".format(self.name))
