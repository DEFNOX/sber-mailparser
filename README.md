### **SBER MAIL PARSER**
Программа для парсинга автоматических email сообщений от сбербанка на предмет ссылки, ее скачивания и распаковки.

-----------  
#### Функции:
- Просмотр непрочитанных сообщений в определенной папке по протоколу IMAP
- Парсинг письма от сбербанка (отправитель и регулярное выражение поиска задается в конфигурации)
- Скачивание архива с выпиской, сохранение архива и его распаковка в разные директории
- Уведомление администратора в telegram о выполнении или ошибках

#### Использование программы:
- `sber-mailparser.exe -cfg=<путь до файла config.ini>  `  
например:  
- `sber-mailparser.exe -cfg=D:\prog\sber\config.ini ` 

#### Установка  
Установка не требуется. Проект скопилирован в единый исполняемый файл

------------------------
### Файл конфигурации config.ini:
- `[mail]` - раздел настройки сервера IMAP
    - `server = mailserver.com` - адрес imap сервера
    - `user = username@mailserver.com` - имя пользователя
    - `pwd = password` - пароль
- `[program]` - настройки программы
    - `sender = sbbol@sberbank.ru` - почта, с которой сбербанк присылает отчет
    - `match_regex = .*/sbns-app/download/.*` - regex выражение для поиска совпадения в ссылке
    - `file_path = D:/Prog/sber/res/` - директория для сохранения архива
    - `extract_dir = D:/Prog/sber/extract/` - директория для сохранения распакованного файла
    - `file_prefix = WINNY_SBER` - префикс для сохраняемых файлов. напр.: `WINNY_SBER_2020-01-30.zip`
    - `target_file = kl_to_1c.txt` - имя файла в скачиваемом архиве, который надо сохранить
    - `use_proxy = False` - использовать ли настройки прокси из раздела `[proxy]` для скачивания файла
- `[proxy]` - настройки прокси для скачивания файла
    - `proxy_server = proxy.example.com` - адрес прокси сервера
    - `proxy_port = 3128` - порт прокси
    - `proxy_user = username` - имя пользователя
    - `proxy_password = password` - пароль
- `[telegram]` - настройки telegram
    - `notify_admin = True` - отправлять уведомления в telegram
    - `notify_tg = [2095785]` - пользователь или список id пользователей (список: `[123321,123321]`)
    - `notify_tg_botkey = 000000000:AAEI51H8WiNP5s-Zq-LFdfsfe_OZdbVyZY` - api ключ бота (via @botfather)
- `[other]` - прочие настройки
    - `user-agent = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36` - подставлять в заголовке агент (прикидываться браузером). можно взять по ссылке: http://www.useragentstring.com/pages/useragentstring.php?name=Chrome

### Лицензия:
Решение распростроняется по лицензии [MIT](https://github.com/DEFNOX/sber-mailparser/blob/main/LICENSE)
