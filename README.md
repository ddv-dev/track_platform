Инструкция по установке (Windows)
1. Клонирование репозитория
bash
git clone https://github.com/ddv-dev/track_platform.git
cd track_platform
2. Настройка базы данных PostgreSQL
Создайте базу данных и пользователя через pgAdmin или командную строку:

sql
CREATE DATABASE track_platform;
CREATE USER track_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE track_platform TO track_user;
3. Настройка бэкенда
Перейдите в папку backend, создайте виртуальное окружение и активируйте его:

bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # macOS/Linux
Установите зависимости:

bash
pip install --upgrade pip
pip install -r requirements.txt
Если файла requirements.txt нет, установите вручную:

bash
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers psycopg2-binary python-dotenv django-filter pillow drf-yasg channels channels-redis redis daphne
Создайте файл .env в папке backend со следующим содержимым (подставьте свои пароли):

env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=track_platform
DB_USER=track_user
DB_PASSWORD=strong_password
DB_HOST=localhost
DB_PORT=5432
Выполните миграции и создайте суперпользователя:

bash
python manage.py makemigrations accounts tracks chat
python manage.py migrate
python manage.py createsuperuser
Загрузите тестовые данные (опционально, но рекомендуется для демонстрации):

bash
python manage.py seed_demo
4. Запуск сервера бэкенда
Важно: Для работы WebSocket (чатов) необходимо запускать ASGI‑сервер, а не runserver. Используйте daphne:

bash
$env:DJANGO_SETTINGS_MODULE="config.settings"   # Windows PowerShell
daphne -b 0.0.0.0 -p 8000 config.asgi:application
Для Linux/macOS:

bash
export DJANGO_SETTINGS_MODULE="config.settings"
daphne -b 0.0.0.0 -p 8000 config.asgi:application
Сервер будет доступен по адресу http://localhost:8000. Админ-панель – http://localhost:8000/admin.

5. Настройка фронтенда
Откройте новый терминал, перейдите в папку frontend и установите зависимости:

bash
cd frontend
npm install
Установите дополнительные пакеты (если они не указаны в package.json):

bash
npm install axios react-router-dom react-hot-toast @tanstack/react-query @mui/material @mui/icons-material @emotion/react @emotion/styled framer-motion react-markdown react-syntax-highlighter date-fns
Создайте файл .env в папке frontend:

env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
Запустите фронтенд:

bash
npm run dev
Фронтенд будет доступен по адресу http://localhost:3000.