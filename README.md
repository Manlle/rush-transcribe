# Rush Transcribe Server

Бесплатный сервер расшифровки голоса для Rush (faster-whisper, без ключей).

## Что это
Принимает аудиофайл, прогоняет через Whisper прямо на сервере, возвращает текст.
Никаких API-ключей. Приложение Rush шлёт сюда голосовые/кружки и получает расшифровку.

## Файлы
- `app.py` — сервер (FastAPI + faster-whisper)
- `requirements.txt` — зависимости Python
- `render.yaml` — конфиг для деплоя на Render

## Деплой на Render (бесплатно) — по шагам

### 1. Создай GitHub-репозиторий
1. Зайди на https://github.com → войди/зарегистрируйся.
2. Нажми зелёную кнопку **New** (или https://github.com/new).
3. Repository name: `rush-transcribe` → **Create repository**.
4. Загрузи в него эти три файла (`app.py`, `requirements.txt`, `render.yaml`):
   - Проще всего: на странице репозитория → **Add file** → **Upload files** → перетащи три файла → **Commit changes**.

### 2. Подключи Render
1. Зайди на https://render.com → **Get Started** → войди через GitHub (кнопка "GitHub").
2. На дашборде нажми **New +** → **Web Service**.
3. Выбери **Build and deploy from a Git repository** → **Next**.
4. Найди репозиторий `rush-transcribe` → **Connect**.
5. Render подхватит `render.yaml` автоматически. Если спросит вручную:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** **Free**
6. Нажми **Create Web Service**.

### 3. Дождись сборки
- Первая сборка идёт ~5-10 минут (скачивает Whisper и зависимости).
- В логах увидишь `[startup] model loaded, server ready`.
- Вверху страницы будет URL вида `https://rush-transcribe.onrender.com` — **скопируй его**, он понадобится в приложении.

### 4. Проверь, что работает
Открой `https://rush-transcribe.onrender.com/` в браузере — должно вернуть:
```json
{"ok": true, "model": "small"}
```

## Важные особенности бесплатного тарифа Render
- **Сервис засыпает** после 15 минут без запросов. Первый запрос после сна будит его (~30-60 сек), потом работает быстро. В приложении это выглядит как "первая расшифровка думает дольше".
- **Лимит RAM 512 МБ.** Модель `small` (int8) влезает. Если будет падать по памяти — поменяй в Render → Environment → `WHISPER_MODEL` на `base` или `tiny` (быстрее и легче, но чуть менее точно).
- Скорость на free CPU: расшифровка 30-секундного голосового ≈ 5-15 секунд.

## Альтернативные хостинги
Если Render не подойдёт — тот же код работает на Railway, Fly.io, HuggingFace Spaces.
Главное: команда запуска `uvicorn app:app --host 0.0.0.0 --port $PORT`.

## Локальный тест (опционально, на твоём ПК)
```
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
Открой http://localhost:8000/ — должно вернуть `{"ok": true, ...}`.
