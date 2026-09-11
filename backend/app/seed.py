"""Deterministic demo dataset — same company tree, accounts and passwords as
documented in the frontend README, now persisted in Postgres instead of
localStorage. Runs once at startup if the `directions` table is empty.
"""

import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models
from .security import hash_password


def _days(offset: int) -> datetime.date:
    return datetime.date.today() + datetime.timedelta(days=offset)


DIRECTIONS = [
    {"id": "dir-back", "name": "Backend"},
    {"id": "dir-front", "name": "Frontend"},
    {"id": "dir-qa", "name": "QA"},
]

DEPARTMENTS = [
    {"id": "dept-root", "name": "Компания", "parent_id": None, "manager_id": "user-ceo"},
    {"id": "dept-dev", "name": "Разработка", "parent_id": "dept-root", "manager_id": "user-cto"},
    {"id": "dept-back", "name": "Backend", "parent_id": "dept-dev", "manager_id": "user-back-lead"},
    {"id": "dept-front", "name": "Frontend", "parent_id": "dept-dev", "manager_id": "user-front-lead"},
    {"id": "dept-qa", "name": "QA", "parent_id": "dept-dev", "manager_id": "user-qa-lead"},
]

USERS = [
    {"id": "user-admin", "full_name": "Администратор Системы", "login": "admin", "password": "admin", "direction_id": "dir-back", "department_id": "dept-root", "is_admin": True, "avatar_color": "#6366f1", "created_at": _days(-400)},
    {"id": "user-ceo", "full_name": "Иванов Иван", "login": "ceo", "password": "ceo123", "direction_id": "dir-back", "department_id": "dept-root", "is_admin": False, "avatar_color": "#0ea5e9", "created_at": _days(-400)},
    {"id": "user-cto", "full_name": "Смирнова Ольга", "login": "cto", "password": "cto123", "direction_id": "dir-back", "department_id": "dept-root", "is_admin": False, "avatar_color": "#0ea5e9", "created_at": _days(-380)},
    {"id": "user-back-lead", "full_name": "Кузнецов Дмитрий", "login": "back.lead", "password": "lead123", "direction_id": "dir-back", "department_id": "dept-dev", "is_admin": False, "avatar_color": "#22c55e", "created_at": _days(-360)},
    {"id": "user-front-lead", "full_name": "Орлова Анна", "login": "front.lead", "password": "lead123", "direction_id": "dir-front", "department_id": "dept-dev", "is_admin": False, "avatar_color": "#f59e0b", "created_at": _days(-360)},
    {"id": "user-qa-lead", "full_name": "Петров Сергей", "login": "qa.lead", "password": "lead123", "direction_id": "dir-qa", "department_id": "dept-dev", "is_admin": False, "avatar_color": "#ec4899", "created_at": _days(-360)},
    {"id": "user-back-1", "full_name": "Волков Артём", "login": "a.volkov", "password": "pass123", "direction_id": "dir-back", "department_id": "dept-back", "is_admin": False, "avatar_color": "#22c55e", "created_at": _days(-300)},
    {"id": "user-back-2", "full_name": "Соколова Мария", "login": "m.sokolova", "password": "pass123", "direction_id": "dir-back", "department_id": "dept-back", "is_admin": False, "avatar_color": "#22c55e", "created_at": _days(-280)},
    {"id": "user-back-3", "full_name": "Морозов Егор", "login": "e.morozov", "password": "pass123", "direction_id": "dir-back", "department_id": "dept-back", "is_admin": False, "avatar_color": "#22c55e", "created_at": _days(-120)},
    {"id": "user-front-1", "full_name": "Новикова Дарья", "login": "d.novikova", "password": "pass123", "direction_id": "dir-front", "department_id": "dept-front", "is_admin": False, "avatar_color": "#f59e0b", "created_at": _days(-300)},
    {"id": "user-front-2", "full_name": "Лебедев Игорь", "login": "i.lebedev", "password": "pass123", "direction_id": "dir-front", "department_id": "dept-front", "is_admin": False, "avatar_color": "#f59e0b", "created_at": _days(-200)},
    {"id": "user-front-3", "full_name": "Попова Виктория", "login": "v.popova", "password": "pass123", "direction_id": "dir-front", "department_id": "dept-front", "is_admin": False, "avatar_color": "#f59e0b", "created_at": _days(-90)},
    {"id": "user-qa-1", "full_name": "Фёдоров Никита", "login": "n.fedorov", "password": "pass123", "direction_id": "dir-qa", "department_id": "dept-qa", "is_admin": False, "avatar_color": "#ec4899", "created_at": _days(-260)},
    {"id": "user-qa-2", "full_name": "Козлова Елена", "login": "e.kozlova", "password": "pass123", "direction_id": "dir-qa", "department_id": "dept-qa", "is_admin": False, "avatar_color": "#ec4899", "created_at": _days(-150)},
]

