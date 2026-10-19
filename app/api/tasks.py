from fastapi import APIRouter, HTTPException, Response, status

from ..schemas import Task, TaskCreate, TaskUpdate
from ..services import tasks as task_service


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[Task])
def list_tasks(status_filter: str | None = None) -> list[dict]:
    return task_service.list_tasks(status_filter)


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> dict:
    return task_service.create_task(payload)


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> dict:
    try:
        task = task_service.update_task(task_id, payload)
    except task_service.EmptyUpdateError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    if task is None:
        raise HTTPException(status_code=404, detail="המשימה לא נמצאה")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    if not task_service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="המשימה לא נמצאה")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

