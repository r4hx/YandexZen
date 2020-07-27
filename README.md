# Аналитика блогов Яндекс Дзен.
Инструмент для анализа блогов и статей в системе рекомендовательного контента Яндекс Дзен.

## Установка
В первую очередь необходимо склонировать репозиторий
```
git clone https://github.com/r4hx/YandexZen.git
```
Устанавливаем зависимостри проекта
```
pip install -r requirements.txt
```

## Использование
Чтобы запустить приложение достаточно указать единственный параметр с ссылкой на анализируемый блог
```
python3 app.py -u https://zen.yandex.ru/python
```
После выполнения программы в ваш stdout будет отображен результат работы

### Сортировка данных в таблице
По умолчанию программа сортирует данные по столбцу ER. Это универсальный показатель вовлеченности в статью рассчитаный по формуле:
```python
round((num_like + num_comment) / num_viewed * 100, 2)
```
> num_like - количество лайков на публикации

> num_comment - количество комментариев

> num_viewed - количество просмотров

Выбрать столбец сортировки можно с помощью указания аргумента ***-s*** при запуске приложения.
```
python3 app.py -u https://zen.yandex.ru/python -s likes
```
В этом примере таблица с отчетом будет отсортирована по столбцу "Лайки"

Доступные значения сортировки

1. ***er*** - сортировка по универсальному параметру
2. ***likes*** - сортировка по количеству лайков
3. ***comments*** - сортировка по количеству комментариев
4. ***views*** - сортировка по количеству просмотров
5. ***reads*** - сортировка по количеству дочитываний

### Формат вывода данных
По умолчанию вывод данных происходит в stdout. Генерируюется читаемая ASCII таблица. Но так же существует способ писать в html.
Для этого необходимо запустить программу с ключем ***-o***
```
python3 app.py -u https://zen.yandex.ru/python -o html
```

Все доступные параметры приложения можно узнать запустив програму с ключем ***--help***