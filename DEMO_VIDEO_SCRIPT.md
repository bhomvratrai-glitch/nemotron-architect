# 🎬 2-Minute Demo Video Script — Nemotron-Architect

> **Target Duration:** 1:45 – 2:00 minutes  
> **Tool to Record:** QuickTime Player / OBS / Loom (Screen recording of Web Studio + Terminal).

---

### Segment 1: The Problem (0:00 – 0:25)
* **Visual:** Browser showing standard AI code outputs with broken imports or failing tests.
* **Narration:**
  > *"Every developer has experienced this frustration: you ask an AI coding assistant to write a complex module, and it outputs code with deprecated methods, hallucinated APIs, and zero unit tests. When you run it, it breaks. Current AI models guess, generate, and terminate with zero verification."*

---

### Segment 2: Introducing Nemotron-Architect (0:25 – 0:50)
* **Visual:** Switch to **Nemotron-Architect Studio** (`http://localhost:8000`), showing clean modern dashboard with NVIDIA Nemotron & Nebius Token Factory badges.
* **Narration:**
  > *"Meet **Nemotron-Architect**—an autonomous, self-healing software engineer built for the Nebius x NVIDIA Hackathon. Powered by **NVIDIA Nemotron 70B** served on **Nebius Token Factory**, and grounded in real-time by **Tavily Search**, Nemotron-Architect doesn't just guess code—it designs, verifies, security audits, and self-heals in a closed loop until tests pass with 100% green status."*

---

### Segment 3: Live Autonomous Demo & Self-Healing (0:50 – 1:30)
* **Visual:**
  1. Click the template **"⏱️ Rate Limiter"** in Web Studio.
  2. Click **"Run Autonomous Engineer"**.
  3. Show the live terminal stream:
     - Phase 1: Tavily fetching live documentation.
     - Phase 2: Nemotron synthesizing the modular file architecture.
     - Phase 3: Writing typed code and pytest suites.
     - Phase 4: AST Security Audit (Clean).
     - Phase 5: Sandbox runs tests -> shows test failure trigger!
     - Phase 6: Nemotron diagnoses error traceback and surgically self-heals -> **All tests PASSED!**
* **Narration:**
  > *"Let's dispatch a task: building an in-memory Token Bucket rate limiter. Notice the live orchestrator: first, Tavily fetches fresh docs. Next, Nemotron 70B structures the project. When our sandboxed pytest suite runs, an edge case fails—and here is where the magic happens. Nemotron-Architect captures the stack trace, diagnoses the root cause, applies a surgical fix, and re-executes. Result: 100% verified green tests!"*

---

### Segment 4: Architecture Diagram & One-Click Export (1:30 – 1:50)
* **Visual:**
  1. Click **"📐 Architecture Diagram"** tab to show the rendered Mermaid graph.
  2. Click **"Download .ZIP"** to demonstrate instant export.
* **Narration:**
  > *"Nemotron-Architect also generates an interactive visual architecture diagram showing client flow and module relationships, and lets developers download the verified codebase as a clean zip file."*

---

### Segment 5: Conclusion & Impact (1:50 – 2:00)
* **Visual:** GitHub repo page showing 13 passing tests.
* **Narration:**
  > *"By combining NVIDIA Nemotron's deep reasoning with Nebius Token Factory's ultra-fast serverless inference and closed-loop self-healing, we're making autonomous software engineering reliable, secure, and production-ready. Thank you!"*
