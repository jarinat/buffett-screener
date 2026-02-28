# 05. Data and Metrics

## 1. Принцип моделирования данных

Нельзя хранить только итоговый score.
Нужно хранить:

1. сущность компании;
2. привязки к тикерам / листингам;
3. raw provider payload;
4. нормализованные финансовые ряды;
5. derived metrics;
6. результаты screen runs;
7. объяснение расчета.

## 2. Базовые сущности

## 2.1 Company
Единая сущность бизнеса.

Пример полей:
- `company_id`
- `name`
- `legal_name`
- `country`
- `region`
- `domicile_market_scope`
- `sector`
- `industry`
- `currency`
- `is_active`

## 2.2 Listing
Отдельный листинг / тикер.

Пример полей:
- `listing_id`
- `company_id`
- `ticker`
- `exchange`
- `mic`
- `currency`
- `is_primary`
- `is_active`

## 2.3 ProviderRawSnapshot
Сырой ответ провайдера.

Пример полей:
- `snapshot_id`
- `provider_name`
- `provider_entity_type`
- `provider_entity_key`
- `fetched_at`
- `payload_json`
- `http_status`
- `ingestion_run_id`

## 2.4 FinancialStatementAnnual
Нормализованные annual values.

Пример полей:
- `company_id`
- `fiscal_year`
- `revenue`
- `gross_profit`
- `net_income`
- `operating_income`
- `eps_diluted`
- `total_assets`
- `total_liabilities`
- `shareholders_equity`
- `free_cash_flow`
- `source_provider`
- `source_snapshot_id`

## 2.5 DerivedMetric
Рассчитанные метрики.

Пример полей:
- `metric_result_id`
- `company_id`
- `metric_code`
- `metric_version`
- `as_of_date`
- `value_numeric`
- `value_text`
- `status`
- `coverage_years`
- `explanation_json`

## 2.6 ScreenDefinition
Описание пользовательского экрана.

Пример полей:
- `screen_id`
- `name`
- `description`
- `definition_json`
- `is_active`

## 2.7 ScreenRun
Фиксация выполнения экрана.

Пример полей:
- `screen_run_id`
- `screen_id`
- `run_started_at`
- `run_finished_at`
- `rule_version_bundle`
- `candidate_count`

## 2.8 ScreenResult
Результаты конкретного запуска.

Пример полей:
- `screen_run_id`
- `company_id`
- `passed_hard_filters`
- `score_total`
- `rank_position`
- `explanation_json`

## 2.9 AlertRule / AlertEvent
Для оповещений.

## 3. Почему нужны raw snapshots

Потому что правила будут меняться.
Если хранить только "готовый score", то ты не сможешь:

- пересчитать метрики,
- отладить ошибку,
- понять, что именно изменил provider,
- сравнить старую и новую нормализацию.

## 4. Метрики v0

Ниже зафиксирован не "вечный Buffett", а стартовая версия проектных правил.

Методологическая пометка: v1 остается quality-first screener. При этом PE сохраняется в наборе метрик как valuation-adjacent показатель без полноценного valuation layer.

## 4.1 Gross Margin

### Формула
`gross_margin = gross_profit / revenue`

### Базовое условие v0
- pass, если `gross_margin > 0.70`

### Статусы
- `ok`
- `insufficient_data`
- `division_by_zero`

## 4.2 Net Margin

### Формула
`net_margin = net_income / revenue`

### Базовое условие v0
- pass, если `net_margin > 0.40`

### Статусы
- `ok`
- `insufficient_data`
- `division_by_zero`

## 4.3 Revenue Growth - 3Y

### Вход
Annual revenue series за минимум 4 точки времени, чтобы оценить 3-летнюю динамику.

### Базовые вычисления
- start value
- end value
- CAGR
- monotonicity / smoothness
- drawdown count

### Классификация v0
- `1` - CAGR >= 10% и серия в целом ровная, без существенных провалов
- `0` - рост есть, но ниже цели или есть краткий провал
- `-1` - роста нет, серия слабая или деградирующая

## 4.4 Revenue Growth - 10Y

Та же логика, но только при достаточном покрытии данными.

### Особое правило
Если покрытие меньше требуемого горизонта:
- не ставить автоматически `-1`,
- ставить `status = insufficient_data`.

## 4.5 Net Income Growth - 3Y / 10Y

Тот же подход, но по серии `net_income`.

### Важно
Для net income нужны дополнительные защитные правила:
- отрицательная база периода;
- переход через ноль;
- экстремальная волатильность.

Эти случаи нельзя оценивать тем же упрощенным CAGR без маркировки edge case.


## 4.6 ROE

### Формула
`roe = net_income / average_shareholders_equity`

### Базовое условие v0
- конкретный порог задается в screen definition
- в дефолтах рекомендуется держать его настраиваемым, а не захардкоженным

### Статусы
- `ok`
- `insufficient_data`
- `negative_equity`
- `division_by_zero`

### Важно
Если equity отрицательный или близок к нулю, ROE нельзя интерпретировать как нормальный quality signal без отдельной маркировки.

## 4.7 PE Ratio

### Формула
`pe_ratio = market_cap / net_income`
или эквивалентно
`pe_ratio = price_per_share / diluted_eps`

### Роль в v0
- reference metric в таблице и карточке компании;
- optional guardrail в screen definition;
- не заменяет полноценную valuation-модель.

### Статусы
- `ok`
- `insufficient_data`
- `negative_earnings`
- `division_by_zero`

### Интерпретация
Для убыточных компаний PE не считается осмысленным фильтром и должен явно маркироваться как special case.

## 5. Рекомендуемая структура metric result

Пример:

```json
{
  "metric_code": "revenue_growth_10y_class",
  "metric_version": "v0",
  "value_numeric": 1,
  "status": "ok",
  "coverage_years": 10,
  "explanation": {
    "start_revenue": 1000,
    "end_revenue": 2700,
    "cagr": 0.104,
    "dips_count": 0,
    "rule_applied": "v0"
  }
}
```

## 6. Composite scoring

Для первой версии рекомендована двухступенчатая схема:

### Step 1. Hard filters
Например:
- gross margin > threshold
- net margin > threshold
- ROE > threshold (optional)
- PE < threshold (optional guardrail)

### Step 2. Soft score
Например:
- revenue growth 3y class
- revenue growth 10y class
- net income growth 3y class
- net income growth 10y class

### Почему так
Это понятнее и проще отлаживать, чем одна большая непрозрачная формула.

## 7. Версионирование правил

Нужно версионировать минимум:

- пороги,
- формулы,
- edge-case rules,
- весовые коэффициенты,
- composite score logic.

### Пример
- `metric_version = v0`
- `screen_rule_bundle = 2026-02-initial`

## 8. Что будет добавляться дальше

С высокой вероятностью в следующие версии войдут:
- debt metrics
- retained earnings behavior
- free cash flow stability
- buyback behavior
- SG&A discipline
- interest coverage
- share dilution / reduction

Важно:
каждая новая метрика должна добавляться через ту же модель:
**raw -> normalized -> derived -> explainable result**

## 9. Важное методологическое правило

Проект не должен притворяться, что существует один "истинный Buffett score".

Правильнее строить систему как:
- набор формализованных пользовательских правил,
- вдохновленных Buffett literature,
- но явно заданных и версионируемых внутри проекта.


## 10. Fixed defaults after scope clarification

- universe scope v1: US-only;
- auth model v1: none, single-user private mode;
- notifications v1: email only;
- ROE входит в стартовый ruleset;
- PE входит в стартовый ruleset как вспомогательная valuation-adjacent метрика.
