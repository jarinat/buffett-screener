# Buffett Screener

A value investing screening tool inspired by Warren Buffett's investment philosophy.

## 🚀 Quick Start (Development)

Get the entire development environment running with a single command:

```bash
./scripts/dev/start.sh
```

This will start all services using Docker Compose. Once ready, access:

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Mailhog** (Email Testing): http://localhost:8025
- **Database**: `postgresql://postgres:postgres@localhost:5432/buffett_screener`

---

## 📋 Prerequisites

- **Docker** (20.10 or later) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (2.0 or later) - Usually included with Docker Desktop
- **Git** - For version control

Verify your installation:

```bash
docker --version
docker compose version
```

---

## 🛠️ Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd buffett-screener
```

### 2. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

The default values work for local development. For production or custom setups, edit `.env`:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=buffett_screener

# Frontend
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The API has additional configuration in `apps/api/.env.example`. Docker Compose will use sensible defaults, but you can customize:

- **Data ingestion settings** (batch size, retry attempts)
- **External providers** (Yahoo Finance timeout, rate limits)
- **Email/SMTP configuration** (already configured for Mailhog)
- **Security settings** (change `SECRET_KEY` in production!)

### 3. Start Development Environment

Use the convenience script:

```bash
./scripts/dev/start.sh
```

Or manually with Docker Compose:

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# View logs
docker compose logs -f
```

### 4. Verify Services

The startup script automatically checks service health. Manually verify:

```bash
# Check all services
docker compose ps

# Test API health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

---

## 📦 Project Structure

```
buffett-screener/
├── apps/
│   ├── api/              # FastAPI backend (Python)
│   │   ├── app/
│   │   │   ├── core/     # Configuration, settings
│   │   │   ├── api/      # API routes
│   │   │   └── main.py   # Application entry point
│   │   ├── migrations/   # Database migrations
│   │   ├── tests/        # API tests
│   │   └── Dockerfile
│   │
│   └── web/              # Next.js frontend (TypeScript + Tailwind)
│       ├── app/          # Next.js app router
│       ├── public/       # Static assets
│       └── Dockerfile
│
├── docs/                 # Project documentation (Russian)
├── scripts/
│   └── dev/             # Development scripts
│       ├── start.sh     # Start development environment
│       └── stop.sh      # Stop all services
│
├── docker-compose.yml   # Docker orchestration
├── .env.example         # Environment template
└── README.md            # This file
```

---

## 🔧 Development Workflow

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f web
```

### Stopping Services

```bash
# Using the script
./scripts/dev/stop.sh

# Or manually
docker compose down

# Stop and remove volumes (⚠️ deletes database data)
docker compose down -v
```

### Rebuilding After Changes

```bash
# Rebuild specific service
docker compose build api

# Rebuild and restart
docker compose up -d --build api
```

### Accessing Service Shells

```bash
# API container (Python)
docker compose exec api bash

# Web container (Node.js)
docker compose exec web sh

# Database (PostgreSQL)
docker compose exec db psql -U postgres -d buffett_screener
```

---

## 📧 Email Testing with Mailhog

Mailhog captures all outgoing emails in development. Access the web UI at:

**http://localhost:8025**

All emails sent by the API (alerts, notifications) will appear here instead of being delivered.

---

## 🐛 Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker info

# View detailed logs
docker compose logs

# Clean restart
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

### Port Already in Use

If ports 3000, 8000, 5432, or 8025 are already in use, either:

1. Stop the conflicting service
2. Edit `docker-compose.yml` to use different ports:
   ```yaml
   ports:
     - "3001:3000"  # Use 3001 instead of 3000
   ```

### Database Connection Issues

```bash
# Check database is healthy
docker compose ps db

# View database logs
docker compose logs db

# Verify connection from API
docker compose exec api python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

### API Not Responding

```bash
# Check API logs
docker compose logs api

# Verify health endpoint
curl -v http://localhost:8000/health

