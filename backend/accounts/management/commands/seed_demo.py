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
    Group,
    EnrollmentRequest,
)
from chat.models import ChatRoom, ChatMessage

User = get_user_model()


class Command(BaseCommand):
    help = "Заполнение БД тестовыми данными (25 треков, кураторы, преподаватели, студенты, контент, прогресс, чаты)"

    def handle(self, *args, **options):
        self.stdout.write("🚀 Начинаем заполнение БД...")

        self.clean_data()
        self.create_directions_and_tracks()
        self.create_users()
        self.assign_curators_and_teachers_to_tracks()
        self.create_educational_content()
        self.create_groups_and_enrollments()
        self.create_progress()
        self.create_chats()

        self.stdout.write(self.style.SUCCESS("✅ База данных успешно заполнена!"))

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
        EnrollmentRequest.objects.all().delete()
        Group.objects.all().delete()
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
            {
                "direction": directions["business"],
                "name": "Управление IT-проектами",
                "short_description": "Agile, Scrum, управление командами",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["business"],
                "name": "Аналитика в RPA",
                "short_description": "Роботизированная автоматизация процессов",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["business"],
                "name": "Бизнес-аналитика",
                "short_description": "Анализ бизнес-процессов и внедрение IT-решений",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["business"],
                "name": "Бизнес в цифровой экономике",
                "short_description": "Цифровая трансформация бизнеса",
                "duration": "2 года",
                "order": 4,
            },
            {
                "direction": directions["business"],
                "name": "Искусственный интеллект в финансовых технологиях (Финтех)",
                "short_description": "AI и ML для финансовой сферы",
                "duration": "2 года",
                "order": 5,
            },
            {
                "direction": directions["business"],
                "name": "Проектирование и внедрение бизнес-решений 1С",
                "short_description": "Разработка на платформе 1С",
                "duration": "2 года",
                "order": 6,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Системная и программная инженерия",
                "short_description": "Разработка сложных систем",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Интеллектуальный анализ данных в цифровой экономике",
                "short_description": "Data Mining и Big Data",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Интернет вещей",
                "short_description": "Разработка IoT-систем",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Предиктивная аналитика и управление в социально-экономических системах",
                "short_description": "Прогнозирование и оптимизация",
                "duration": "2 года",
                "order": 4,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Управление цифровыми продуктами",
                "short_description": "Product Management в IT",
                "duration": "2 года",
                "order": 5,
            },
            {
                "direction": directions["comp_eng"],
                "name": "Интеллектуальные системы анализа данных",
                "short_description": "Продвинутый анализ данных и нейросети",
                "duration": "2 года",
                "order": 6,
            },
            {
                "direction": directions["inf_sys"],
                "name": "Программное обеспечение корпоративных информационных систем",
                "short_description": "Разработка ERP/CRM",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["inf_sys"],
                "name": "Интеллектуальные встраиваемые системы",
                "short_description": "Embedded AI и умные устройства",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["inf_sys"],
                "name": "Техническое обеспечение интеллектуальных информационных систем",
                "short_description": "Аппаратная поддержка ИИ-систем",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["inf_sys"],
                "name": "Технологии разработки и сопровождения интеллектуальных информационных систем",
                "short_description": "MLOps и сопровождение моделей",
                "duration": "2 года",
                "order": 4,
            },
            {
                "direction": directions["app_inf"],
                "name": "Графический дизайн и 3D-дизайн",
                "short_description": "Дизайн интерфейсов, графика, 3D-моделирование",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["app_inf"],
                "name": "Разработка мобильных и веб-приложений",
                "short_description": "React, React Native, Node.js",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["app_inf"],
                "name": "BIM-технологии, IT-решения в архитектуре и строительстве",
                "short_description": "Информационное моделирование зданий",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["app_inf"],
                "name": "Системная аналитика",
                "short_description": "Анализ и проектирование сложных систем",
                "duration": "2 года",
                "order": 4,
            },
            {
                "direction": directions["app_inf"],
                "name": "Промдизайн и инжиниринг",
                "short_description": "Промышленный дизайн и инженерная подготовка",
                "duration": "2 года",
                "order": 5,
            },
            {
                "direction": directions["app_math"],
                "name": "Алгоритмы и методы наукоемкого программного обеспечения",
                "short_description": "Сложные алгоритмы для научных задач",
                "duration": "2 года",
                "order": 1,
            },
            {
                "direction": directions["app_math"],
                "name": "Робототехника и киберфизические системы",
                "short_description": "Разработка роботов и управляющих систем",
                "duration": "2 года",
                "order": 2,
            },
            {
                "direction": directions["app_math"],
                "name": "Прикладная математика в интеллектуальных системах",
                "short_description": "Математические основы ИИ",
                "duration": "2 года",
                "order": 3,
            },
            {
                "direction": directions["app_math"],
                "name": "Искусственный интеллект и робототехника",
                "short_description": "Интеграция ИИ в робототехнические системы",
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
                full_description=t.get(
                    "full_description", "Полное описание будет добавлено позже."
                ),
                career_paths=t.get("career_paths", "Карьерные пути..."),
                skills=t.get("skills", "Навыки..."),
                duration=t["duration"],
                is_active=True,
                order=t["order"],
            )
            self.tracks.append(track)
        self.stdout.write(
            f"✅ Создано {len(directions)} направлений и {len(self.tracks)} треков."
        )

    def create_users(self):
        self.stdout.write("Создание пользователей...")
        # Админ
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin123",
                role="admin",
            )

        # Кураторы (25 штук, по одному на трек)
        curators = []
        curator_names = [
            "Анна",
            "Дмитрий",
            "Елена",
            "Сергей",
            "Мария",
            "Ольга",
            "Игорь",
            "Татьяна",
            "Алексей",
            "Наталья",
            "Владимир",
            "Ксения",
            "Павел",
            "Юлия",
            "Артём",
            "Екатерина",
            "Михаил",
            "Анастасия",
            "Андрей",
            "Виктория",
            "Николай",
            "Светлана",
            "Денис",
            "Людмила",
            "Григорий",
        ]
        for i, name in enumerate(curator_names[:25], 1):
            curator = User.objects.create_user(
                username=f"curator_{name.lower()}",
                email=f"curator_{i}@example.com",
                password="curator123",
                first_name=name,
                last_name="Куратор",
                role="curator",
            )
            curators.append(curator)

        # Преподаватели (50 штук, по два на трек)
        teachers = []
        teacher_first = [
            "Пётр",
            "Ольга",
            "Иван",
            "Светлана",
            "Алексей",
            "Елена",
            "Дмитрий",
            "Мария",
            "Сергей",
            "Татьяна",
            "Андрей",
            "Наталья",
            "Владимир",
            "Ирина",
            "Михаил",
            "Анна",
            "Николай",
            "Евгения",
            "Юрий",
            "Кристина",
            "Виктор",
            "Алиса",
            "Станислав",
            "Вероника",
            "Роман",
            "Валерия",
            "Константин",
            "Антонина",
            "Георгий",
            "Зоя",
        ]
        for i in range(1, 51):
            first = teacher_first[(i - 1) % len(teacher_first)]
            teacher = User.objects.create_user(
                username=f"teacher_{first.lower()}_{i}",
                email=f"teacher_{i}@example.com",
                password="teacher123",
                first_name=first,
                last_name="Преподаватель",
                role="teacher",
            )
            teachers.append(teacher)

        # Студенты (25 треков * 6 = 150)
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
            "Кирилл",
            "Виктор",
            "Анастасия",
            "Андрей",
            "Екатерина",
            "Юлия",
            "Василий",
            "Ксения",
            "Глеб",
            "Дарья",
            "Илья",
            "Маргарита",
            "Евгений",
            "София",
            "Алиса",
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
            "Фёдоров",
            "Морозов",
            "Волков",
            "Алексеев",
            "Лебедев",
            "Семёнов",
            "Егоров",
            "Павлов",
            "Козлов",
            "Степанов",
        ]
        for i in range(1, 151):
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
        self.teachers = teachers
        self.students = students
        self.stdout.write(
            f"✅ Создано: {len(curators)} кураторов, {len(teachers)} преподавателей, {len(students)} студентов."
        )

    def assign_curators_and_teachers_to_tracks(self):
        self.stdout.write(
            "Привязка кураторов (один на трек) и преподавателей (два на трек)..."
        )
        for idx, track in enumerate(self.tracks):
            # Куратор – однозначно
            curator = self.curators[idx]  # 1:1
            track.curator = curator
            track.save()
            # Преподаватели – два на трек
            teacher1 = self.teachers[idx * 2]
            teacher2 = self.teachers[idx * 2 + 1]
            track.teachers.add(teacher1, teacher2)
        self.stdout.write("✅ Кураторы и преподаватели привязаны.")

    def create_educational_content(self):
        self.stdout.write("Создание учебного контента (гайды, чек-листы, задания)...")
        for track in self.tracks:
            # Гайды (3-5)
            num_guides = random.randint(3, 5)
            for i in range(1, num_guides + 1):
                Guide.objects.create(
                    track=track,
                    title=f"Гайд {i}: {self._random_guide_title(track.name)}",
                    content=f"Содержание гайда {i} по треку «{track.name}».",
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

            # Задания (минимум 6: 3 теории + 3 практики)
            self._create_tasks_for_track(track)
        self.stdout.write("✅ Учебный контент создан.")

    def _create_tasks_for_track(self, track):
        tasks_data = []
        # 3 теоретических (single/multiple)
        for i in range(1, 4):
            tasks_data.append(
                {
                    "title": f"Теоретический вопрос {i} по {track.name}",
                    "description": "Выберите правильный вариант ответа.",
                    "category": "theory",
                    "task_type": "single",
                    "correct_answer": "Правильный ответ",
                    "points": 10,
                    "options": [
                        ("Вариант A", False),
                        ("Вариант B", True),
                        ("Вариант C", False),
                    ],
                }
            )
        # 3 практических (text)
        for i in range(1, 4):
            tasks_data.append(
                {
                    "title": f"Практическое задание {i} по {track.name}",
                    "description": "Опишите решение задачи.",
                    "category": "practice",
                    "task_type": "text",
                    "correct_answer": "Развёрнутый ответ",
                    "points": 15,
                }
            )
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
            if "options" in task_info:
                for opt_text, is_correct in task_info["options"]:
                    TaskOption.objects.create(
                        task=task, text=opt_text, is_correct=is_correct
                    )

    def create_groups_and_enrollments(self):
        self.stdout.write(
            "Создание групп и зачисление студентов (каждый студент – на один трек)..."
        )
        # Для каждого трека создаём группу
        group_map = {}
        for track in self.tracks:
            group, _ = Group.objects.get_or_create(
                track=track,
                defaults={"name": f"Группа {track.name}", "curator": track.curator},
            )
            group_map[track.id] = group

        # Распределяем студентов по трекам (каждый студент попадает на уникальный трек, 6 на трек)
        student_per_track = 6
        for idx, track in enumerate(self.tracks):
            start = idx * student_per_track
            end = start + student_per_track
            track_students = self.students[start:end]
            for student in track_students:
                # Создаём заявку и сразу принимаем
                req, _ = EnrollmentRequest.objects.get_or_create(
                    student=student, track=track, defaults={"status": "pending"}
                )
                req.status = "accepted"
                req.reviewed_by = track.curator
                req.save()
                # Зачисляем в группу
                student.group = group_map[track.id]
                student.save()
                # Создаём прогресс
                UserProgress.objects.get_or_create(user=student, track=track)
        self.stdout.write("✅ Группы созданы, студенты зачислены.")

    def create_progress(self):
        self.stdout.write("Отметка выполненных заданий (случайный прогресс)...")
        for student in self.students:
            if not student.group:
                continue
            track = student.group.track
            progress = UserProgress.objects.filter(user=student, track=track).first()
            if not progress:
                continue
            tasks = list(track.tasks.all())
            if tasks:
                # От 1 до 3 заданий выполнено (демо)
                completed_count = random.randint(1, min(3, len(tasks)))
                for task in random.sample(tasks, k=completed_count):
                    progress.completed_tasks.add(task)
            checklist_items = []
            for checklist in track.checklists.all():
                checklist_items.extend(checklist.items.all())
            if checklist_items:
                completed_items_count = random.randint(1, min(3, len(checklist_items)))
                for item in random.sample(checklist_items, k=completed_items_count):
                    progress.checklist_items.add(item)
            progress.save()
        self.stdout.write("✅ Прогресс студентов создан.")

    def create_chats(self):
        self.stdout.write("Создание групповых чатов и личных чатов студент-куратор...")
        # Для каждого трека создаём групповой чат (без поля title, просто связь)
        for track in self.tracks:
            group_chat, created = ChatRoom.objects.get_or_create(
                track=track,
                is_group_chat=True,
            )
            # Добавляем куратора и всех студентов группы
            if track.curator:
                group_chat.participants.add(track.curator)
            group = Group.objects.filter(track=track).first()
            if group:
                for student in group.students.all():
                    group_chat.participants.add(student)
            if created:
                # Приветственное сообщение от куратора
                if track.curator:
                    ChatMessage.objects.create(
                        room=group_chat,
                        user=track.curator,
                        message=f"Добро пожаловать в групповой чат трека «{track.name}»!",
                    )
        # Личные чаты студент-куратор (уже должны быть созданы при зачислении, но добавим для полноты)
        for student in self.students:
            if not student.group or not student.group.track:
                continue
            track = student.group.track
            curator = track.curator
            if not curator:
                continue
            private_chat, created = ChatRoom.objects.get_or_create(
                track=track,
                student=student,
                curator=curator,
                is_group_chat=False,
            )
            if created:
                ChatMessage.objects.create(
                    room=private_chat,
                    user=curator,
                    message=f"Здравствуйте, {student.first_name}! Я куратор трека «{track.name}». Рад(а) помочь.",
                )
        self.stdout.write("✅ Чаты созданы.")

    def _random_guide_title(self, track_name):
        titles = [
            f"Введение в {track_name}",
            f"Ключевые понятия и инструменты {track_name}",
            f"Практическое применение {track_name}",
            f"Обзор современных трендов в {track_name}",
            f"Как эффективно изучать {track_name}",
            f"Примеры успешных проектов по {track_name}",
            f"Частые ошибки начинающих в {track_name}",
        ]
        return random.choice(titles)
