# 06. Roadmap

## Принцип roadmap

Roadmap строится не по списку экранов, а по снижению рисков.

Главные риски:
1. качество и глубина данных,
2. корректность расчетов,
3. удобство развития правил,
4. только потом - красивый UI.

## Phase 0. Strategy Baseline
Статус: закрывается этим пакетом документов.

Результат:
- зафиксирована цель,
- выбран стартовый стек,
- принято решение по provider abstraction,
- зафиксированы открытые вопросы.

## Phase 1. Technical Bootstrap

Цель:
поднять каркас проекта.

Результат фазы:
- монорепозиторий создан;
- `apps/api` и `apps/web` заведены;
- локальный docker stack работает;
- PostgreSQL и миграции настроены;
- базовый healthcheck есть;
- CI запускает lint + tests.

## Phase 2. Data Layer MVP

Цель:
получать и сохранять данные.

Результат фазы:
- реализован `YahooYFinanceProvider`;
- universe scope ограничен США;
- есть ingestion runs;
- raw snapshots сохраняются;
- company + listing + annual financial tables заполняются;
- есть ручной запуск sync.

Критерий готовности:
можно загрузить ограниченный universe и увидеть данные в БД.

## Phase 3. Metrics Engine MVP

Цель:
считать стартовые метрики корректно и воспроизводимо.

Результат фазы:
- реализованы gross margin и net margin;
- реализован ROE;
- реализован PE как reference / guardrail metric;
- реализованы revenue growth 3y / 10y;
- реализованы net income growth 3y / 10y;
- есть unit tests на формулы и edge cases;
- metric versioning работает.

Критерий готовности:
по выбранной компании можно руками сверить расчет.

## Phase 4. Screening UI MVP

Цель:
дать работающий интерфейс отбора.

Результат фазы:
- таблица компаний;
- без auth flow / login pages;
- фильтры;
- сортировки;
- сохранение screen definition;
- карточка компании;
- explanation block.

Критерий готовности:
пользователь может выполнить полный цикл отбора без SQL и скриптов.

## Phase 5. Alerts MVP

Цель:
убрать ручной мониторинг.

Результат фазы:
- scheduler jobs;
- saved alerts;
- email отправка;
- deduplication;
- журнал отправок.

Критерий готовности:
новый matching candidate приводит к письму.

## Phase 6. Hardening

Цель:
сделать систему устойчивой.

Результат фазы:
- retry / backoff;
- better logging;
- admin diagnostics;
- richer data coverage status;
- fallback provider spike.

## Phase 7. Portfolio Context (Optional)

Цель:
добавить контекст относительно текущего портфеля.

Результат фазы:
- read-only IBKR sync;
- текущие holdings видны в UI;
- candidate already owned flag;
- comparison with portfolio.

## Что нельзя откладывать слишком долго

Даже если UI хочется сделать раньше, нельзя долго откладывать:

- provider abstraction;
- raw snapshot storage;
- metric versioning;
- tests на формулы.

Если их не заложить сразу, потом будет дорого переделывать.
