/**
 * AI Agents Learning Hub — Progress Tracking & Lab Filters
 *
 * Features:
 * 1. Lab completion checkboxes (localStorage)
 * 2. Progress bars on path pages
 * 3. Cost filter buttons on All Labs page
 * 4. Certificate generation
 */

(function () {
  "use strict";

  const STORAGE_KEY = "ai-hub-progress";

  // ── Progress Storage ──────────────────────────────────────────────────
  function getProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    } catch {
      return {};
    }
  }

  function setCompleted(labId, done) {
    const progress = getProgress();
    if (done) {
      progress[labId] = new Date().toISOString();
    } else {
      delete progress[labId];
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  }

  function isCompleted(labId) {
    return !!getProgress()[labId];
  }

  // ── Lab Completion Checkbox ───────────────────────────────────────────
  function addCompletionCheckbox() {
    // Only on lab pages (URL contains /labs/lab-)
    if (!window.location.pathname.includes("/labs/lab-")) return;

    const match = window.location.pathname.match(/lab-(\d+)/);
    if (!match) return;
    const labId = "lab-" + match[1];

    // Find the lab title (h1)
    const h1 = document.querySelector("article h1");
    if (!h1) return;

    const wrapper = document.createElement("div");
    wrapper.className = "lab-completion";
    wrapper.innerHTML = `
      <label class="completion-toggle">
        <input type="checkbox" id="lab-done" ${isCompleted(labId) ? "checked" : ""}>
        <span class="completion-label">${isCompleted(labId) ? "✅ Completed!" : "Mark as completed"}</span>
      </label>
    `;

    h1.after(wrapper);

    const checkbox = document.getElementById("lab-done");
    const label = wrapper.querySelector(".completion-label");
    checkbox.addEventListener("change", function () {
      setCompleted(labId, this.checked);
      label.textContent = this.checked ? "✅ Completed!" : "Mark as completed";
      // Update any progress bars on the page
      updateProgressBars();
    });
  }

  // ── Progress Bars ─────────────────────────────────────────────────────
  function updateProgressBars() {
    document.querySelectorAll(".progress-bar-container").forEach(function (el) {
      const labs = el.dataset.labs ? el.dataset.labs.split(",") : [];
      if (!labs.length) return;

      const completed = labs.filter(function (id) {
        return isCompleted(id.trim());
      }).length;
      const pct = Math.round((completed / labs.length) * 100);

      el.querySelector(".progress-fill").style.width = pct + "%";
      el.querySelector(".progress-text").textContent =
        completed + "/" + labs.length + " completed (" + pct + "%)";
    });
  }

  // ── Cost Filters ──────────────────────────────────────────────────────
  function addCostFilters() {
    // Only on the All Labs page
    const heading = document.querySelector('h1');
    if (!heading || heading.textContent.trim() !== "All Labs") return;

    const filterBar = document.createElement("div");
    filterBar.className = "lab-filters";
    filterBar.innerHTML = `
      <span class="filter-label">Filter by cost:</span>
      <button class="filter-btn active" data-filter="all">All</button>
      <button class="filter-btn" data-filter="free">✅ Free Only</button>
      <button class="filter-btn" data-filter="azure">⚠️ Azure</button>
      <button class="filter-btn" data-filter="m365">⚠️ M365</button>
    `;

    // Insert after the first paragraph
    const firstP = heading.nextElementSibling;
    if (firstP) {
      firstP.after(filterBar);
    }

    filterBar.querySelectorAll(".filter-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        filterBar
          .querySelectorAll(".filter-btn")
          .forEach(function (b) { b.classList.remove("active"); });
        this.classList.add("active");

        const filter = this.dataset.filter;
        document.querySelectorAll("article table tbody tr").forEach(function (row) {
          const costCell = row.cells ? row.cells[row.cells.length - 1] : null;
          if (!costCell) return;
          const cost = costCell.textContent.trim().toLowerCase();
          if (filter === "all") {
            row.style.display = "";
          } else if (filter === "free") {
            row.style.display = cost.includes("free") ? "" : "none";
          } else if (filter === "azure") {
            row.style.display = cost.includes("azure") ? "" : "none";
          } else if (filter === "m365") {
            row.style.display = cost.includes("m365") ? "" : "none";
          }
        });
      });
    });
  }

  // ── Stats Dashboard ───────────────────────────────────────────────────
  function addStatsDashboard() {
    const heading = document.querySelector('h1');
    if (!heading || heading.textContent.trim() !== "All Labs") return;

    const progress = getProgress();
    const total = document.querySelectorAll("article table tbody tr").length;
    const completed = Object.keys(progress).length;
    const pct = total > 0 ? Math.round((completed / total) * 100) : 0;

    if (completed > 0) {
      const stats = document.createElement("div");
      stats.className = "hub-stats";
      stats.innerHTML = `
        <div class="stats-card">
          <span class="stats-number">${completed}</span>
          <span class="stats-label">Labs Completed</span>
        </div>
        <div class="stats-card">
          <span class="stats-number">${pct}%</span>
          <span class="stats-label">Progress</span>
        </div>
        <div class="stats-progress">
          <div class="progress-fill" style="width: ${pct}%"></div>
        </div>
      `;
      heading.after(stats);
    }
  }

  // ── Certificate Generator ─────────────────────────────────────────────
  function addCertificateButton() {
    // Only on path pages
    if (!window.location.pathname.includes("/paths/")) return;

    const tables = document.querySelectorAll("article table");
    if (!tables.length) return;

    // Find lab links in the table
    const labLinks = document.querySelectorAll('article table a[href*="lab-"]');
    const labIds = [];
    labLinks.forEach(function (a) {
      const m = a.href.match(/lab-(\d+)/);
      if (m) labIds.push("lab-" + m[1]);
    });

    if (!labIds.length) return;

    const completed = labIds.filter(function (id) { return isCompleted(id); }).length;
    const allDone = completed === labIds.length;

    // Add progress bar
    const h2 = document.querySelector('h2[id*="path-labs"]') ||
               Array.from(document.querySelectorAll("h2")).find(function (h) {
                 return h.textContent.includes("Path Labs");
               });

    if (h2) {
      const pct = Math.round((completed / labIds.length) * 100);
      const bar = document.createElement("div");
      bar.className = "path-progress";
      bar.innerHTML = `
        <div class="progress-bar-container" data-labs="${labIds.join(",")}">
          <div class="progress-fill" style="width: ${pct}%"></div>
          <span class="progress-text">${completed}/${labIds.length} completed (${pct}%)</span>
        </div>
      `;
      h2.after(bar);

      if (allDone) {
        const certBtn = document.createElement("button");
        certBtn.className = "cert-button";
        certBtn.textContent = "🎓 Generate Certificate";
        certBtn.onclick = function () { generateCertificate(); };
        bar.after(certBtn);
      }
    }
  }

  function generateCertificate() {
    const pathName = document.querySelector("h1")
      ? document.querySelector("h1").textContent.trim()
      : "Learning Path";
    const userName = prompt("Enter your name for the certificate:");
    if (!userName) return;

    const date = new Date().toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });

    const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" font-family="Segoe UI, Arial, sans-serif">
  <rect width="800" height="600" fill="#fafbfc" rx="16"/>
  <rect x="20" y="20" width="760" height="560" fill="none" stroke="#6d28d9" stroke-width="3" rx="12"/>
  <rect x="30" y="30" width="740" height="540" fill="none" stroke="#6d28d9" stroke-width="1" rx="10" stroke-dasharray="8,4"/>
  <text x="400" y="100" text-anchor="middle" font-size="28" font-weight="700" fill="#1e293b">🎓 Certificate of Completion</text>
  <text x="400" y="150" text-anchor="middle" font-size="14" fill="#64748b">AI Agents Learning Hub</text>
  <line x1="200" y1="180" x2="600" y2="180" stroke="#e2e8f0" stroke-width="1"/>
  <text x="400" y="230" text-anchor="middle" font-size="16" fill="#475569">This certifies that</text>
  <text x="400" y="280" text-anchor="middle" font-size="32" font-weight="700" fill="#6d28d9">${userName}</text>
  <text x="400" y="330" text-anchor="middle" font-size="16" fill="#475569">has successfully completed all labs in</text>
  <text x="400" y="380" text-anchor="middle" font-size="24" font-weight="600" fill="#1e293b">${pathName}</text>
  <text x="400" y="440" text-anchor="middle" font-size="14" fill="#64748b">${date}</text>
  <line x1="200" y1="480" x2="600" y2="480" stroke="#e2e8f0" stroke-width="1"/>
  <text x="400" y="520" text-anchor="middle" font-size="12" fill="#94a3b8">github.com/lcarli/AI-LearningHub</text>
  <text x="400" y="545" text-anchor="middle" font-size="10" fill="#cbd5e1">Verified by completion tracking • Generated client-side</text>
</svg>`;

    const blob = new Blob([svg], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "certificate-" + pathName.replace(/[^a-zA-Z0-9]/g, "-") + ".svg";
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── Init ──────────────────────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    addCompletionCheckbox();
    addCostFilters();
    addStatsDashboard();
    addCertificateButton();
  });

  // MkDocs Material uses instant loading — re-run on navigation
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () {
      addCompletionCheckbox();
      addCostFilters();
      addStatsDashboard();
      addCertificateButton();
    });
  }
})();
