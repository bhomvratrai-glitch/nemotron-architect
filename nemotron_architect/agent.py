import re
import json
import logging
import difflib
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from nemotron_architect.llm import NemotronClient
from nemotron_architect.tavily_search import TavilySearcher
from nemotron_architect.sandbox import CodeSandbox, ExecutionResult
from nemotron_architect.security_auditor import SecurityAuditor, SecurityFinding

logger = logging.getLogger(__name__)

@dataclass
class BuildReport:
    prompt: str
    success: bool
    files: Dict[str, str] = field(default_factory=dict)
    test_results: Optional[ExecutionResult] = None
    heal_attempts: int = 0
    diagram: str = ""
    security_findings: List[SecurityFinding] = field(default_factory=list)
    healed_diffs: List[Dict[str, Any]] = field(default_factory=list)
    research_summary: List[Dict[str, str]] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

class NemotronArchitectAgent:
    """
    Autonomous Self-Healing Software Engineering Swarm.
    Powered by NVIDIA Nemotron 70B (Nebius Token Factory) & Grounded by Tavily Search.
    """
    def __init__(
        self,
        llm: Optional[NemotronClient] = None,
        searcher: Optional[TavilySearcher] = None,
        auditor: Optional[SecurityAuditor] = None,
        on_log: Optional[Callable[[str], None]] = None
    ):
        self.llm = llm or NemotronClient()
        self.searcher = searcher or TavilySearcher()
        self.auditor = auditor or SecurityAuditor()
        self.on_log = on_log or (lambda msg: None)

    def log(self, message: str):
        logger.info(message)
        self.on_log(message)

    def run(self, user_prompt: str, output_dir: Optional[str] = None) -> BuildReport:
        """
        Executes complete multi-stage autonomous engineering pipeline:
        1. Tavily Research & Live Grounding
        2. Nemotron Architecture Synthesis & Mermaid Diagram
        3. Code & Hermetic Unit Test Generation
        4. AST Static Security Audit
        5. Sandboxed Test Execution
        6. Autonomous Self-Healing Closed-Loop
        """
        report = BuildReport(prompt=user_prompt, success=False)
        self.log(f"🚀 Initializing Nemotron-Architect Swarm for task: '{user_prompt}'")

        # Step 1: Tavily Search Grounding
        self.log("🔍 [Phase 1/6] Fetching live technical documentation via Tavily...")
        research_docs = self.searcher.search_docs(user_prompt)
        report.research_summary = research_docs
        self.log(f"   ✓ Retrieved {len(research_docs)} live technical references.")

        # Step 2: Architecture Planning & Diagram with NVIDIA Nemotron
        self.log("📐 [Phase 2/6] Synthesizing architecture & data flow using NVIDIA Nemotron...")
        plan_prompt = self._build_planning_prompt(user_prompt, research_docs)
        plan_raw = self.llm.generate([{"role": "user", "content": plan_prompt}])
        architecture = self._parse_json_or_fallback(plan_raw, user_prompt)
        report.diagram = self._generate_mermaid_diagram(architecture)
        self.log(f"   ✓ Planned {len(architecture.get('files', []))} core modules with architecture diagram.")

        # Step 3: Code & Test Generation
        self.log("💻 [Phase 3/6] Generating typed, modular implementations and unit test suites...")
        files: Dict[str, str] = {}
        for file_spec in architecture.get("files", []):
            path = file_spec.get("path", "module.py")
            desc = file_spec.get("description", "")
            self.log(f"   ⚙️ Coding module: {path}")
            code = self._generate_file_code(user_prompt, path, desc, files, research_docs)
            files[path] = code
        report.files = files

        # Step 4: AST Security Audit
        self.log("🛡️ [Phase 4/6] Running AST static security audit on generated codebase...")
        findings = self.auditor.audit_all(files)
        report.security_findings = findings
        if findings:
            self.log(f"   ⚠️ Detected {len(findings)} potential security advisories. Running remediation...")
            files = self._remediate_security(files, findings)
            report.files = files
        else:
            self.log("   ✓ Zero security vulnerabilities detected (Clean AST Audit).")

        # Step 5: Sandboxed Verification
        self.log("🧪 [Phase 5/6] Executing hermetic test suite in local sandbox...")
        sandbox = CodeSandbox(base_dir=output_dir)
        for path, content in files.items():
            sandbox.write_file(path, content)

        test_result = sandbox.run_tests()
        report.test_results = test_result

        # Step 6: Autonomous Self-Healing Closed-Loop
        heal_count = 0
        max_heals = 3
        while not test_result.success and heal_count < max_heals:
            heal_count += 1
            self.log(f"⚠️ [Phase 6/6] Test failure detected! Triggering Self-Healing Loop (Attempt {heal_count}/{max_heals})...")
            self.log(f"   Traceback: {test_result.stderr[:200]}...")

            repaired_files = self._self_heal_files(files, test_result.stderr, test_result.stdout)
            
            # Compute diff for report
            for p, new_code in repaired_files.items():
                old_code = files.get(p, "")
                diff = "".join(difflib.unified_diff(
                    old_code.splitlines(keepends=True),
                    new_code.splitlines(keepends=True),
                    fromfile=f"a/{p}",
                    tofile=f"b/{p}"
                ))
                report.healed_diffs.append({"file": p, "diff": diff, "attempt": heal_count})

            files.update(repaired_files)
            report.files = files

            # Update sandbox with repaired files
            for p, c in repaired_files.items():
                sandbox.write_file(p, c)

            test_result = sandbox.run_tests()
            report.test_results = test_result

        report.heal_attempts = heal_count
        if test_result.success:
            self.log("🎉 All tests PASSED with 100% green verification! Project ready.")
            report.success = True
        else:
            self.log(f"❌ Test verification did not pass after {max_heals} attempts.")
            report.success = False

        return report

    def _generate_mermaid_diagram(self, architecture: Dict[str, Any]) -> str:
        files = architecture.get("files", [])
        lines = ["flowchart TD"]
        lines.append("    Client([External Client]) --> App[Application Entry]")
        for f in files:
            path = f.get("path", "file.py")
            safe_id = re.sub(r'[^a-zA-Z0-9]', '_', path)
            desc = f.get("description", path)
            if "test" in path:
                lines.append(f"    {safe_id}[🧪 {path}<br/><small>{desc}</small>]:::test")
            else:
                lines.append(f"    {safe_id}[📦 {path}<br/><small>{desc}</small>]:::impl")
                lines.append(f"    App --> {safe_id}")
        lines.append("    classDef test fill:#ecfdf5,stroke:#10b981,stroke-width:2px;")
        lines.append("    classDef impl fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;")
        return "\n".join(lines)

    def _remediate_security(self, files: Dict[str, str], findings: List[SecurityFinding]) -> Dict[str, str]:
        # Filter dangerous patterns
        cleaned = {}
        for p, code in files.items():
            fixed = code.replace("eval(", "json.loads(").replace("os.system(", "subprocess.run(")
            cleaned[p] = fixed
        return cleaned

    def _build_planning_prompt(self, prompt: str, docs: List[Dict[str, str]]) -> str:
        doc_context = "\n".join([f"- {d['title']}: {d['content'][:150]}" for d in docs])
        return f"""You are NVIDIA Nemotron acting as Chief Software Architect on Nebius Token Factory.
Plan a modular, tested Python software project for:
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
