# ⚡ Nemotron-Architect

> **Autonomous Self-Healing AI Software Engineer**  
> *Powered by **NVIDIA Nemotron 70B** served via **Nebius Token Factory** & Grounded by **Tavily Search**.*

[![NVIDIA Nemotron](https://img.shields.io/badge/Model-NVIDIA%20Nemotron%2070B-76B900?style=for-the-badge&logo=nvidia)](https://nebius.com)
[![Nebius Token Factory](https://img.shields.io/badge/Inference-Nebius%20Token%20Factory-7C3AED?style=for-the-badge)](https://nebius.com)
[![Tavily Search](https://img.shields.io/badge/Grounding-Tavily%20AI-2563EB?style=for-the-badge)](https://tavily.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

Built for the **Nebius × NVIDIA Global AI Hackathon**  
**Category Track:** *Coding and Agentic Engineering Track*  
**Partner Award:** *Best Use of Tavily Award*

---

## 💡 What is Nemotron-Architect?

Existing AI coding assistants suffer from two fatal flaws:
1. **Hallucination of APIs & Deprecated Methods:** Models trained on older snapshots hallucinate non-existent parameters.
2. **Open-Loop Guesswork:** Agents write code and immediately exit without testing, leaving broken imports, syntax errors, or failing edge cases for humans to fix.

**Nemotron-Architect** solves this with an **Autonomous Closed-Loop Engineering Engine**:
- **Live Technical Grounding:** Uses **Tavily Search** to retrieve up-to-the-minute API docs before writing a single line of code.
- **Deep Architectural Reasoning:** Utilizes **NVIDIA Nemotron 70B** (via **Nebius Token Factory**) to design modular architectures and generate typed Python implementations.
- **Hermetic Sandboxed Execution:** Spawns an isolated local runtime to execute AST syntax checks and unit test suites.
- **Autonomous Self-Healing:** When tests fail, Nemotron captures the execution traceback, diagnoses the failure, applies surgical repairs, and re-executes until **100% green verification** is achieved!

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    User([User Requirement / Prompt]) --> Agent[Nemotron-Architect Orchestrator]
    
    subgraph Phase 1: Research & Grounding
        Agent -->|Query Latest Docs| Tavily[Tavily Search Engine]
        Tavily -->|Live Technical Context| Agent
    end

    subgraph Phase 2: Architectural Synthesis
        Agent -->|Spec & File Hierarchy| Nemotron[NVIDIA Nemotron 70B\non Nebius Token Factory]
        Nemotron -->|Modular Schema| Agent
    end

    subgraph Phase 3: Code & Test Generation
        Agent -->|Generate Modules & Unit Tests| Nemotron
        Nemotron -->|Executable Code| Agent
    end

    subgraph Phase 4: Sandboxed Verification
        Agent -->|Write Files & Execute| Sandbox[Isolated Code Sandbox]
        Sandbox -->|Run Pytest & AST Validation| Results{Tests Passed?}
    end

    Results -->|Yes 100% Green| Final[Verified Production Ready Artifact]
    Results -->|No / Traceback| Heal[Phase 5: Self-Healing Loop]
    Heal -->|Traceback Diagnosis & Fix| Nemotron
    Nemotron -->|Surgical Repair| Sandbox
```

---

## 🚀 Key Features

* **⚡ Ultra-Low Latency Inference:** Powered by **Nebius Token Factory** serverless inference for NVIDIA Nemotron.
* **🔍 Tavily Knowledge Injection:** Real-time web search guarantees modern imports and valid syntax for newer libraries.
* **🛡️ Closed-Loop Self-Healing:** Catches runtime exceptions, assertion errors, and missing imports automatically.
* **💻 Dual Interaction Modes:**
  * **Rich Terminal CLI:** Color-coded progress bars, streaming logs, and diagnostic tables.
  * **Web Studio Dashboard:** Beautiful, clean light-mode UI with live Server-Sent Events (SSE) terminal streaming, multi-file code viewer, and 1-click `.zip` export.

---

## 🛠️ Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/bhomvratrai-glitch/nemotron-architect.git
cd nemotron-architect
```

### 2. Configure Environment Variables
Create a `.env` file:
```bash
NEBIUS_API_KEY="your-nebius-api-key"
NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"
NEBIUS_MODEL="nvidia/llama-3.1-nemotron-70b-instruct"
TAVILY_API_KEY="your-tavily-api-key"
```
*(Note: If no API key is provided, the engine automatically runs in self-contained deterministic verification mode for local testing).*

### 3. Run the CLI
```bash
python3 -m nemotron_architect.cli "Build an in-memory Token Bucket rate limiter with pytest tests"
```

### 4. Launch the Web Studio
```bash
python3 -m nemotron_architect.server
```
Open **`http://localhost:8000`** in your browser.

---

## 🧪 Automated Test Verification

Verify the entire test suite hermetically:
```bash
python3 -m pytest tests/test_engine.py -v
```

All 5 core engine test suites pass in **< 0.70 seconds**.

---

## 📜 License
This project is open-source under the [MIT License](LICENSE).
