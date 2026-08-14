# stripe_test

Учебный проект: пример онлайн-магазина с оплатой через [Stripe](https://stripe.com).

## Структура

```
config/       Конфигурация Django (settings.py, test_settings.py)
payments/     Backend на Django 6 + psycopg2 (PostgreSQL)
  domain/          Доменные сущности, репозитории, сервисы (DDD)
  application/     Use cases (корзина, заказ, checkout, webhook)
  infrastructure/  Django models + Stripe gateway
  representation/  REST-эндпоинты (views, urls)
  tests/           Юнит-тесты: domain / application / infrastructure / presentation
frontend/     SPA на React + Vite, платёжная форма Stripe (react-stripe-js)
```

## Возможности

- Каталог товаров, корзина, оформление заказа, покупка в один клик
- Платёжный flow через Stripe PaymentIntent + обработка webhook
- Курсы валют, налоги, скидки

## API (кратко)

| Метод | URL | Описание |
|---|---|---|
| GET | `/api/products/` | Список товаров |
| GET | `/api/cart/` | Получить/создать активную корзину |
| POST | `/api/cart/add/` | Добавить товар в корзину |
| POST | `/api/cart/checkout/` | Checkout корзины |
| GET | `/api/orders/` | Список заказов |
| POST | `/api/buy-in-one-click/` | Покупка в один клик |
| POST | `/webhook/stripe/` | Webhook от Stripe |

## Требования

- Python 3.14
- Node.js 22 (для frontend)
- Docker + Docker Compose (PostgreSQL 16)

## Установка и запуск

1. Скопируйте `.env.example` в `.env` и впишите свои Stripe-ключи:
   ```
   cp .env.example .env
   ```
   Тестовые ключи можно получить в дашборде Stripe (режим Test mode).

2. Запустите стек через Docker Compose (PostgreSQL, API, frontend):
   ```
   docker compose up --build
   ```
   - API: http://localhost:8000
   - Frontend: http://localhost:5173

   Для локального запуска без Docker:
   ```
   python -m venv .venv && source .venv/bin/activate
   pip install -r req.txt -r req-dev.txt
   python manage.py migrate
   python manage.py runserver
   ```

## Webhook

Для локального приёма webhook'ов Stripe используйте Stripe CLI:
```
stripe listen --forward-to localhost:8000/webhook/stripe/
```
`STRIPE_WEBHOOK_SECRET` из вывода команды нужно подставить в `.env`.

## Тесты

Запуск требует тестовую PostgreSQL на `127.0.0.1:5434` (поднимается через `docker compose up -d db-test`).

```
pytest
```

### Качество кода

```
ruff check .
ruff format --check .
mypy payments config
pre-commit run --all-files
```

CI (`.github/workflows/ci.yml`) выполняет lint, type check и тесты на каждую ветку `main`/`dev` и PR.