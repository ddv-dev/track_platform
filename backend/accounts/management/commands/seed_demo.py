import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProgress
from tracks.models import (
    Direction,
    Track,
    Guide,
    Checklist,
    ChecklistItem,
    Task,
    TaskOption,
)
from chat.models import ChatRoom, ChatMessage

User = get_user_model()


class Command(BaseCommand):
    help = "Расширенное заполнение БД тестовыми данными (25 треков, много пользователей, контент, прогресс, чаты)"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Начинаем расширенное заполнение БД...")

        self.clean_data()
        self.create_directions_and_tracks()
        self.create_users()
        self.assign_curators_to_tracks()
        self.create_educational_content()
        self.create_progress()
        self.create_chats()

        self.stdout.write(
            self.style.SUCCESS("✅ База данных успешно заполнена расширенными данными!")
        )

    def clean_data(self):
        self.stdout.write("Очистка старых данных...")
        ChatMessage.objects.all().delete()
        ChatRoom.objects.all().delete()
        UserProgress.objects.all().delete()
        TaskOption.objects.all().delete()
        Task.objects.all().delete()
        ChecklistItem.objects.all().delete()
        Checklist.objects.all().delete()
        Guide.objects.all().delete()
        Track.objects.all().delete()
        Direction.objects.all().delete()
        User.objects.exclude(is_superuser=True).delete()
        self.stdout.write("Очистка завершена.")

    def create_directions_and_tracks(self):
        self.stdout.write("Создание направлений и 25 треков...")

        directions_data = {
            "business": {
                "code": "38.03.05",
                "name": "Бизнес-информатика",
                "description": "IT-менеджмент и бизнес-аналитика",
            },
            "comp_eng": {
                "code": "09.03.01",
                "name": "Информатика и вычислительная техника",
                "description": "Разработка ПО и вычислительных систем",
            },
            "inf_sys": {
                "code": "09.03.02",
                "name": "Информационные системы и технологии",
                "description": "Проектирование информационных систем",
            },
            "app_inf": {
                "code": "09.03.03",
                "name": "Прикладная информатика",
                "description": "IT в различных предметных областях",
            },
            "app_math": {
                "code": "01.03.04",
                "name": "Прикладная математика",
                "description": "Математическое моделирование и алгоритмы",
            },
        }
        directions = {}
        for key, d in directions_data.items():
            dir_obj = Direction.objects.create(**d)
            directions[key] = dir_obj

        tracks_list = [
            # Бизнес-информатика (6)
            {
                "direction": directions["business"],
                "name": "Управление IT-проектами",
                "short_description": "Agile, Scrum, управление командами",
                "full_description": "Полное описание трека...",
                "career_paths": "Project Manager → Program Manager → CIO",
                "skills": "Agile, Scrum, Jira, Confluence, бюджетирование",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["business"],
                "name": "Аналитика в RPA",
                "short_description": "Роботизированная автоматизация процессов",
                "full_description": "...",
                "career_paths": "RPA-аналитик → RPA-разработчик",
                "skills": "RPA, UiPath, BPMN",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["business"],
                "name": "Бизнес-аналитика",
                "short_description": "Анализ бизнес-процессов и внедрение IT-решений",
                "full_description": "...",
                "career_paths": "BA → Senior BA → Product Owner",
                "skills": "BPMN, SQL, требования",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["business"],
                "name": "Бизнес в цифровой экономике",
                "short_description": "Цифровая трансформация бизнеса",
                "full_description": "...",
                "career_paths": "Digital-стратег → CEO стартапа",
                "skills": "Маркетинг, e-commerce, аналитика",
                "duration": "2 года",
                "order": 4,
            },
            {
                "direction": directions["business"],
                "name": "Искусственный интеллект в финансовых технологиях (Финтех)",
                "short_description": "AI и ML для финансовой сферы",
                "full_description": "...",
                "career_paths": "Data Scientist (Fintech) → ML Engineer",
                "skills": "Python, pandas, scikit-learn",
                "duration": "2 года",
                "order": 5,
            },
            {
                "direction": directions["business"],
                "name": "Проектирование и внедрение бизнес-решений 1С",
                "short_description": "Разработка на платформе 1С",
                "full_description": "...",
                "career_paths": "1С-разработчик → Архитектор 1С",
                "skills": "1С:Предприятие, запросы",
                "duration": "2 года",
                "order": 6,
            },
            # Информатика и вычислительная техника (6)
            {
                "direction": directions["comp_eng"],
                "name": "Системная и программная инженерия",
                "short_description": "Разработка сложных систем",
                "full_description": "...",
                "career_paths": "Software Engineer → Architect → CTO",
                "skills": "Java, C++, архитектура, Docker",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Интеллектуальный анализ данных в цифровой экономике",
                "short_description": "Data Mining и Big Data",
                "full_description": "...",
                "career_paths": "Data Analyst → Data Scientist",
                "skills": "Python, SQL, Hadoop, Spark",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Интернет вещей",
                "short_description": "Разработка IoT-систем",
                "full_description": "...",
                "career_paths": "IoT Developer → Architect",
                "skills": "C, Python, MQTT, LoRaWAN",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Предиктивная аналитика и управление в социально-экономических системах",
                "short_description": "Прогнозирование и оптимизация",
                "full_description": "...",
                "career_paths": "Аналитик → Руководитель аналитического отдела",
                "skills": "Эконометрика, временные ряды, Python, R",
                "duration": "2 года",
                "order": 4,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Управление цифровыми продуктами",
                "short_description": "Product Management в IT",
                "full_description": "...",
                "career_paths": "Product Owner → Product Manager → Head of Product",
                "skills": "Agile, Scrum, OKR, маркетинг",
                "duration": "2 года",
                "order": 5,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Интеллектуальные системы анализа данных",
                "short_description": "Продвинутый анализ данных и нейросети",
                "full_description": "...",
                "career_paths": "ML Engineer → AI Researcher",
                "skills": "Python, PyTorch, OpenCV, NLP",
                "duration": "2 года",
                "order": 6,
            },
            # Информационные системы и технологии (4)
            {
                "direction": directions["inf_sys"],
                "name": "Программное обеспечение корпоративных информационных систем",
                "short_description": "Разработка ERP/CRM",
                "full_description": "...",
                "career_paths": "Backend Developer → Lead",
                "skills": "Java, .NET, SQL, микросервисы",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["inf_sys"],
                "name": "Интеллектуальные встраиваемые системы",
                "short_description": "Embedded AI и умные устройства",
                "full_description": "...",
                "career_paths": "Embedded Engineer → Firmware Architect",
                "skills": "C/C++, RTOS, TinyML",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["inf_sys"],
                "name": "Техническое обеспечение интеллектуальных информационных систем",
                "short_description": "Аппаратная поддержка ИИ-систем",
                "full_description": "...",
                "career_paths": "DevOps Engineer → Cloud Architect",
                "skills": "Linux, Kubernetes, GPU, облака",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["inf_sys"],
                "name": "Технологии разработки и сопровождения интеллектуальных информационных систем",
                "short_description": "MLOps и сопровождение моделей",
                "full_description": "...",
                "career_paths": "MLOps Engineer → Data Platform Architect",
                "skills": "Python, Docker, MLflow, CI/CD",
                "duration": "2 года",
                "order": 4,
            },
            # Прикладная информатика (5)
            {
                "direction": directions["app_inf"],
                "name": "Графический дизайн и 3D-дизайн",
                "short_description": "Дизайн интерфейсов, графика, 3D-моделирование",
                "full_description": "...",
                "career_paths": "UI/UX Designer → Art Director",
                "skills": "Figma, Adobe, Blender",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["app_inf"],
                "name": "Разработка мобильных и веб-приложений",
                "short_description": "React, React Native, Node.js",
                "full_description": "...",
                "career_paths": "Frontend → Fullstack → Tech Lead",
                "skills": "JavaScript, React, Node.js",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["app_inf"],
                "name": "BIM-технологии, IT-решения в архитектуре и строительстве",
                "short_description": "Информационное моделирование зданий",
                "full_description": "...",
                "career_paths": "BIM-менеджер → Digital Transformation Lead",
                "skills": "Revit, Dynamo, Python, IFC",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["app_inf"],
                "name": "Системная аналитика",
                "short_description": "Анализ и проектирование сложных систем",
                "full_description": "...",
                "career_paths": "System Analyst → Enterprise Architect",
                "skills": "UML, BPMN, SQL, архитектура",
                "duration": "2 года",
                "order": 4,
            },
            {
                "direction": directions["app_inf"],
                "name": "Промдизайн и инжиниринг",
                "short_description": "Промышленный дизайн и инженерная подготовка",
                "full_description": "...",
                "career_paths": "Industrial Designer → Product Design Manager",
                "skills": "CAD, 3D-печать, прототипирование",
                "duration": "2 года",
                "order": 5,
            },
            # Прикладная математика (4)
            {
                "direction": directions["app_math"],
                "name": "Алгоритмы и методы наукоемкого программного обеспечения",
                "short_description": "Сложные алгоритмы для научных задач",
                "full_description": "...",
                "career_paths": "Algorithm Engineer → Research Scientist",
                "skills": "C++, Python, MPI, CUDA",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["app_math"],
                "name": "Робототехника и киберфизические системы",
                "short_description": "Разработка роботов и управляющих систем",
                "full_description": "...",
                "career_paths": "Robotics Engineer → R&D Manager",
                "skills": "C++, ROS, Python, компьютерное зрение",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["app_math"],
                "name": "Прикладная математика в интеллектуальных системах",
                "short_description": "Математические основы ИИ",
                "full_description": "...",
                "career_paths": "Data Scientist → Research Scientist",
                "skills": "Математика, статистика, ML",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["app_math"],
                "name": "Искусственный интеллект и робототехника",
                "short_description": "Интеграция ИИ в робототехнические системы",
                "full_description": "...",
                "career_paths": "AI Robotics Engineer → CTO",
                "skills": "Python, C++, ROS, PyTorch",
                "duration": "2 года",
                "order": 4,
            },
        ]

        self.tracks = []
        for t in tracks_list:
            track = Track.objects.create(
                direction=t["direction"],
                name=t["name"],
                short_description=t["short_description"],
                full_description=t["full_description"],
                career_paths=t["career_paths"],
                skills=t["skills"],
                duration=t["duration"],
                is_active=True,
                order=t["order"],
            )
            self.tracks.append(track)

        self.stdout.write(f"✅ Создано 5 направлений и {len(self.tracks)} треков.")

    def create_users(self):
        self.stdout.write("Создание пользователей...")
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123",
                role="admin",
            )
        # Кураторы (5)
        curators = []
        curator_names = ["Анна", "Дмитрий", "Елена", "Сергей", "Мария"]
        for i, name in enumerate(curator_names, 1):
            curator = User.objects.create_user(
                username=f"curator_{name.lower()}",
                email=f"curator_{i}@example.com",
                password="curator123",
                first_name=name,
                last_name="Кураторская",
                role="curator",
            )
            curators.append(curator)
        # Студенты (30)
        students = []
        first_names = [
            "Алексей",
            "Владимир",
            "Дмитрий",
            "Иван",
            "Михаил",
            "Николай",
            "Павел",
            "Роман",
            "Сергей",
            "Фёдор",
            "Анна",
            "Елена",
            "Мария",
            "Ольга",
            "Татьяна",
        ]
        last_names = [
            "Иванов",
            "Петров",
            "Сидоров",
            "Кузнецов",
            "Смирнов",
            "Попов",
            "Васильев",
            "Соколов",
            "Михайлов",
            "Новиков",
        ]
        for i in range(1, 31):
            first = random.choice(first_names)
            last = random.choice(last_names)
            username = f"{first.lower()}_{last.lower()}_{i}"
            student = User.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password="student123",
                first_name=first,
                last_name=last,
                role="student",
            )
            students.append(student)
        self.curators = curators
        self.students = students
        self.stdout.write(
            f"✅ Создано: {len(curators)} кураторов, {len(students)} студентов."
        )

    def assign_curators_to_tracks(self):
        self.track_curator_map = {}
        for idx, track in enumerate(self.tracks):
            curator = self.curators[idx % len(self.curators)]
            self.track_curator_map[track.id] = curator
        self.stdout.write("✅ Кураторы закреплены за треками.")

    def create_educational_content(self):
        self.stdout.write("Создание учебного контента (гайды, чек-листы, задания)...")
        for track in self.tracks:
            # Гайды (3-5)
            num_guides = random.randint(3, 5)
            for i in range(1, num_guides + 1):
                Guide.objects.create(
                    track=track,
                    title=f"Гайд {i}: {self._random_guide_title(track.name)}",
                    content=f'Содержание гайда {i} по треку "{track.name}".',
                    order=i,
                )
            # Чек-лист
            checklist = Checklist.objects.create(
                track=track, title="Чек-лист для успешного старта", order=1
            )
            checklist_items = [
                "Ознакомиться с программой трека",
                "Зарегистрироваться на все необходимые курсы",
                "Настроить рабочее окружение",
                "Познакомиться с куратором",
                "Выполнить первое вводное задание",
                "Изучить дополнительные материалы",
                "Принять участие в вебинаре",
                "Заполнить анкету обратной связи",
            ]
            selected_items = random.sample(checklist_items, k=random.randint(5, 7))
            for idx, text in enumerate(selected_items, 1):
                ChecklistItem.objects.create(checklist=checklist, text=text, order=idx)
            # Задания
            self._create_tasks_for_track(track)
        self.stdout.write("✅ Учебный контент создан.")

    def _create_tasks_for_track(self, track):
        tasks_data = self._get_tasks_by_track_name(track.name)
        for j, task_info in enumerate(tasks_data, 1):
            task = Task.objects.create(
                track=track,
                title=task_info["title"],
                description=task_info["description"],
                task_type=task_info["task_type"],
                category=task_info.get("category", "theory"),
                correct_answer=task_info["correct_answer"],
                points=task_info["points"],
                order=j,
                is_auto_check=task_info["task_type"] in ("single", "multiple"),
            )
            if (
                task_info["task_type"] in ("single", "multiple")
                and "options" in task_info
            ):
                for opt_text, is_correct in task_info["options"]:
                    TaskOption.objects.create(
                        task=task, text=opt_text, is_correct=is_correct
                    )

    def _get_tasks_by_track_name(self, track_name):
        # Управление IT-проектами
        if "Управление IT-проектами" in track_name:
            return [
                {
                    "title": "Что такое Scrum?",
                    "category": "theory",
                    "description": "Выберите правильное определение Scrum.",
                    "task_type": "single",
                    "correct_answer": "Гибкая методология управления проектами",
                    "points": 10,
                    "options": [
                        ("Методология жёсткого планирования", False),
                        ("Гибкая методология управления проектами", True),
                        ("Система контроля версий", False),
                    ],
                },
                {
                    "title": "Роль Product Owner",
                    "category": "theory",
                    "description": "Какова основная ответственность Product Owner в Scrum?",
                    "task_type": "single",
                    "correct_answer": "Управление бэклогом продукта",
                    "points": 10,
                    "options": [
                        ("Управление командой", False),
                        ("Управление бэклогом продукта", True),
                        ("Контроль качества", False),
                    ],
                },
                {
                    "title": "Артефакты Scrum",
                    "category": "theory",
                    "description": "Какие из перечисленного являются артефактами Scrum?",
                    "task_type": "multiple",
                    "correct_answer": "Бэклог продукта, бэклог спринта, инкремент",
                    "points": 20,
                    "options": [
                        ("Бэклог продукта", True),
                        ("Бэклог спринта", True),
                        ("Инкремент", True),
                        ("Диаграмма Ганта", False),
                    ],
                },
                {
                    "title": "Составьте план спринта",
                    "category": "practice",
                    "description": "Опишите шаги планирования двухнедельного спринта.",
                    "task_type": "text",
                    "correct_answer": "1. Выбор задач из бэклога 2. Оценка сложности 3. Формирование цели спринта 4. Распределение задач",
                    "points": 25,
                },
            ]
        # Бизнес-аналитика
        elif "Бизнес-аналитика" in track_name:
            return [
                {
                    "title": "Что такое BPMN?",
                    "category": "theory",
                    "description": "Для чего используется нотация BPMN?",
                    "task_type": "single",
                    "correct_answer": "Моделирование бизнес-процессов",
                    "points": 10,
                    "options": [
                        ("Моделирование баз данных", False),
                        ("Моделирование бизнес-процессов", True),
                        ("Управление проектами", False),
                    ],
                },
                {
                    "title": "Требования к ПО",
                    "category": "theory",
                    "description": "Какие виды требований бывают?",
                    "task_type": "single",
                    "correct_answer": "Функциональные и нефункциональные",
                    "points": 10,
                    "options": [
                        ("Только функциональные", False),
                        ("Функциональные и нефункциональные", True),
                        ("Только нефункциональные", False),
                    ],
                },
                {
                    "title": "Создание диаграммы процесса",
                    "category": "practice",
                    "description": "Опишите процесс согласования заявки в виде текстовой диаграммы BPMN.",
                    "task_type": "text",
                    "correct_answer": "Заявка → Проверка руководителем → Принятие решения → Уведомление",
                    "points": 20,
                },
            ]
        # Разработка мобильных и веб-приложений
        elif "Разработка мобильных и веб-приложений" in track_name:
            return [
                {
                    "title": "Что такое React?",
                    "category": "theory",
                    "description": "React – это...",
                    "task_type": "single",
                    "correct_answer": "Библиотека для UI",
                    "points": 10,
                    "options": [
                        ("Фреймворк", False),
                        ("Библиотека для UI", True),
                        ("Язык программирования", False),
                    ],
                },
                {
                    "title": "React Hook useState",
                    "category": "theory",
                    "description": "Для чего используется useState?",
                    "task_type": "single",
                    "correct_answer": "Управление состоянием компонента",
                    "points": 10,
                    "options": [
                        ("Управление состоянием компонента", True),
                        ("Работа с API", False),
                        ("Стилизация", False),
                    ],
                },
                {
                    "title": "Напишите компонент на React",
                    "category": "practice",
                    "description": 'Создайте функциональный компонент, который выводит "Hello, World!"',
                    "task_type": "code",
                    "correct_answer": "function Hello() { return <div>Hello, World!</div>; }",
                    "points": 30,
                },
            ]
        # Искусственный интеллект в Финтехе
        elif "Искусственный интеллект в финансовых технологиях" in track_name:
            return [
                {
                    "title": "Что такое скоринг?",
                    "category": "theory",
                    "description": "Что оценивается с помощью скоринговых моделей?",
                    "task_type": "single",
                    "correct_answer": "Кредитоспособность клиента",
                    "points": 10,
                    "options": [
                        ("Кредитоспособность клиента", True),
                        ("Курс валют", False),
                        ("Рыночный спрос", False),
                    ],
                },
                {
                    "title": "Применение ML в финтехе",
                    "category": "practice",
                    "description": "Опишите, как ML помогает выявлять мошеннические транзакции.",
                    "task_type": "text",
                    "correct_answer": "Обучение модели на исторических данных с меткой мошенничества, выявление аномалий.",
                    "points": 20,
                },
            ]
        # Системная и программная инженерия
        elif "Системная и программная инженерия" in track_name:
            return [
                {
                    "title": "Что такое Docker?",
                    "category": "theory",
                    "description": "Для чего используется Docker?",
                    "task_type": "single",
                    "correct_answer": "Контейнеризация приложений",
                    "points": 10,
                    "options": [
                        ("Виртуализация серверов", False),
                        ("Контейнеризация приложений", True),
                        ("Управление базами данных", False),
                    ],
                },
                {
                    "title": "Напишите Dockerfile",
                    "category": "practice",
                    "description": "Напишите простой Dockerfile для Python-приложения (Flask).",
                    "task_type": "code",
                    "correct_answer": 'FROM python:3.9\nWORKDIR /app\nCOPY . .\nRUN pip install flask\nCMD ["python", "app.py"]',
                    "points": 30,
                },
            ]
        # Интернет вещей
        elif "Интернет вещей" in track_name:
            return [
                {
                    "title": "Протокол MQTT",
                    "category": "theory",
                    "description": "Какой транспортный протокол обычно используется в MQTT?",
                    "task_type": "single",
                    "correct_answer": "TCP",
                    "points": 10,
                    "options": [("UDP", False), ("TCP", True), ("HTTP", False)],
                },
                {
                    "title": "Схема IoT-устройства",
                    "category": "practice",
                    "description": "Опишите архитектуру IoT-устройства для сбора температуры.",
                    "task_type": "text",
                    "correct_answer": "Датчик → микроконтроллер (ESP32) → Wi-Fi → MQTT брокер → база данных",
                    "points": 20,
                },
            ]
        # Графический дизайн и 3D-дизайн
        elif "Графический дизайн и 3D-дизайн" in track_name:
            return [
                {
                    "title": "Что такое Figma?",
                    "category": "theory",
                    "description": "Для чего используется Figma?",
                    "task_type": "single",
                    "correct_answer": "Прототипирование интерфейсов",
                    "points": 10,
                    "options": [
                        ("Редактирование видео", False),
                        ("Прототипирование интерфейсов", True),
                        ("3D-моделирование", False),
                    ],
                },
                {
                    "title": "Создание прототипа",
                    "category": "practice",
                    "description": "Опишите шаги создания интерактивного прототипа в Figma.",
                    "task_type": "text",
                    "correct_answer": "Создание экранов, добавление ссылок, настройка переходов, публикация прототипа.",
                    "points": 20,
                },
            ]
        # Для остальных треков – базовый набор
        else:
            return [
                {
                    "title": f"Основы {track_name}",
                    "category": "theory",
                    "description": "Выберите верное утверждение.",
                    "task_type": "single",
                    "correct_answer": "Правильный ответ",
                    "points": 10,
                    "options": [("Неправильно", False), ("Правильно", True)],
                },
                {
                    "title": "Практическое задание",
                    "category": "practice",
                    "description": "Опишите применение знаний на практике.",
                    "task_type": "text",
                    "correct_answer": "Развёрнутый ответ",
                    "points": 15,
                },
            ]

    def create_progress(self):
        self.stdout.write("Создание прогресса студентов...")
        for student in self.students:
            num_tracks_for_student = random.randint(2, 5)
            selected_tracks = random.sample(self.tracks, k=num_tracks_for_student)
            for track in selected_tracks:
                progress, _ = UserProgress.objects.get_or_create(
                    user=student, track=track
                )
                # Для демонстрации отмечаем выполненные задания (все auto_check задания)
                tasks = list(track.tasks.all())
                if tasks:
                    completed_count = random.randint(0, len(tasks))
                    for task in random.sample(tasks, k=completed_count):
                        progress.completed_tasks.add(task)
                checklist_items = []
                for checklist in track.checklists.all():
                    checklist_items.extend(checklist.items.all())
                if checklist_items:
                    completed_items_count = random.randint(0, len(checklist_items))
                    for item in random.sample(checklist_items, k=completed_items_count):
                        progress.checklist_items.add(item)
                progress.save()
        self.stdout.write("✅ Прогресс студентов создан.")

    def create_chats(self):
        self.stdout.write("Создание чатов и сообщений...")
        for student in self.students:
            progresses = UserProgress.objects.filter(user=student)
            for progress in progresses:
                track = progress.track
                curator = self.track_curator_map.get(track.id)
                if not curator:
                    curator = random.choice(self.curators)
                room, created = ChatRoom.objects.get_or_create(
                    track=track, student=student, defaults={"curator": curator}
                )
                if created:
                    ChatMessage.objects.create(
                        room=room,
                        user=curator,
                        message=f'Привет! Я куратор трека "{track.name}". Рад(а) помочь.',
                        is_read=False,
                    )
                    if random.random() < 0.7:
                        ChatMessage.objects.create(
                            room=room,
                            user=student,
                            message="Спасибо! С чего лучше начать?",
                            is_read=False,
                        )
                        if random.random() < 0.5:
                            ChatMessage.objects.create(
                                room=room,
                                user=curator,
                                message="Начните с гайдов и заданий. Удачи!",
                                is_read=False,
                            )
        self.stdout.write("✅ Чаты и сообщения созданы.")

    def _random_guide_title(self, track_name):
        titles = [
            f"Введение в {track_name}",
            f"Ключевые понятия {track_name}",
            f"Практическое применение {track_name}",
            f"Обзор трендов",
            f"Как эффективно изучать {track_name}",
            f"Примеры проектов",
            f"Частые ошибки",
        ]
        return random.choice(titles)
