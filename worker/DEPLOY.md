# Живой отсчёт до Нового года (Cloudflare Workers)

Файл `countdown.js` — это маленький сервис, который отдаёт SVG с оставшимся временем:
дни, часы, минуты, секунды. Секунды тикают сами, JavaScript внутри картинки не нужен.

## Деплой (бесплатно, ~10 минут)

1. Зарегистрируйся на https://dash.cloudflare.com (бесплатный аккаунт).
2. Открой **Workers & Pages** → **Create** → **Start with Hello World!**
3. Назови сервис, например `newyear`, и нажми **Deploy**.
4. Нажми **Edit code**, удали весь код в `worker.js`, вставь содержимое файла `countdown.js`
   и нажми **Deploy**.
5. Скопируй адрес вида `https://newyear.ТВОЁ-ИМЯ.workers.dev` и открой его в браузере:
   должна появиться карточка. Проверь также `?theme=light`.

Названия кнопок в Cloudflare иногда меняются, но порядок остаётся таким же.

Через консоль (если уже стоит Node.js):
```
npx wrangler deploy countdown.js --name newyear --compatibility-date 2024-01-01
```

## Подключение к README

Замени в `README.md` блок с картинкой `festive-dark.svg` / `festive-light.svg` на это
(подставь свой адрес вместо `ТВОЁ-ИМЯ`):

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://newyear.ТВОЁ-ИМЯ.workers.dev/?theme=dark">
  <source media="(prefers-color-scheme: light)" srcset="https://newyear.ТВОЁ-ИМЯ.workers.dev/?theme=light">
  <img src="https://newyear.ТВОЁ-ИМЯ.workers.dev/?theme=dark" alt="New Year countdown">
</picture>
```

## Параметры адреса

| Параметр | Значение | По умолчанию |
|----------|----------|--------------|
| `theme`  | `dark` или `light` | `dark` |
| `to`     | год, до которого считать, например `2028` | следующий год |
| `tz`     | часовой пояс в часах от UTC | `5` (Ташкент) |

## Важно знать

- Отсчёт считается от момента загрузки картинки. Если GitHub покажет закэшированную копию,
  время на карточке отстанет на возраст кэша. Сервис отдаёт заголовки `no-cache`,
  поэтому обычно это не проблема, но полностью исключить задержку нельзя.
- Бесплатный тариф Cloudflare — 100 000 запросов в сутки, для личного профиля этого с запасом.
- С 1 по 15 января карточка показывает «HAPPY NEW YEAR!» с конфетти, потом считает до следующего года.
  После праздников блок можно просто убрать из README.
