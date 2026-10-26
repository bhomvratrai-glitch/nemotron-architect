import os
import pytest
from nemotron_architect.config import Config
from nemotron_architect.sandbox import CodeSandbox
from nemotron_architect.tavily_search import TavilySearcher
from nemotron_architect.llm import NemotronClient
from nemotron_architect.agent import NemotronArchitectAgent

def test_sandbox_write_and_syntax():
    sandbox = CodeSandbox()
    try:
        p = sandbox.write_file("hello.py", "def greet(name: str) -> str:\n    return f'Hello, {name}'\n")
        assert p.exists()
        res = sandbox.check_syntax("hello.py")
        assert res.success is True
        assert res.exit_code == 0
    finally:
        sandbox.cleanup()

def test_sandbox_run_passing_test():
    sandbox = CodeSandbox()
    try:
        sandbox.write_file("calc.py", "def add(a, b):\n    return a + b\n")
        sandbox.write_file("test_calc.py", "from calc import add\ndef test_add():\n    assert add(2, 3) == 5\n")
        res = sandbox.run_tests("test_calc.py")
        assert res.success is True
        assert res.exit_code == 0
    finally:
        sandbox.cleanup()

def test_tavily_searcher_fallback():
    searcher = TavilySearcher(api_key="")
    docs = searcher.search_docs("FastAPI rate limiter")
    assert len(docs) >= 1
    assert "FastAPI rate limiter" in docs[0]["title"]

def test_nemotron_client_fallback():
    client = NemotronClient(api_key="dummy-key")
    resp = client.generate([{"role": "user", "content": "plan architecture and files for calculator"}])
    assert "files" in resp or "calculator" in resp.lower()

def test_agent_end_to_end():
    logs = []
    agent = NemotronArchitectAgent(
        llm=NemotronClient(api_key="dummy-key"),
        searcher=TavilySearcher(api_key=""),
        on_log=lambda m: logs.append(m)
    )
    report = agent.run("build a sample calculator")
    assert len(report.files) >= 1
    assert len(logs) > 0