SKILLS = [
    {"id": "skill-back-1", "name": "REST API design", "direction_id": "dir-back"},
    {"id": "skill-back-2", "name": "Базы данных (SQL)", "direction_id": "dir-back"},
    {"id": "skill-back-3", "name": "Асинхронное программирование", "direction_id": "dir-back"},
    {"id": "skill-back-4", "name": "Микросервисная архитектура", "direction_id": "dir-back"},
    {"id": "skill-back-5", "name": "Docker / Kubernetes", "direction_id": "dir-back"},
    {"id": "skill-back-6", "name": "Тестирование (unit/integration)", "direction_id": "dir-back"},
    {"id": "skill-front-1", "name": "Vue 3 / Composition API", "direction_id": "dir-front"},
    {"id": "skill-front-2", "name": "TypeScript", "direction_id": "dir-front"},
    {"id": "skill-front-3", "name": "State management (Pinia)", "direction_id": "dir-front"},
    {"id": "skill-front-4", "name": "Веб-производительность", "direction_id": "dir-front"},
    {"id": "skill-front-5", "name": "Доступность (a11y)", "direction_id": "dir-front"},
    {"id": "skill-front-6", "name": "Дизайн-системы", "direction_id": "dir-front"},
    {"id": "skill-qa-1", "name": "Тест-дизайн", "direction_id": "dir-qa"},
    {"id": "skill-qa-2", "name": "Автотесты (E2E)", "direction_id": "dir-qa"},
    {"id": "skill-qa-3", "name": "API-тестирование", "direction_id": "dir-qa"},
    {"id": "skill-qa-4", "name": "Нагрузочное тестирование", "direction_id": "dir-qa"},
    {"id": "skill-qa-5", "name": "Баг-трекинг и репортинг", "direction_id": "dir-qa"},
    {"id": "skill-qa-6", "name": "CI/CD для тестов", "direction_id": "dir-qa"},
]

