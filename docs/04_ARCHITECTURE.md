# 04. Architecture

## 1. Архитектурный принцип

Проект строится как **screening platform with pluggable data providers**, а не как thin UI над Yahoo Finance.

## 2. Целевой стек

## 2.1 Backend

- Python 3.x
- FastAPI
- SQLAlchemy / SQLModel style ORM layer
- PostgreSQL
- Alembic migrations
- APScheduler for recurring jobs
- Pandas / numerical utilities for metrics calculations
- Pydantic for contracts and settings

## 2.2 Frontend

- Next.js
- TypeScript
- Tailwind CSS
- data grid / table toolkit
- charting library for financial series

## 2.3 Infra

- Docker / Docker Compose for local development
- environment-based config
- CI for lint + tests + migrations sanity
- later: container deployment to VPS / cloud

## 2.4 Notifications

- Email provider API
- alert event log in DB
- deduplication before send

## 3. High-level modules

## 3.1 Provider adapters
Назначение:
- общаться с внешними источниками данных;
- возвращать унифицированные модели.

Интерфейсы:
- `CompanyUniverseProvider`
- `FundamentalsProvider`
- `PriceHistoryProvider`
- `PortfolioSyncProvider` (future)

Стартовые реализации:
- `YahooYFinanceProvider`
- later: `FmpProvider`, `AlphaVantageProvider`, `IbkrPortfolioProvider`

## 3.2 Ingestion pipeline
Назначение:
- запускать обновление данных;
- сохранять raw payload;
- нормализовывать сущности;
- логировать статус.

Шаги:
1. выбрать scope universe;
2. запросить provider;
3. сохранить raw response;
4. преобразовать в canonical model;
5. обновить normalized tables;
6. зафиксировать ingestion run.

## 3.3 Metrics engine
Назначение:
- вычислять производные метрики на основе normalized series;
- работать по versioned rule definitions;
- возвращать значения, статусы и explanation fragments.

## 3.4 Screening engine
Назначение:
- применять hard filters;
- рассчитывать composite score;
- выдавать ranked list;
- сохранять snapshot результата.

## 3.5 Alert engine
Назначение:
- запускать saved screens по расписанию;
- сравнивать новый результат с предыдущим;
- формировать alert events;
- отправлять уведомления.

## 3.6 API layer
Назначение:
- обслуживать frontend;
- отдавать screens, companies, metrics, alert history.

## 3.7 Web UI
Главные экраны:
- screening table
- saved screens
- company detail
- alerts
- settings
- без страницы логина в MVP

## 4. Data flow

### Flow A. Обновление universe / fundamentals

1. Scheduler запускает ingestion job для universe США
2. Provider adapter получает данные
3. Raw payload сохраняется в raw store / raw tables
4. Нормализация приводит данные к canonical schema
5. Metrics engine пересчитывает нужные derived metrics
6. Screening engine при необходимости обновляет materialized view / cached result
7. Alert engine проверяет saved rules

### Flow B. Пользователь открывает saved screen

1. Frontend вызывает API
2. API получает definition screen
3. Screening engine строит query / score
4. Возвращается ranked list + explanation summary

## 5. Почему не monolith на одном фронтенд-фреймворке

Можно было бы сделать все на одном full-stack JS-стеке.
Но у проекта:
- тяжелая доменная логика расчетов;
- табличные финансовые данные;
- batch jobs;
- evolving metrics engine.

Поэтому Python backend дает лучшее соотношение:
- скорость разработки;
- ясность доменной логики;
- простота тестирования расчетов.

## 6. Почему не только FastAPI BackgroundTasks

BackgroundTasks в FastAPI хороши для "сделай что-то после ответа".
Но твоя задача - именно **регулярные периодические пересчеты**, а не пост-обработка HTTP запроса.

Поэтому стартовое решение:
- APScheduler для расписаний;
- job state в БД;
- idempotent jobs.

## 7. Почему пока без брокерской интеграции

Текущая ценность продукта - selection and review.
Не execution.

Добавление торгового контура:
- резко повышает сложность,
- затрагивает безопасность,
- меняет рисковый профиль проекта.

Поэтому:
- phase 1 = research only
- phase 2 = optional read-only portfolio sync
- trading integration = только после отдельного решения

## 8. Рекомендуемая модель деплоя

### Local dev
- Docker Compose
- `web`, `api`, `db`
- optional `mailhog` or local email emulator
- без отдельного auth service

### First production
- 1 VPS / 1 container host
- reverse proxy
- Next.js app
- FastAPI app
- managed PostgreSQL or dedicated DB container
- scheduled jobs inside api process or dedicated scheduler process

### Когда выносить scheduler отдельно
Когда:
- jobs становятся тяжелыми,
- нужно контролировать retries / concurrency отдельно,
- появляется multi-user нагрузка.

## 9. Observability

Сразу заложить:
- structured logging;
- ingestion run logs;
- metric calculation errors;
- alert send logs;
- health endpoint.

## 10. Security baseline

Даже для personal-use:
- секреты только через env;
- не хранить ключи в репозитории;
- раздельные env для dev / prod;
- read-only доступы там, где возможно;
- IBKR integration - только отдельным секретным конфигом и не в MVP.

## 11. Architectural north star

Архитектура должна позволять ответить на вопрос:

**"Если завтра Yahoo перестанет устраивать, сможем ли мы перейти на другой provider без переписывания screen logic?"**

Если ответ "нет", архитектура выбрана неправильно.


## 12. Scope-specific constraints for v1

- universe ingestion ограничен США;
- multi-user abstractions не требуются;
- auth middleware не является обязательной частью MVP;
- email - единственный канал alerts в первой версии;
- PE поддерживается в data model и screening rules, но отдельный valuation engine отсутствует.
