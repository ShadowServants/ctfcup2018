## Arlington


Сервис представлял собой обменник документами между группами и хранение документов юзера.
Документы представляли собой текст, который рендерился в PDF файл.
По документам работал полнотекстовый поиск.

Флаги в сервисе были в личных заметках пользователя и в документах групп.

Через первые 2 уязвимости можно было получить флаги только в документах. Последняя уязвимость давала доступ ко всем флагам.

Уязвимости: 

### NGINX Index

Документы групп рендерились и клались в папку `data/rendered_docs`.

В NGINX файлы отдаются так 
```
location /rendered_docs/ {
        autoindex on;
        alias /var/uploads/data/rendered_docs/;
  }
```

Строчка autoindex включает индексацию файлов, а значит можно зайти на /rendered_docs/ и получить названия всех документов.

Закрывается `autoindex off` или удалить эту строчку.

### Elastic Injection(SSRF)

По документам был реалиован полнотекстовый поиск с помощью Elastic Search.

Все документы клались в одну коллекцию, однако проверка на то, чтобы вытаскивать только документы твоей группы была реализована на стороне запроса в Elastic:

`elastic.find(f"(title:'{q}' OR text:'{q}') AND group_id:{self.group_id}",sort_by='-id')`

Если посмотреть на реализацию, можно увидеть что title и text никак не проверяются и не экранируются.
```
full_url = self._collection_url + "_search?"
if sort_by:
    full_url += "sort=" + self._sort_field(sort_by) + "&"
full_url += "q=" + query
resp = requests.get(full_url)
```
Значит, мы можем провернуть атаку вида SSRF, отрезав условие проверки на группу.
Для этого пишем запрос вида secret(все флаги заливались с таким title) + ')' + #

Скобку нужно закрыть для того, чтобы осталось валидное выражение для elastic'a.

Однако, символ # нужно представить в формате urlencode, иначе не сработает

Можно сделать это и без знания, что у всех флагов `title=secret`, вот так — `*:*`, однако это даст нам вообще все записи в базе, а поиск вернет только 10 записей.


В итоге запрос выглядит примерно как-то так:

`localhost:8888/groups/1/documents/search?q=secret)%23`

Обратите внимание, что вы должны быть залогинены и принадлежать к группе, в которой ищете, однако наш запрос даст документы всех групп.


Кстати, можно было увеличить количество отдаваемых записей, дописав еще один параметр к запросу.

Закрывается уязвимость с помощью использования нормальной библиотеки для отправки GET запросов с экранированием спец символов.

Либо можно было использовать не query string API, a JSON API Elastic Search для поиска.


### Latex RCE

**Latex** — этим все сказано. 

Документы рендерились с помощью программы pdflatex, которая конвертила latex в pdf.

Latex достаточно мощный инструмент и имеет внутри себя опцию write18, которая позволяет вызвать любую команду на сервере (RCE)

[Почитать можно здесь](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/LaTeX%20injection)

Собственно пишем вот такую строчку в latex'e
`\immediate\write18{cp data/db.sqlite3 data/rendered_docs/youwillneverguess.sqlite3}`

И потом спокойно загружаем бд по ссылке, которую знаем только мы.

Альтернативно можно было сделать `cat data/db.sqlite3 | base64encode`, но потом нужно будет прочитать pdf и декодировать base64, что сложнее.

#### Как закрыть?

В опциях запуска заменить  `--shell-escape` на `--no-shell-escape`. Это отключит RCE (нэйминг огонь, конечно)

Однако это не исправит чтение локальных файлов через \input.
Но эта уязвимость не очень страшная, так как вы не можете получить файлы с нечитаемыми символами.
Закрыть можно, просто удаляя \input из данных.

