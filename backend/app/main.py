from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.database import engine
from app.models import Project, Agent, Task, TaskDependency, AgentRun, Error, ErrorAttempt

from app.routes.projects import router as project_router
from app.routes.tasks import router as task_router
from app.routes.agents import router as agent_router
from app.routes.agent_runs import router as agent_run_router
from app.routes.errors import router as error_router
from app.routes.project_brain import router as project_brain_router
from app.routes.master import router as master_router
from app.routes.llm_interactions import router as llm_interactions_router

app = FastAPI(
    title="AI Software Factory",
    description="Backend for the multi-agent software engineering platform",
    version="0.1.0"
)

app.include_router(project_router)
app.include_router(task_router)
app.include_router(agent_router)
app.include_router(agent_run_router)
app.include_router(error_router)
app.include_router(project_brain_router)
app.include_router(master_router)
app.include_router(llm_interactions_router)

@app.get("/")
def root():
    return {
        "message": "AI Software Factory backend is running"
    }


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            return {
                "status": "healthy",
                "database": "connected"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }