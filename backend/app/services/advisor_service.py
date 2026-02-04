"""Service layer for Anjo Social advisory system."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.advisor import Advisor, Case, CaseNote, CaseStatus, CasePriority


# --- Advisor Operations ---

async def get_advisor(db: AsyncSession, advisor_id) -> Optional[Advisor]:
    """Get an advisor by ID."""
    result = await db.execute(select(Advisor).where(Advisor.id == advisor_id))
    return result.scalars().first()


async def get_active_advisors(db: AsyncSession) -> list[Advisor]:
    """List all active advisors."""
    result = await db.execute(
        select(Advisor)
        .where(Advisor.is_active == True)
        .order_by(Advisor.name)
    )
    return list(result.scalars().all())


async def create_advisor(db: AsyncSession, data: dict) -> Advisor:
    """Create a new advisor."""
    advisor = Advisor(id=uuid4(), **data)
    db.add(advisor)
    return advisor


async def find_best_advisor(
    db: AsyncSession,
    benefits: list[str],
    priority: str = "medium",
) -> Optional[Advisor]:
    """Find the best available advisor based on specialty match and workload.

    Prioriza: 1) especialidade compatível, 2) menor carga de casos ativos.
    """
    # Busca assessores ativos
    result = await db.execute(
        select(Advisor).where(Advisor.is_active == True)
    )
    advisors = list(result.scalars().all())

    if not advisors:
        return None

    # Conta casos ativos por assessor
    active_statuses = [CaseStatus.ASSIGNED.value, CaseStatus.IN_PROGRESS.value]
    case_counts = {}
    for advisor in advisors:
        count_result = await db.execute(
            select(func.count(Case.id))
            .where(
                Case.advisor_id == advisor.id,
                Case.status.in_(active_statuses)
            )
        )
        case_counts[advisor.id] = count_result.scalar() or 0

    # Filtra assessores com capacidade
    available = [
        a for a in advisors
        if case_counts.get(a.id, 0) < a.max_active_cases
    ]

    if not available:
        # Emergência: pega o com menos casos mesmo acima do limite
        if priority == CasePriority.EMERGENCY.value:
            available = advisors
        else:
            return None

    # Ordena por: match de especialidade (desc), carga (asc)
    def score(advisor: Advisor) -> tuple:
        specialties = advisor.specialties or []
        match_count = sum(1 for b in benefits if b in specialties)
        active_count = case_counts.get(advisor.id, 0)
        return (-match_count, active_count)

    available.sort(key=score)
    return available[0]


# --- Case Operations ---

async def create_case(
    db: AsyncSession,
    citizen_session_id: str,
    benefits: list[str],
    escalation_reason: str,
    priority: str = "medium",
    citizen_context: Optional[dict] = None,
    auto_assign: bool = True,
) -> Case:
    """Create a new advisory case, optionally auto-assigning an advisor."""
    case = Case(
        id=uuid4(),
        citizen_session_id=citizen_session_id,
        benefits=benefits,
        escalation_reason=escalation_reason,
        priority=priority,
        citizen_context=citizen_context,
        status=CaseStatus.OPEN.value,
    )

    if auto_assign:
        advisor = await find_best_advisor(db, benefits, priority)
        if advisor:
            case.advisor_id = advisor.id
            case.status = CaseStatus.ASSIGNED.value

    db.add(case)

    # Nota automática do sistema
    system_note = CaseNote(
        id=uuid4(),
        case_id=case.id,
        author="sistema",
        content=f"Caso criado por escalonamento da IA. Motivo: {escalation_reason}",
    )
    db.add(system_note)

    return case


async def get_case(db: AsyncSession, case_id) -> Optional[Case]:
    """Get a case by ID with advisor and notes loaded."""
    result = await db.execute(
        select(Case)
        .options(selectinload(Case.advisor), selectinload(Case.notes))
        .where(Case.id == case_id)
    )
    return result.scalars().first()


async def update_case(
    db: AsyncSession,
    case_id,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    advisor_id=None,
) -> Optional[Case]:
    """Update case fields."""
    case = await get_case(db, case_id)
    if not case:
        return None

    if status:
        case.status = status
        if status == CaseStatus.RESOLVED.value:
            case.resolved_at = datetime.utcnow()
            # Incrementa contador do assessor
            if case.advisor:
                case.advisor.total_resolved += 1

    if priority:
        case.priority = priority

    if advisor_id is not None:
        case.advisor_id = advisor_id
        if case.status == CaseStatus.OPEN.value:
            case.status = CaseStatus.ASSIGNED.value

    case.updated_at = datetime.utcnow()
    return case


async def add_case_note(
    db: AsyncSession,
    case_id,
    author: str,
    content: str,
) -> Optional[CaseNote]:
    """Add a note to a case."""
    case = await get_case(db, case_id)
    if not case:
        return None

    note = CaseNote(
        id=uuid4(),
        case_id=case_id,
        author=author,
        content=content,
    )
    db.add(note)
    return note


async def list_cases(
    db: AsyncSession,
    advisor_id=None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Case], int]:
    """List cases with optional filters. Returns (cases, total_count)."""
    base = select(Case).options(selectinload(Case.advisor))

    conditions = []
    if advisor_id:
        conditions.append(Case.advisor_id == advisor_id)
    if status:
        conditions.append(Case.status == status)
    if priority:
        conditions.append(Case.priority == priority)

    if conditions:
        base = base.where(and_(*conditions))

    # Total count
    count_q = select(func.count(Case.id))
    if conditions:
        count_q = count_q.where(and_(*conditions))
    total = (await db.execute(count_q)).scalar() or 0

    # Paginated results
    result = await db.execute(
        base.order_by(Case.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    cases = list(result.scalars().all())

    return cases, total


async def get_advisor_dashboard(db: AsyncSession, advisor_id) -> dict:
    """Get dashboard data for an advisor."""
    advisor = await get_advisor(db, advisor_id)
    if not advisor:
        return None

    # Casos ativos
    active_statuses = [
        CaseStatus.OPEN.value,
        CaseStatus.ASSIGNED.value,
        CaseStatus.IN_PROGRESS.value,
    ]
    active_result = await db.execute(
        select(Case)
        .options(selectinload(Case.notes))
        .where(
            Case.advisor_id == advisor_id,
            Case.status.in_(active_statuses)
        )
        .order_by(
            # Emergência primeiro
            Case.priority.desc(),
            Case.created_at.asc()
        )
    )
    active_cases = list(active_result.scalars().all())

    # Stats
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    resolved_month = await db.execute(
        select(func.count(Case.id)).where(
            Case.advisor_id == advisor_id,
            Case.status == CaseStatus.RESOLVED.value,
            Case.resolved_at >= month_start,
        )
    )

    # Tempo médio de resolução (últimos 90 dias)
    ninety_days_ago = now - timedelta(days=90)
    avg_result = await db.execute(
        select(
            func.avg(
                func.extract('epoch', Case.resolved_at) -
                func.extract('epoch', Case.created_at)
            )
        ).where(
            Case.advisor_id == advisor_id,
            Case.status == CaseStatus.RESOLVED.value,
            Case.resolved_at >= ninety_days_ago,
            Case.resolved_at.isnot(None),
        )
    )
    avg_seconds = avg_result.scalar()
    avg_days = round(avg_seconds / 86400, 1) if avg_seconds else None

    open_count = sum(1 for c in active_cases if c.status in [CaseStatus.OPEN.value, CaseStatus.ASSIGNED.value])
    in_progress_count = sum(1 for c in active_cases if c.status == CaseStatus.IN_PROGRESS.value)

    return {
        "advisor": advisor.to_dict(),
        "activeCases": [c.to_dict() for c in active_cases],
        "stats": {
            "openCases": open_count,
            "inProgressCases": in_progress_count,
            "resolvedThisMonth": resolved_month.scalar() or 0,
            "totalResolved": advisor.total_resolved,
            "avgResolutionDays": avg_days,
        },
    }
