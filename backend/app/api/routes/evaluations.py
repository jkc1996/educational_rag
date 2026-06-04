from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_evaluation_service
from app.schemas.evaluations import EvaluationSetsResponse, RagasEvaluationRequest, RagasEvaluationResponse
from app.services.evaluation_service import RagasEvaluationService

router = APIRouter()


@router.get("/evaluations/eval-sets", response_model=EvaluationSetsResponse)
def list_eval_sets(service: RagasEvaluationService = Depends(get_evaluation_service)) -> EvaluationSetsResponse:
    return service.list_eval_sets()


@router.post("/evaluations/ragas", response_model=RagasEvaluationResponse)
def run_ragas(
    request: RagasEvaluationRequest,
    service: RagasEvaluationService = Depends(get_evaluation_service),
) -> RagasEvaluationResponse:
    try:
        return service.run(request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
