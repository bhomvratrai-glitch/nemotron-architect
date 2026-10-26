document.addEventListener("DOMContentLoaded", () => {
  const promptInput = document.getElementById("promptInput");
  const runBtn = document.getElementById("runBtn");
  const downloadBtn = document.getElementById("downloadBtn");
  const terminalLogs = document.getElementById("terminalLogs");
  const engineStatus = document.getElementById("engineStatus");
  const filesTabs = document.getElementById("filesTabs");
  const codeContent = document.getElementById("codeContent");
  const testPill = document.getElementById("testPill");
  const statFiles = document.getElementById("statFiles");
  const statHeals = document.getElementById("statHeals");
  const statStatus = document.getElementById("statStatus");

  let currentFiles = {};
  let activeTab = "welcome";

  // Preset chips handler
  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      promptInput.value = chip.getAttribute("data-preset");
      promptInput.focus();
    });
  });

  // Log line appender
  function appendLog(text) {
    const line = document.createElement("div");
    line.className = "log-line";
    if (text.includes("✓") || text.includes("PASSED")) line.classList.add("green");
    else if (text.includes("⚠️") || text.includes("Phase")) line.classList.add("yellow");
    else if (text.includes("❌") || text.includes("FAILED")) line.classList.add("red");
    else line.classList.add("dim");

    line.textContent = text;
    terminalLogs.appendChild(line);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
  }

  const diagramTabBtn = document.getElementById("diagramTabBtn");
  const preBlock = document.getElementById("preBlock");
  const diagramContainer = document.getElementById("diagramContainer");
  const securityPill = document.getElementById("securityPill");
  const statSec = document.getElementById("statSec");

  let currentDiagram = "";

  if (window.mermaid) {
    mermaid.initialize({ startOnLoad: false, theme: "neutral" });
  }

  // Diagram tab click
  if (diagramTabBtn) {
    diagramTabBtn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      diagramTabBtn.classList.add("active");
      preBlock.style.display = "none";
      diagramContainer.style.display = "block";
      if (currentDiagram) {
        diagramContainer.innerHTML = currentDiagram;
        diagramContainer.removeAttribute("data-processed");
        if (window.mermaid) {
          mermaid.run({ nodes: [diagramContainer] });
        }
      } else {
        diagramContainer.textContent = "No diagram generated yet.";
      }
    });
  }

  // Switch active file tab
  function renderTabs(files) {
    filesTabs.innerHTML = "";
    const paths = Object.keys(files);
    if (paths.length === 0) return;

    // Add diagram button back
    const diagBtn = document.createElement("button");
    diagBtn.className = "tab-btn";
    diagBtn.textContent = "📐 Architecture Diagram";
    diagBtn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      diagBtn.classList.add("active");
      preBlock.style.display = "none";
      diagramContainer.style.display = "block";
      if (currentDiagram) {
        diagramContainer.innerHTML = currentDiagram;
        diagramContainer.removeAttribute("data-processed");
        if (window.mermaid) {
          mermaid.run({ nodes: [diagramContainer] });
        }
      }
    });
    filesTabs.appendChild(diagBtn);

    paths.forEach((path, index) => {
      const btn = document.createElement("button");
      btn.className = `tab-btn ${index === 0 ? "active" : ""}`;
      btn.textContent = path;
      btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        preBlock.style.display = "block";
        diagramContainer.style.display = "none";
        codeContent.textContent = files[path];
      });
      filesTabs.appendChild(btn);
    });

    // Set first file content
    preBlock.style.display = "block";
    diagramContainer.style.display = "none";
    codeContent.textContent = files[paths[0]];
  }

  // Run Agent
  runBtn.addEventListener("click", async () => {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      alert("Please enter a project or feature prompt.");
      return;
    }

    runBtn.disabled = true;
    downloadBtn.disabled = true;
    engineStatus.textContent = "Autonomous Agent Running...";
    engineStatus.className = "status-indicator running";
    terminalLogs.innerHTML = "";
    appendLog(`Dispatching mission: "${prompt}"`);

    testPill.className = "test-pill";
    testPill.querySelector(".pill-text").textContent = "Synthesizing...";

    try {
      // 1. Trigger generate
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prompt })
      });

      if (!res.ok) {
        throw new Error("Failed to start agent task.");
      }

      // 2. Stream logs via SSE
      const evtSource = new EventSource("/api/logs/stream");

      evtSource.onmessage = async (e) => {
        const data = JSON.parse(e.data);
        const msg = data.message;

        if (msg.startsWith("__BUILD_FINISHED__")) {
          evtSource.close();
          await fetchReport();
          runBtn.disabled = false;
          engineStatus.textContent = "Task Complete";
          engineStatus.className = "status-indicator";
        } else {
          appendLog(msg);
        }
      };

      evtSource.onerror = () => {
        evtSource.close();
        runBtn.disabled = false;
        engineStatus.textContent = "Ready";
        engineStatus.className = "status-indicator";
      };

    } catch (err) {
      appendLog(`Error: ${err.message}`);
      runBtn.disabled = false;
      engineStatus.textContent = "Error";
      engineStatus.className = "status-indicator";
    }
  });

  // Fetch complete report
  async function fetchReport() {
    try {
      const res = await fetch("/api/report");
      const report = await res.json();

      if (report.has_report) {
        currentFiles = report.files;
        currentDiagram = report.diagram || "";
        renderTabs(currentFiles);

        statFiles.textContent = Object.keys(currentFiles).length;
        statHeals.textContent = report.heal_attempts;

        if (statSec) {
          const count = report.security_count || 0;
          statSec.textContent = count === 0 ? "0 (Clean)" : `${count} Detected`;
          statSec.style.color = count === 0 ? "var(--accent-green)" : "var(--accent-red)";
        }

        if (report.success) {
          testPill.className = "test-pill passed";
          testPill.querySelector(".pill-text").textContent = "100% Tests Passed";
          statStatus.textContent = "Verified Green";
          statStatus.style.color = "var(--accent-green)";
          downloadBtn.disabled = false;
        } else {
          testPill.className = "test-pill failed";
          testPill.querySelector(".pill-text").textContent = "Test Failure";
          statStatus.textContent = "Failed";
          statStatus.style.color = "var(--accent-red)";
        }
      }
    } catch (e) {
      console.error("Failed to load report", e);
    }
  }

  // Download project as ZIP
  downloadBtn.addEventListener("click", () => {
    window.location.href = "/api/download/zip";
  });
});
