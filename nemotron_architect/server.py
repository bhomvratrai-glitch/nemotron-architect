import os
import sys
import json
import zipfile
import io
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from nemotron_architect.agent import NemotronArchitectAgent, BuildReport
from nemotron_architect.config import config

app = FastAPI(title="Nemotron-Architect Studio", version="1.0.0")

# Store in-memory reports
latest_report: Optional[BuildReport] = None
is_running: bool = False
log_queue: asyncio.Queue = asyncio.Queue()

class GenerateRequest(BaseModel):
    prompt: str
    output_dir: Optional[str] = "./workspace_output"

WEB_DIR = Path(__file__).parent.parent / "web"

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "engine": "NVIDIA Nemotron 70B",
        "provider": "Nebius Token Factory",
        "tavily_enabled": bool(config.tavily_api_key)
    }

@app.post("/api/generate")
async def generate(req: GenerateRequest, background_tasks: BackgroundTasks):
    global is_running
    if is_running:
        raise HTTPException(status_code=400, detail="An autonomous engineering task is already running.")

    def run_agent_task(prompt: str, out_dir: Optional[str]):
        global latest_report, is_running
        is_running = True
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            def broadcast_log(msg: str):
                try:
                    log_queue.put_nowait(msg)
                except Exception:
                    pass

            agent = NemotronArchitectAgent(on_log=broadcast_log)
            report = agent.run(user_prompt=prompt, output_dir=out_dir)
            latest_report = report
            broadcast_log(f"__BUILD_FINISHED__:{json.dumps({'success': report.success, 'files': list(report.files.keys())})}")
        finally:
            is_running = False

    background_tasks.add_task(run_agent_task, req.prompt, req.output_dir)
    return {"status": "started", "prompt": req.prompt}

@app.get("/api/logs/stream")
async def stream_logs():
    async def event_generator():
        while True:
            msg = await log_queue.get()
            yield f"data: {json.dumps({'message': msg})}\n\n"
            if msg.startswith("__BUILD_FINISHED__"):
                break

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/report")
def get_report():
    if not latest_report:
        return {"has_report": False}
    return {
        "has_report": True,
        "success": latest_report.success,
        "prompt": latest_report.prompt,
        "files": latest_report.files,
        "heal_attempts": latest_report.heal_attempts,
        "diagram": latest_report.diagram,
        "security_count": len(latest_report.security_findings),
        "healed_diffs": latest_report.healed_diffs,
        "test_stdout": latest_report.test_results.stdout if latest_report.test_results else "",
        "test_stderr": latest_report.test_results.stderr if latest_report.test_results else "",
        "research": latest_report.research_summary
    }

@app.get("/api/download/zip")
def download_zip():
    if not latest_report or not latest_report.files:
        raise HTTPException(status_code=404, detail="No generated project files found.")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for path, content in latest_report.files.items():
            z.writestr(path, content)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="nemotron_project.zip"'}
    )

if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="static")

def start_server():
    uvicorn.run(app, host=config.server_host, port=config.server_port)

if __name__ == "__main__":
    start_server()
