# 07. Repository Structure

## 1. Принцип

Структура должна быть простой для:
- человека,
- AI-агента,
- CI,
- локального запуска.

Не нужно перегружать репозиторий микропакетами без пользы.

## 2. Рекомендуемая структура v1

```text
/
├── AGENTS.md
├── README.md
├── docs/
│   ├── 01_PROJECT_CHARTER.md
│   ├── 02_RESEARCH_AND_DECISIONS.md
│   ├── 03_PRODUCT_REQUIREMENTS.md
│   ├── 04_ARCHITECTURE.md
│   ├── 05_DATA_AND_METRICS.md
│   ├── 06_ROADMAP.md
│   ├── 07_REPOSITORY_STRUCTURE.md
│   ├── 08_OPEN_QUESTIONS.md
│   └── 09_SOURCES.md
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── auth/  # absent or minimal stub in v1
│   │   │   ├── core/
│   │   │   ├── domain/
│   │   │   ├── models/
│   │   │   ├── providers/
│   │   │   ├── repositories/
│   │   │   ├── services/
│   │   │   ├── jobs/
│   │   │   └── metrics/
│   │   ├── migrations/
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   └── web/
│       ├── app/
│       ├── components/
│       ├── features/
│       ├── lib/
│       ├── types/
│       ├── package.json
│       └── Dockerfile
├── infra/
│   ├── docker-compose.yml
│   ├── env/
│   └── scripts/
├── scripts/
│   ├── dev/
│   └── data/
└── .github/
    └── workflows/
```

## 3. Backend layering

### `domain/`
Чистые доменные модели и правила предметной области.

### `providers/`
Адаптеры внешних источников:
- Yahoo
- later FMP
- later IBKR

### `repositories/`
Работа с БД.

### `services/`
Оркестрация use cases.

### `jobs/`
Scheduler jobs.

### `metrics/`
Изолированные функции и rule bundles для расчета метрик.

## 4. Frontend structure

### `features/`
Фичи по доменам:
- screening
- companies
- alerts
- settings

Примечание:
в v1 feature `auth` не нужна.

### `components/`
Переиспользуемые UI-компоненты.

### `lib/`
API client, utils, formatters.

## 5. Почему docs в корне репозитория важны

Потому что стратегия будет меняться.
Если документы лежат рядом с кодом:
- проще обновлять;
- AI-агенту проще держать контекст;
- архитектурные решения не теряются по чатам.

## 6. Что стоит добавить позже

Позже можно добавить:

- `adr/` для отдельных decision records;
- `playbooks/` для runbooks;
- `datasets/` для тестовых fixture-наборов;
- `examples/` для проверочных company cases.

## 7. Naming conventions

Рекомендуется:
- на уровне файлов docs - явная нумерация;
- на уровне кода - английские имена;
- domain metric codes - стабильные machine-friendly коды.

Примеры:
- `gross_margin`
- `net_margin`
- `revenue_growth_3y_class`
- `net_income_growth_10y_class`

## 8. Правило по документации

Если меняется хотя бы одно из:
- формула,
- слой архитектуры,
- provider contract,
- roadmap priority,

то вместе с кодом должен меняться соответствующий документ в `docs/`.
