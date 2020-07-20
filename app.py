import argparse

from function import Channel, Post, Report

PARSER = argparse.ArgumentParser(description='Yandex.Zen analatycs channel analytics utility')
PARSER.add_argument('-u', help='channel url', required=True)
PARSER.add_argument('-o', help='output format [asci, html]', default='asci')
PARSER.add_argument('-s', help='sortby [likes, comments, views, reads]', default='views')
ARGS = vars(PARSER.parse_args())

if ARGS['u'].split('/')[0] == 'https:' and ARGS['u'].split('/')[2] == 'zen.yandex.ru':
    if ARGS['u'].split('/')[3] == 'id':
        channel_name = "{}/{}".format(ARGS['u'].split('/')[3], ARGS['u'].split('/')[4])
    else:
        channel_name = "{}".format(ARGS['u'].split('/')[3])
else:
    raise("Неправильная ссылка на канал")

o_format = ARGS['o']
sortby = ARGS['s']
c = Channel(channel_name)
publication_list = c.publication()
r = Report(c.name(), sortby)

header = "Название канала: {}\nОписание: {}\nПубликации: {}, Подписчики: {}, Аудитория: {}".format(c.name(), c.description(), len(c.publication()), c.subscribers(), c.audience())


def add_row(link):
    print("Сканирование публикаций {}/{}".format(r.row_count, len(publication_list)), end="\r")
    p = Post(link)
    viewed = p.viewed()
    reading = p.reading()
    r.add_row(p.date(), p.title(), 'card', p.like(), p.comment(), viewed, reading, p.reading_percentage(viewed, reading), p.time_reading(), p.hashtag())


if __name__ == '__main__':
    print("Собираем информацию о количестве публикаций на канале")
    for link in publication_list:
        # pyppeteer.errors.TimeoutError: Navigation Timeout Exceeded: 8000 ms exceeded.
        try:
            add_row(link)
        except:
            pass
    r.output(o_format, header)
