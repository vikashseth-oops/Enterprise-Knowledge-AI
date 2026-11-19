import json
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.core.logging import logger
from app.core.security import verify_api_key
from app.schemas.eval import EvalReport, EvalRunRequest

router = APIRouter(prefix="/api/v1/eval", tags=["Evaluation"])

RESULTS_FILE = Path(__file__).resolve().parent.parent.parent / "evals" / "results" / "report.json"


@router.get("/latest", response_model=EvalReport, dependencies=[Depends(verify_api_key)])
async def get_latest_eval():
    """Retrieves the latest evaluated performance, recall, and benchmark report."""
    if not RESULTS_FILE.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No evaluation report found. Run an evaluation first via POST /api/v1/eval/run or run_retrieval_eval.py.",
        )

    try:
        data = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
        return EvalReport(**data)
    except Exception as e:
        logger.error("read_eval_report_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read evaluation report: {e!s}",
        )


@router.post("/run", dependencies=[Depends(verify_api_key)])
async def trigger_eval(
    request: EvalRunRequest,
    background_tasks: BackgroundTasks,
):
    """
    Triggers an automated evaluation and benchmark run in the background.
    Results will be saved to evals/results/report.json and report.md.
    """
    from evals.run_retrieval_eval import run_evaluation_suite

    background_tasks.add_task(
        run_evaluation_suite,
        sample_size=request.sample_size or 100,
        evaluate_generation=request.evaluate_generation,
    )

    return {
        "message": "Evaluation suite initiated in the background.",
        "sample_size": request.sample_size,
        "results_path": str(RESULTS_FILE),
    }
