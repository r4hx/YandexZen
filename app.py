import argparse

from function import Channel, Post, Report

PARSER = argparse.ArgumentParser(description='Yandex.Zen analatycs channel analytics utility')
PARSER.add_argument('-u', help='channel url', required=True)
PARSER.add_argument('-o', help='output format [asci, html]. default: asci', default='asci')
PARSER.add_argument('-s', help='sortby [er, likes, comments, views, reads]. default: er', default='er')
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
print("Собираем информацию о количестве публикаций на канале")
publication_list = c.publication()
r = Report(c.name(), sortby)

header = "Название канала: {}\nОписание: {}\nПубликации: {}, Подписчики: {}, Аудитория: {}".format(c.name(), c.description(), len(c.publication()), c.subscribers(), c.audience())


def add_row(link):
    print("Сканирование публикаций {}/{}".format(r.row_count, len(publication_list)), end="\r")
    p = Post(link)
    date = p.date()
    title = p.title()
    post_type = 'card'
    like = p.like()
    comment = p.comment()
    viewed = p.viewed()
    reading = p.reading()
    reading_percentage = p.reading_percentage(viewed, reading)
    reading_time = p.time_reading()
    hashtag = p.hashtag()
    engagement_rate = p.engagement_rate(like, comment, viewed)
    r.add_row(
        date, title, post_type, engagement_rate,
        like, comment, viewed, reading,
        reading_percentage, reading_time, hashtag
    )


if __name__ == '__main__':
    for link in publication_list:
        add_row(link)
    r.output(o_format, header)
