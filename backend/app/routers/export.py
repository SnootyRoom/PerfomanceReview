import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .. import models, permissions, reports
from ..database import get_db
from ..deps import get_current_user

router = APIRouter(prefix="/export", tags=["export"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
PDF_MEDIA_TYPE = "application/pdf"


def _attachment(content: bytes, media_type: str, filename: str) -> Response:
    return Response(content=content, media_type=media_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'})


async def gather_employee_report_data(db: AsyncSession, user_id: str, viewer: models.User) -> dict:
    if not await permissions.can_view(db, viewer, user_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав для доступа к данным этого сотрудника")
    employee = await db.get(models.User, user_id)
    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Сотрудник не найден")
    direction = await db.get(models.Direction, employee.direction_id)

    plan_items_raw = (await db.execute(select(models.PlanItem).where(models.PlanItem.user_id == user_id))).scalars().all()
    meetings_raw = (
        (
            await db.execute(
                select(models.Meeting)
                .options(selectinload(models.Meeting.skill_marks), selectinload(models.Meeting.problems))
                .where(models.Meeting.employee_id == user_id)
                .order_by(models.Meeting.date.desc())
            )
        )
        .scalars()
        .all()
    )

    skill_ids = {p.skill_id for p in plan_items_raw}
    for m in meetings_raw:
        skill_ids |= {sm.skill_id for sm in m.skill_marks}
        skill_ids |= {p.skill_id for p in m.problems if p.skill_id}
    skills_map = {}
    if skill_ids:
        skills_map = {s.id: s.name for s in (await db.execute(select(models.Skill).where(models.Skill.id.in_(skill_ids)))).scalars()}

    conductor_ids = {m.conducted_by_id for m in meetings_raw}
    conductors = {}
    if conductor_ids:
        conductors = {u.id: u.full_name for u in (await db.execute(select(models.User).where(models.User.id.in_(conductor_ids)))).scalars()}

    today = datetime.date.today()
    plan_items = []
    confirmed_n = 0
    problem_n = 0
    for p in plan_items_raw:
        if p.confirmed:
            status_str, confirmed_n = "confirmed", confirmed_n + 1
        elif p.planned_date < today:
            status_str, problem_n = "problem", problem_n + 1
        else:
            status_str = "planned"
        plan_items.append(
            {
                "skill": skills_map.get(p.skill_id, "—"),
                "planned_date": p.planned_date,
                "status": status_str,
                "confirmed_date": p.confirmed_date,
            }
        )
    plan_items.sort(key=lambda i: i["planned_date"])

    meetings = []
    problems = []
    for m in meetings_raw:
        meetings.append(
            {
                "date": m.date,
                "conducted_by": conductors.get(m.conducted_by_id, "—"),
                "confirmed_skills": sum(1 for sm in m.skill_marks if sm.confirmed),
                "problems": len(m.problems),
            }
        )
        for p in m.problems:
            problems.append(
                {
                    "date": m.date,
                    "skill": skills_map.get(p.skill_id) if p.skill_id else None,
                    "comment": p.comment,
                    "resolved": p.resolved,
                }
            )

    total = len(plan_items)
    return {
        "employee": {
            "full_name": employee.full_name,
            "login": employee.login,
            "direction": direction.name if direction else "—",
            "department": await permissions.department_path(db, employee.department_id),
        },
        "generated_at": today,
        "plan_items": plan_items,
        "meetings": meetings,
        "problems": problems,
        "stats": {
            "total": total,
            "confirmed": confirmed_n,
            "problem": problem_n,
            "completion_pct": round(confirmed_n / total * 100) if total else 0,
        },
    }


async def gather_department_report_data(db: AsyncSession, dept_id: str, viewer: models.User) -> dict:
    if not await permissions.can_view_department(db, viewer, dept_id):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав для доступа к данным этого подразделения")
    dept = await db.get(models.Department, dept_id)
    if not dept:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Подразделение не найдено")

    member_dept_ids = {dept_id} | await permissions.get_descendant_department_ids(db, dept_id)
    employees = (
        (await db.execute(select(models.User).where(models.User.department_id.in_(member_dept_ids)))).scalars().all()
    )
    employee_ids = [e.id for e in employees]

    plan_items = []
    open_problems_by_user: dict[str, int] = {}
    if employee_ids:
        plan_items = (
            (await db.execute(select(models.PlanItem).where(models.PlanItem.user_id.in_(employee_ids)))).scalars().all()
        )
        meetings = (
            (
                await db.execute(
                    select(models.Meeting)
                    .options(selectinload(models.Meeting.problems))
                    .where(models.Meeting.employee_id.in_(employee_ids))
                )
            )
            .scalars()
            .all()
        )
        for m in meetings:
            open_count = sum(1 for p in m.problems if not p.resolved)
            if open_count:
                open_problems_by_user[m.employee_id] = open_problems_by_user.get(m.employee_id, 0) + open_count

    direction_ids = {e.direction_id for e in employees}
    directions_map = {}
    if direction_ids:
        directions_map = {
            d.id: d.name for d in (await db.execute(select(models.Direction).where(models.Direction.id.in_(direction_ids)))).scalars()
        }

    today = datetime.date.today()
    by_user: dict[str, list] = {e.id: [] for e in employees}
    for p in plan_items:
        if p.user_id in by_user:
            by_user[p.user_id].append(p)

    employee_rows = []
    total_confirmed = 0
    total_items = 0
    for e in employees:
        items = by_user.get(e.id, [])
        confirmed = sum(1 for p in items if p.confirmed)
        total_confirmed += confirmed
        total_items += len(items)
        employee_rows.append(
            {
                "full_name": e.full_name,
                "direction": directions_map.get(e.direction_id, "—"),
                "confirmed": confirmed,
                "total": len(items),
                "completion_pct": round(confirmed / len(items) * 100) if items else 0,
                "open_problems": open_problems_by_user.get(e.id, 0),
            }
        )
    employee_rows.sort(key=lambda r: r["full_name"])

    manager_name = None
    if dept.manager_id:
        manager = await db.get(models.User, dept.manager_id)
        manager_name = manager.full_name if manager else None

    return {
        "department": {"path": await permissions.department_path(db, dept_id), "manager": manager_name},
        "generated_at": today,
        "employees": employee_rows,
        "stats": {
            "people": len(employees),
            "completion_pct": round(total_confirmed / total_items * 100) if total_items else 0,
            "open_problems": sum(open_problems_by_user.values()),
        },
    }


@router.get("/employees/{user_id}.xlsx")
async def export_employee_xlsx(user_id: str, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    data = await gather_employee_report_data(db, user_id, user)
    return _attachment(reports.build_employee_xlsx(data), XLSX_MEDIA_TYPE, f"report_{data['employee']['login']}.xlsx")


@router.get("/employees/{user_id}.pdf")
async def export_employee_pdf(user_id: str, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    data = await gather_employee_report_data(db, user_id, user)
    return _attachment(reports.build_employee_pdf(data), PDF_MEDIA_TYPE, f"report_{data['employee']['login']}.pdf")


@router.get("/departments/{dept_id}.xlsx")
async def export_department_xlsx(dept_id: str, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    data = await gather_department_report_data(db, dept_id, user)
    return _attachment(reports.build_department_xlsx(data), XLSX_MEDIA_TYPE, f"report_department_{dept_id}.xlsx")


@router.get("/departments/{dept_id}.pdf")
async def export_department_pdf(dept_id: str, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    data = await gather_department_report_data(db, dept_id, user)
    return _attachment(reports.build_department_pdf(data), PDF_MEDIA_TYPE, f"report_department_{dept_id}.pdf")