PLAN_ITEMS = [
    {"id": "plan-1", "user_id": "user-back-1", "skill_id": "skill-back-1", "planned_date": _days(-60), "confirmed": True, "confirmed_date": _days(-58), "confirmed_in_meeting_id": "meeting-1"},
    {"id": "plan-2", "user_id": "user-back-1", "skill_id": "skill-back-2", "planned_date": _days(-20), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-3", "user_id": "user-back-1", "skill_id": "skill-back-3", "planned_date": _days(30), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-4", "user_id": "user-back-1", "skill_id": "skill-back-5", "planned_date": _days(90), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-5", "user_id": "user-back-2", "skill_id": "skill-back-1", "planned_date": _days(-90), "confirmed": True, "confirmed_date": _days(-91), "confirmed_in_meeting_id": "meeting-2"},
    {"id": "plan-6", "user_id": "user-back-2", "skill_id": "skill-back-4", "planned_date": _days(-91), "confirmed": True, "confirmed_date": _days(-91), "confirmed_in_meeting_id": "meeting-2"},
    {"id": "plan-7", "user_id": "user-back-2", "skill_id": "skill-back-6", "planned_date": _days(15), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-8", "user_id": "user-back-3", "skill_id": "skill-back-1", "planned_date": _days(20), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-9", "user_id": "user-back-3", "skill_id": "skill-back-2", "planned_date": _days(45), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-10", "user_id": "user-front-1", "skill_id": "skill-front-1", "planned_date": _days(-70), "confirmed": True, "confirmed_date": _days(-72), "confirmed_in_meeting_id": "meeting-3"},
    {"id": "plan-11", "user_id": "user-front-1", "skill_id": "skill-front-2", "planned_date": _days(-72), "confirmed": True, "confirmed_date": _days(-72), "confirmed_in_meeting_id": "meeting-3"},
    {"id": "plan-12", "user_id": "user-front-1", "skill_id": "skill-front-4", "planned_date": _days(-10), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-13", "user_id": "user-front-1", "skill_id": "skill-front-5", "planned_date": _days(60), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-14", "user_id": "user-front-2", "skill_id": "skill-front-1", "planned_date": _days(-40), "confirmed": True, "confirmed_date": _days(-41), "confirmed_in_meeting_id": "meeting-4"},
    {"id": "plan-15", "user_id": "user-front-2", "skill_id": "skill-front-3", "planned_date": _days(25), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-16", "user_id": "user-front-2", "skill_id": "skill-front-6", "planned_date": _days(75), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-17", "user_id": "user-front-3", "skill_id": "skill-front-2", "planned_date": _days(15), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-18", "user_id": "user-qa-1", "skill_id": "skill-qa-1", "planned_date": _days(-55), "confirmed": True, "confirmed_date": _days(-56), "confirmed_in_meeting_id": "meeting-5"},
    {"id": "plan-19", "user_id": "user-qa-1", "skill_id": "skill-qa-2", "planned_date": _days(-56), "confirmed": True, "confirmed_date": _days(-56), "confirmed_in_meeting_id": "meeting-5"},
    {"id": "plan-20", "user_id": "user-qa-1", "skill_id": "skill-qa-4", "planned_date": _days(-5), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-21", "user_id": "user-qa-1", "skill_id": "skill-qa-6", "planned_date": _days(40), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
    {"id": "plan-22", "user_id": "user-qa-2", "skill_id": "skill-qa-1", "planned_date": _days(-30), "confirmed": True, "confirmed_date": _days(-33), "confirmed_in_meeting_id": "meeting-6"},
    {"id": "plan-23", "user_id": "user-qa-2", "skill_id": "skill-qa-3", "planned_date": _days(35), "confirmed": False, "confirmed_date": None, "confirmed_in_meeting_id": None},
]

MEETINGS = [
    {
        "id": "meeting-1", "employee_id": "user-back-1", "conducted_by_id": "user-back-lead", "date": _days(-58),
        "summary_markdown": "### Итоги встречи\n\nАртём хорошо разобрался с проектированием REST API, разобрали best practices версионирования.\n\n**Дальше:** сфокусироваться на SQL — есть пробелы в оконных функциях.",
        "attachments": [{"type": "link", "name": "Заметки в Confluence", "url": "https://example.com/notes/1"}],
        "skill_marks": [{"skill_id": "skill-back-1", "confirmed": True, "comment": "Уверенно применяет на практике"}],
        "problems": [],
    },
    {
        "id": "meeting-2", "employee_id": "user-back-2", "conducted_by_id": "user-back-lead", "date": _days(-91),
        "summary_markdown": "### Итоги встречи\n\nМария показала отличное понимание микросервисной архитектуры на примере текущего проекта.",
        "attachments": [],
        "skill_marks": [
            {"skill_id": "skill-back-1", "confirmed": True, "comment": ""},
            {"skill_id": "skill-back-4", "confirmed": True, "comment": "Разложила по полочкам паттерны saga/outbox"},
        ],
        "problems": [],
    },
    {
        "id": "meeting-3", "employee_id": "user-front-1", "conducted_by_id": "user-front-lead", "date": _days(-72),
        "summary_markdown": "### Итоги встречи\n\nДарья закрыла Vue 3 и TypeScript, готова к более сложным задачам.",
        "attachments": [{"type": "file", "name": "code-review-screenshot.png", "url": "#"}],
        "skill_marks": [
            {"skill_id": "skill-front-1", "confirmed": True, "comment": ""},
            {"skill_id": "skill-front-2", "confirmed": True, "comment": ""},
        ],
        "problems": [],
    },
    {
        "id": "meeting-4", "employee_id": "user-front-2", "conducted_by_id": "user-front-lead", "date": _days(-41),
        "summary_markdown": "### Итоги встречи\n\nИгорь подтвердил Vue 3, но пока не готов к менторству джунов — рано.",
        "attachments": [],
        "skill_marks": [{"skill_id": "skill-front-1", "confirmed": True, "comment": ""}],
        "problems": [{"scope": "employee", "skill_id": None, "comment": "Нужно подтянуть soft skills — сложно объясняет решения на код-ревью", "resolved": False}],
    },
    {
        "id": "meeting-5", "employee_id": "user-qa-1", "conducted_by_id": "user-qa-lead", "date": _days(-56),
        "summary_markdown": "### Итоги встречи\n\nНикита закрыл тест-дизайн и автотесты, хорошая динамика.",
        "attachments": [],
        "skill_marks": [
            {"skill_id": "skill-qa-1", "confirmed": True, "comment": ""},
            {"skill_id": "skill-qa-2", "confirmed": True, "comment": ""},
        ],
        "problems": [],
    },
    {
        "id": "meeting-6", "employee_id": "user-qa-2", "conducted_by_id": "user-qa-lead", "date": _days(-33),
        "summary_markdown": "### Итоги встречи\n\nЕлена подтвердила тест-дизайн, план по API-тестированию сдвинут.",
        "attachments": [],
        "skill_marks": [{"skill_id": "skill-qa-1", "confirmed": True, "comment": ""}],
        "problems": [{"scope": "skill", "skill_id": "skill-qa-3", "comment": "Не хватает практики с Postman/newman в CI", "resolved": False}],
    },
]


async def seed_if_empty(db: AsyncSession) -> None:
    existing = (await db.execute(select(models.Direction.id).limit(1))).first()
    if existing:
        return

    # Departments and users reference each other (department.manager_id -> user,
    # user.department_id -> department), so insert departments without their
    # manager first, then users, then backfill manager_id once users exist.
    db.add_all(models.Direction(**d) for d in DIRECTIONS)
    db.add_all(models.Department(id=d["id"], name=d["name"], parent_id=d["parent_id"], manager_id=None) for d in DEPARTMENTS)
    await db.flush()

    for u in USERS:
        fields = dict(u)
        plain_password = fields.pop("password")
        db.add(models.User(**fields, password_hash=hash_password(plain_password)))
    db.add_all(models.Skill(**s) for s in SKILLS)
    await db.flush()

    for d in DEPARTMENTS:
        dept = await db.get(models.Department, d["id"])
        dept.manager_id = d["manager_id"]

    for m in MEETINGS:
        meeting = models.Meeting(
            id=m["id"],
            employee_id=m["employee_id"],
            conducted_by_id=m["conducted_by_id"],
            date=m["date"],
            summary_markdown=m["summary_markdown"],
        )
        db.add(meeting)
        for idx, a in enumerate(m["attachments"]):
            db.add(models.Attachment(id=f"{m['id']}-att-{idx}", meeting_id=m["id"], **a))
        for idx, sm in enumerate(m["skill_marks"]):
            db.add(models.SkillMark(id=f"{m['id']}-mark-{idx}", meeting_id=m["id"], **sm))
        for idx, p in enumerate(m["problems"]):
            db.add(models.ProblemFlag(id=f"{m['id']}-problem-{idx}", meeting_id=m["id"], **p))

    db.add_all(models.PlanItem(**p) for p in PLAN_ITEMS)

    await db.commit()
