from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import department as crud
from app.models.department import Department
from app.schemas.common import ResponseModel
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentOut

router = APIRouter(prefix="/system/departments", tags=["departments"])


def _build_tree(departments: list[Department], parent_id: str | None = None) -> list[DepartmentOut]:
    tree = []
    for dept in departments:
        if dept.parent_id == parent_id:
            node = DepartmentOut(
                id=dept.id, name=dept.name, parentId=dept.parent_id,
                sort=dept.sort, leader=dept.leader, phone=dept.phone,
                status=dept.status, remark=dept.remark,
                children=_build_tree(departments, dept.id),
            )
            tree.append(node)
    tree.sort(key=lambda x: x.sort)
    return tree


def _to_out(d: Department) -> DepartmentOut:
    return DepartmentOut(
        id=d.id, name=d.name, parentId=d.parent_id, sort=d.sort,
        leader=d.leader, phone=d.phone, status=d.status, remark=d.remark,
    )


@router.get("/tree")
async def get_department_tree(db: AsyncSession = Depends(get_db)):
    departments = await crud.get_all(db)
    tree = _build_tree(departments)
    return ResponseModel(data=tree)


@router.get("")
async def get_departments(
    page: int = 1, pageSize: int = 10, keyword: str = "",
    db: AsyncSession = Depends(get_db),
):
    all_items = await crud.get_list(db, keyword=keyword)
    total = len(all_items)
    start = (page - 1) * pageSize
    items = all_items[start : start + pageSize]
    return ResponseModel(data={"list": [_to_out(d) for d in items], "total": total})


@router.get("/{dept_id}")
async def get_department(dept_id: str, db: AsyncSession = Depends(get_db)):
    dept = await crud.get_by_id(db, dept_id)
    if not dept:
        return ResponseModel(code=404, message="部门不存在")
    return ResponseModel(data=_to_out(dept))


@router.post("")
async def create_department(body: DepartmentCreate, db: AsyncSession = Depends(get_db)):
    dept = await crud.create(
        db, name=body.name, parent_id=body.parentId, sort=body.sort,
        leader=body.leader, phone=body.phone, status=body.status, remark=body.remark,
    )
    return ResponseModel(data=_to_out(dept))


@router.put("/{dept_id}")
async def update_department(dept_id: str, body: DepartmentUpdate, db: AsyncSession = Depends(get_db)):
    dept = await crud.get_by_id(db, dept_id)
    if not dept:
        return ResponseModel(code=404, message="部门不存在")
    dept = await crud.update(
        db, dept, name=body.name, parent_id=body.parentId, sort=body.sort,
        leader=body.leader, phone=body.phone, status=body.status, remark=body.remark,
    )
    return ResponseModel(data=_to_out(dept))


@router.delete("/{dept_id}")
async def delete_department(dept_id: str, db: AsyncSession = Depends(get_db)):
    dept = await crud.get_by_id(db, dept_id)
    if not dept:
        return ResponseModel(code=404, message="部门不存在")
    await crud.delete(db, dept)
    return ResponseModel(message="删除成功")
