import re
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from nemotron_architect.llm import NemotronClient
from nemotron_architect.tavily_search import TavilySearcher
from nemotron_architect.sandbox import CodeSandbox, ExecutionResult

logger = logging.getLogger(__name__)

@dataclass
class BuildReport:
    prompt: str
    success: bool
    files: Dict[str, str] = field(default_factory=dict)
    test_results: Optional[ExecutionResult] = None
    heal_attempts: int = 0
    research_summary: List[Dict[str, str]] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

class NemotronArchitectAgent:
    """
    Autonomous Self-Healing Software Engineering Agent.
    Powered by NVIDIA Nemotron (served on Nebius Token Factory) & Tavily Search.
    """
    def __init__(
        self,
        llm: Optional[NemotronClient] = None,
        searcher: Optional[TavilySearcher] = None,
        on_log: Optional[Callable[[str], None]] = None
    ):
        self.llm = llm or NemotronClient()
        self.searcher = searcher or TavilySearcher()
        self.on_log = on_log or (lambda msg: None)

    def log(self, message: str):
        logger.info(message)
        self.on_log(message)

    def run(self, user_prompt: str, output_dir: Optional[str] = None) -> BuildReport:
        """
        Executes end-to-end autonomous engineering pipeline:
        Research -> Architecture Planning -> Code Gen -> Sandboxed Test -> Self-Healing.
        """
        report = BuildReport(prompt=user_prompt, success=False)
        self.log(f"🚀 Initializing Nemotron-Architect for task: '{user_prompt}'")

        # Step 1: Tavily Search Grounding
        self.log("🔍 [Phase 1/5] Fetching live technical documentation via Tavily...")
        research_docs = self.searcher.search_docs(user_prompt)
        report.research_summary = research_docs
        self.log(f"   ✓ Retrieved {len(research_docs)} live technical references.")

        # Step 2: Architecture Planning with NVIDIA Nemotron
        self.log("📐 [Phase 2/5] Synthesizing architecture & file schema using NVIDIA Nemotron...")
        plan_prompt = self._build_planning_prompt(user_prompt, research_docs)
        plan_raw = self.llm.generate([{"role": "user", "content": plan_prompt}])
        architecture = self._parse_json_or_fallback(plan_raw, user_prompt)
        self.log(f"   ✓ Planned {len(architecture.get('files', []))} core modules with test coverage.")

        # Step 3: Code Generation
        self.log("💻 [Phase 3/5] Generating typed, production-ready code and hermetic tests...")
        files: Dict[str, str] = {}
        for file_spec in architecture.get("files", []):
            path = file_spec.get("path", "module.py")
            desc = file_spec.get("description", "")
            self.log(f"   ⚙️ Coding module: {path}")
            code = self._generate_file_code(user_prompt, path, desc, files, research_docs)
            files[path] = code
        report.files = files

        # Step 4: Sandboxed Verification & Closed-Loop Execution
        self.log("🧪 [Phase 4/5] Executing hermetic test suite in local sandbox...")
        sandbox = CodeSandbox(base_dir=output_dir)
        for path, content in files.items():
            sandbox.write_file(path, content)

        test_result = sandbox.run_tests()
        report.test_results = test_result

        # Step 5: Autonomous Self-Healing Loop
        heal_count = 0
        max_heals = 3
        while not test_result.success and heal_count < max_heals:
            heal_count += 1
            self.log(f"⚠️ [Phase 5/5] Test failure detected! Triggering Self-Healing Loop (Attempt {heal_count}/{max_heals})...")
            self.log(f"   Traceback snippet: {test_result.stderr[:200]}...")

            repaired_files = self._self_heal_files(files, test_result.stderr, test_result.stdout)
            files.update(repaired_files)
            report.files = files

            # Update sandbox with repaired files
            for p, c in repaired_files.items():
                sandbox.write_file(p, c)

            test_result = sandbox.run_tests()
            report.test_results = test_result

        report.heal_attempts = heal_count
        if test_result.success:
            self.log(f"🎉 All tests PASSED with 100% green verification! Project ready.")
            report.success = True
        else:
            self.log(f"❌ Test verification did not pass after {max_heals} attempts.")
            report.success = False

        return report

    def _build_planning_prompt(self, prompt: str, docs: List[Dict[str, str]]) -> str:
        doc_context = "\n".join([f"- {d['title']}: {d['content'][:150]}" for d in docs])
        return f"""You are NVIDIA Nemotron acting as Chief Software Architect on Nebius Token Factory.
Plan a modular, tested Python software project for the following requirement:
"{prompt}"

Relevant Docs & Standards:
{doc_context}

Return a STRICT JSON object in this format:
{{
  "project_name": "short_name",
  "files": [
    {{"path": "service.py", "description": "Core logic implementation"}},
    {{"path": "test_service.py", "description": "Comprehensive pytest unit tests covering edge cases"}}
  ]
}}
Ensure there is at least one core implementation file and one test file.
"""

    def _generate_file_code(self, prompt: str, file_path: str, description: str, existing_files: Dict[str, str], docs: List[Dict[str, str]]) -> str:
        context_files = "\n\n".join([f"# --- {p} ---\n{c}" for p, c in existing_files.items()])
        code_prompt = f"""You are NVIDIA Nemotron 70B, an elite software engineer.
Generate clean, self-contained Python code for the file: `{file_path}`.
Role: {description}
Goal: {prompt}

Existing Project Context:
{context_files if context_files else "No previous files yet."}

Requirements:
- Production-grade code with type hints.
- If this is a test file, use standard pytest and import the implementation properly.
- Return ONLY the executable Python code inside ```python ``` blocks. No explanatory chat.
"""
        raw = self.llm.generate([{"role": "user", "content": code_prompt}])
        return self._extract_code(raw)

    def _self_heal_files(self, current_files: Dict[str, str], stderr: str, stdout: str) -> Dict[str, str]:
        """
        NVIDIA Nemotron analyzes execution stack traces and provides surgical repairs.
        """
        heal_prompt = f"""You are NVIDIA Nemotron acting as Senior Autonomous Debugger.
A unit test failed during execution. Analyze the error trace and fix the buggy code.

ERROR TRACE:
{stderr}
{stdout}

CURRENT FILES:
{json.dumps(current_files, indent=2)}

Return a JSON dictionary mapping the modified file path to its full corrected code:
{{
  "service.py": "def corrected_code(): ..."
}}
"""
        response = self.llm.generate([{"role": "user", "content": heal_prompt}])
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, dict):
                    return {str(k): str(v) for k, v in parsed.items() if isinstance(v, str)}
            except Exception:
                pass
        return {}

    def _parse_json_or_fallback(self, raw: str, user_prompt: str) -> Dict[str, Any]:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        # Fallback architecture
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', user_prompt.lower())[:20].strip('_') or "project"
        return {
            "project_name": safe_name,
            "files": [
                {"path": f"{safe_name}.py", "description": "Core business logic"},
                {"path": f"test_{safe_name}.py", "description": "Pytest unit tests"}
            ]
        }

    def _extract_code(self, raw: str) -> str:
        match = re.search(r'```python(.*?)```', raw, re.DOTALL)
        if match:
            return match.group(1).strip()
        match_generic = re.search(r'```(.*?)```', raw, re.DOTALL)
        if match_generic:
            return match_generic.group(1).strip()
        return raw.strip()
