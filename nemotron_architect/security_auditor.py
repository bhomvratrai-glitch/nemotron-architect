import ast
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SecurityFinding:
    severity: str  # HIGH, MEDIUM, LOW
    rule_id: str
    message: str
    file_path: str
    line_number: int

class SecurityAuditor:
    """
    AST-level static security auditor for generated code.
    Detects dangerous functions (eval, exec), hardcoded credentials, and unsafe subprocess calls.
    """
    DANGEROUS_CALLS = {
        "eval": ("HIGH", "SEC-001", "Use of dangerous eval() function"),
        "exec": ("HIGH", "SEC-002", "Use of dangerous exec() function"),
        "os.system": ("HIGH", "SEC-003", "Use of unescaped shell execution via os.system"),
        "subprocess.Popen": ("MEDIUM", "SEC-004", "Direct process spawn; verify shell=False"),
    }

    SUSPICIOUS_KEY_NAMES = ["password", "secret", "private_key", "api_key", "token"]

    def audit_file(self, file_path: str, code: str) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return findings

        for node in ast.walk(tree):
            # Check function calls
            if isinstance(node, ast.Call):
                call_name = ""
                if isinstance(node.func, ast.Name):
                    call_name = node.func.id
                elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    call_name = f"{node.func.value.id}.{node.func.attr}"

                if call_name in self.DANGEROUS_CALLS:
                    sev, rule_id, msg = self.DANGEROUS_CALLS[call_name]
                    findings.append(SecurityFinding(
                        severity=sev,
                        rule_id=rule_id,
                        message=msg,
                        file_path=file_path,
                        line_number=getattr(node, "lineno", 1)
                    ))

            # Check hardcoded literal secrets
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name_lower = target.id.lower()
                        if any(k in name_lower for k in self.SUSPICIOUS_KEY_NAMES):
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                if len(node.value.value) > 8 and not node.value.value.startswith("env:"):
                                    findings.append(SecurityFinding(
                                        severity="MEDIUM",
                                        rule_id="SEC-005",
                                        message=f"Possible hardcoded secret in variable '{target.id}'. Use environment variables.",
                                        file_path=file_path,
                                        line_number=getattr(node, "lineno", 1)
                                    ))

        return findings

    def audit_all(self, files: Dict[str, str]) -> List[SecurityFinding]:
        all_findings = []
        for path, content in files.items():
            all_findings.extend(self.audit_file(path, content))
        return all_findings