# Rebuild API
docker compose build api
docker compose up -d api
```

---

## 📚 Additional Documentation

For project background, architecture decisions, and roadmap (in Russian):

- `docs/01_PROJECT_CHARTER.md` - Project goals and principles
- `docs/02_RESEARCH_AND_DECISIONS.md` - Research findings and ADRs
- `docs/03_PRODUCT_REQUIREMENTS.md` - MVP requirements
- `docs/04_ARCHITECTURE.md` - Target architecture and tech stack
- `docs/05_DATA_AND_METRICS.md` - Data model and screening formulas
- `docs/06_ROADMAP.md` - Implementation phases
- `docs/07_REPOSITORY_STRUCTURE.md` - Repository organization
- `docs/08_OPEN_QUESTIONS.md` - Open questions
- `docs/09_SOURCES.md` - Research sources

---

---

# Стартовый пакет стратегии (Russian Project Overview)

Этот репозиторий - веб-приложение по долгосрочному инвестированию в стиле Buffett / value investing.

## Что внутри

- `AGENTS.md` - правила работы AI-агентов в репозитории
- `docs/01_PROJECT_CHARTER.md` - цель продукта, рамки и принципы
- `docs/02_RESEARCH_AND_DECISIONS.md` - результаты исследования и стартовые решения
- `docs/03_PRODUCT_REQUIREMENTS.md` - требования к MVP и ближайшим итерациям
- `docs/04_ARCHITECTURE.md` - целевая архитектура и выбранный стек
- `docs/05_DATA_AND_METRICS.md` - модель данных, формулы и версия правил отбора
- `docs/06_ROADMAP.md` - этапы реализации
- `docs/07_REPOSITORY_STRUCTURE.md` - рекомендуемая структура монорепозитория
- `docs/08_OPEN_QUESTIONS.md` - вопросы, которые нужно закрыть перед реализацией части функций
- `docs/09_SOURCES.md` - человекочитаемый список источников исследования

## Ключевая идея пакета

Приложение проектируется не как "поиск недооцененной цены на завтра", а как инструмент отбора и регулярного пересмотра качественных компаний для долгосрочного владения.

### Рабочая гипотеза v1

- пользователь один, режим private use;
- решение используется как личный исследовательский инструмент;
- сделки принимаются вручную, приложение не размещает ордера;
- первоначальный источник данных - Yahoo Finance через `yfinance`;
- архитектура сразу строится с абстракцией провайдера данных, чтобы позднее можно было перейти на более устойчивый источник без переписывания ядра;
- первая версия поддерживает скрининг, карточку компании, сохраненные экраны и оповещения;
- интеграция с Interactive Brokers откладывается до фазы read-only синхронизации портфеля.

## Как использовать этот пакет в репозитории

1. Положить файлы в корень нового репозитория.
2. Прочитать документы в порядке:
   1. `docs/01_PROJECT_CHARTER.md`
   2. `docs/02_RESEARCH_AND_DECISIONS.md`
   3. `docs/03_PRODUCT_REQUIREMENTS.md`
   4. `docs/04_ARCHITECTURE.md`
   5. `docs/05_DATA_AND_METRICS.md`
3. Зафиксировать первые ADR-решения в `docs/02_RESEARCH_AND_DECISIONS.md`.
4. Следующим шагом подготовить технический bootstrap репозитория.

## Что уже решено этим пакетом

- MVP делаем как обычное веб-приложение, без mobile-first усложнений.
- Основной backend - Python, чтобы не бороться с финансовыми расчетами и табличной обработкой.
- Сразу разделяем слои:
  - ingestion,
  - normalization,
  - metrics,
  - screening,
  - alerts,
  - UI/API.
- Бизнес-правила метрик версионируем. Это обязательно, потому что твои критерии будут расти и меняться.

## Что еще не решено

Большая часть стартовых развилок уже закрыта:

- география покрытия v1 - только США;
- авторизация в MVP не нужна, режим single-user private-only;
- канал оповещений v1 - email;
- v1 остаётся quality-first screener;
- в стартовый набор метрик добавлены ROE и PE;
- fallback provider path после Yahoo по-прежнему держим открытым, с приоритетом FMP.

## Технический bootstrap (выполнено)

✅ Монорепозиторий создан с полной структурой:
- `apps/api` - FastAPI backend с Python
- `apps/web` - Next.js frontend с TypeScript и Tailwind CSS
- `docker-compose.yml` - оркестрация всех сервисов
- PostgreSQL база данных
- Mailhog для тестирования email
- Скрипты для разработки в `scripts/dev/`
