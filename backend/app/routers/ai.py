from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import gigachat, models, reports, schemas
from ..database import get_db
from ..deps import get_current_user
from .export import gather_department_report_data, gather_employee_report_data

router = APIRouter(prefix="/ai", tags=["ai"])

SYSTEM_PROMPT = (
    "Ты — ассистент руководителя разработки, помогаешь анализировать развитие сотрудников "
    "по данным системы Performance Review. Отвечай на русском языке, кратко и по делу, "
    "структурируй ответ короткими абзацами или списком. Не выдумывай факты, которых нет "
    "во входных данных."
)


def _build_employee_prompt(data: dict) -> str:
    lines = [
        f"Сотрудник: {data['employee']['full_name']}",
        f"Направление: {data['employee']['direction']}",
        f"Подразделение: {data['employee']['department']}",
        f"Выполнение плана обучения: {data['stats']['completion_pct']}% "
        f"({data['stats']['confirmed']} из {data['stats']['total']} навыков подтверждено, "
        f"{data['stats']['problem']} просрочено)",
        "",
        "План обучения:",
    ]
    for item in data["plan_items"]:
        status_label = reports.STATUS_LABELS.get(item["status"], item["status"])
        line = f"- {item['skill']}: {status_label}, план {item['planned_date'].isoformat()}"
        if item["confirmed_date"]:
            line += f", подтверждён {item['confirmed_date'].isoformat()}"
        lines.append(line)

    lines.append("")
    lines.append(f"Проведено PR-встреч: {len(data['meetings'])}")
    for m in data["meetings"][:10]:
        lines.append(f"- {m['date'].isoformat()}: подтверждено навыков {m['confirmed_skills']}, проблем {m['problems']}")

    open_problems = [p for p in data["problems"] if not p["resolved"]]
    if open_problems:
        lines.append("")
        lines.append("Открытые проблемы:")
        for p in open_problems:
            lines.append(f"- {p['skill'] or 'Общее'}: {p['comment']}")

    lines.append("")
    lines.append(
        "На основе этих данных напиши: 1) краткую характеристику прогресса сотрудника, "
        "2) риски и на что стоит обратить внимание, 3) конкретные рекомендации руководителю "
        "для следующей PR-встречи."
    )
    return "\n".join(lines)


def _build_department_prompt(data: dict) -> str:
    lines = [
        f"Подразделение: {data['department']['path']}",
        f"Руководитель: {data['department']['manager'] or '—'}",
        f"Сотрудников: {data['stats']['people']}",
        f"Среднее выполнение плана обучения: {data['stats']['completion_pct']}%",
        f"Открытых проблем в команде: {data['stats']['open_problems']}",
        "",
        "По сотрудникам:",
    ]
    for e in data["employees"]:
        line = f"- {e['full_name']} ({e['direction']}): {e['confirmed']}/{e['total']} навыков, {e['completion_pct']}%"
        if e["open_problems"]:
            line += f", открытых проблем: {e['open_problems']}"
        lines.append(line)

    lines.append("")
    lines.append(
        "На основе этих данных напиши: 1) краткую сводку по состоянию команды, "
        "2) кто из сотрудников требует внимания и почему, 3) рекомендации руководителю "
        "подразделения по приоритетам на ближайший месяц."
    )
    return "\n".join(lines)


@router.post("/employees/{user_id}", response_model=schemas.AiAnalysisOut)
async def analyze_employee(user_id: str, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    if not gigachat.is_configured():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "GigaChat не настроен на сервере (GIGACHAT_AUTH_KEY)")
    data = await gather_employee_report_data(db, user_id, user)
    text = await gigachat.complete(SYSTEM_PROMPT, _build_employee_prompt(data))
    if text is None:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Не удалось получить ответ от GigaChat")
    return schemas.AiAnalysisOut(text=text)


@router.post("/departments/{dept_id}", response_model=schemas.AiAnalysisOut)
async def analyze_department(dept_id: str, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    if not gigachat.is_configured():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "GigaChat не настроен на сервере (GIGACHAT_AUTH_KEY)")
    data = await gather_department_report_data(db, dept_id, user)
    text = await gigachat.complete(SYSTEM_PROMPT, _build_department_prompt(data))
    if text is None:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Не удалось получить ответ от GigaChat")
    return schemas.AiAnalysisOut(text=text)
