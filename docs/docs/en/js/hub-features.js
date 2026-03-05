/**
 * AI Agents Learning Hub — Progress Tracking & Lab Filters
 *
 * Features:
 * 1. Lab completion checkboxes (localStorage — browser-only)
 * 2. Progress bars on path pages
 * 3. Cost filter buttons on All Labs page
 * 4. Certificate generation
 * 5. Multilingual support (EN/PT/FR)
 */

(function () {
  "use strict";

  var STORAGE_KEY = "ai-hub-progress";

  // ── i18n Labels ───────────────────────────────────────────────────────
  var LABELS = {
    en: {
      markComplete: "Mark as completed",
      completed: "✅ Completed!",
      filterLabel: "Filter by cost:",
      filterAll: "All",
      filterFree: "✅ Free Only",
      filterAzure: "⚠️ Azure",
      filterM365: "⚠️ M365",
      labsCompleted: "Labs Completed",
      progress: "Progress",
      generateCert: "🎓 Generate Certificate",
      certTitle: "🎓 Certificate of Completion",
      certCertifies: "This certifies that",
      certCompleted: "has successfully completed all labs in",
      enterName: "Enter your name for the certificate:",
      progressSaved: "Progress is saved in your browser (localStorage)",
      completedOf: "completed"
    },
    pt: {
      markComplete: "Marcar como concluído",
      completed: "✅ Concluído!",
      filterLabel: "Filtrar por custo:",
      filterAll: "Todos",
      filterFree: "✅ Apenas Gratuitos",
      filterAzure: "⚠️ Azure",
      filterM365: "⚠️ M365",
      labsCompleted: "Labs Concluídos",
      progress: "Progresso",
      generateCert: "🎓 Gerar Certificado",
      certTitle: "🎓 Certificado de Conclusão",
      certCertifies: "Isto certifica que",
      certCompleted: "concluiu com sucesso todos os labs em",
      enterName: "Digite seu nome para o certificado:",
      progressSaved: "Progresso salvo no seu navegador (localStorage)",
      completedOf: "concluído(s)"
    },
    fr: {
      markComplete: "Marquer comme terminé",
      completed: "✅ Terminé !",
      filterLabel: "Filtrer par coût :",
      filterAll: "Tous",
      filterFree: "✅ Gratuits uniquement",
      filterAzure: "⚠️ Azure",
      filterM365: "⚠️ M365",
      labsCompleted: "Labs Terminés",
      progress: "Progrès",
      generateCert: "🎓 Générer le Certificat",
      certTitle: "🎓 Certificat de Réussite",
      certCertifies: "Ceci certifie que",
      certCompleted: "a terminé avec succès tous les labs de",
      enterName: "Entrez votre nom pour le certificat :",
      progressSaved: "Progrès sauvegardé dans votre navigateur (localStorage)",
      completedOf: "terminé(s)"
    }
  };

  function getLang() {
    var path = window.location.pathname;
    if (path.indexOf("/pt/") !== -1) return "pt";
    if (path.indexOf("/fr/") !== -1) return "fr";
    return "en";
  }

  function t(key) {
    var lang = getLang();
    return (LABELS[lang] && LABELS[lang][key]) || LABELS.en[key] || key;
  }

  // ── Progress Storage ──────────────────────────────────────────────────
  function getProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    } catch (e) {
      return {};
    }
  }

  function setCompleted(labId, done) {
    var progress = getProgress();
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

  // ── Cleanup: remove previously injected elements ──────────────────────
  function cleanup() {
    var selectors = [".lab-completion", ".lab-filters", ".hub-stats", ".path-progress", ".cert-button"];
    selectors.forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (el) { el.remove(); });
    });
  }

  // ── Lab Completion Checkbox ───────────────────────────────────────────
  function addCompletionCheckbox() {
    if (window.location.pathname.indexOf("/labs/lab-") === -1) return;

    var match = window.location.pathname.match(/lab-(\d+)/);
    if (!match) return;
    var labId = "lab-" + match[1];

    var h1 = document.querySelector("article h1");
    if (!h1) return;

    var wrapper = document.createElement("div");
    wrapper.className = "lab-completion";
    var checked = isCompleted(labId);
    wrapper.innerHTML =
      '<label class="completion-toggle">' +
      '<input type="checkbox" id="lab-done" ' + (checked ? "checked" : "") + ">" +
      '<span class="completion-label">' + (checked ? t("completed") : t("markComplete")) + "</span>" +
      "</label>" +
      '<span class="completion-note">' + t("progressSaved") + "</span>";

    h1.after(wrapper);

    var checkbox = document.getElementById("lab-done");
    var label = wrapper.querySelector(".completion-label");
    checkbox.addEventListener("change", function () {
      setCompleted(labId, this.checked);
      label.textContent = this.checked ? t("completed") : t("markComplete");
    });
  }

  // ── Cost Filters ──────────────────────────────────────────────────────
  function addCostFilters() {
    var heading = document.querySelector("h1");
    if (!heading) return;
    var text = heading.textContent.trim();
    if (text !== "All Labs" && text !== "Todos os Labs" && text !== "Tous les Labs") return;

    var filterBar = document.createElement("div");
    filterBar.className = "lab-filters";
    filterBar.innerHTML =
      '<span class="filter-label">' + t("filterLabel") + "</span>" +
      '<button class="filter-btn active" data-filter="all">' + t("filterAll") + "</button>" +
      '<button class="filter-btn" data-filter="free">' + t("filterFree") + "</button>" +
      '<button class="filter-btn" data-filter="azure">' + t("filterAzure") + "</button>" +
      '<button class="filter-btn" data-filter="m365">' + t("filterM365") + "</button>";

    var firstP = heading.nextElementSibling;
    if (firstP) firstP.after(filterBar);

    filterBar.querySelectorAll(".filter-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        filterBar.querySelectorAll(".filter-btn").forEach(function (b) { b.classList.remove("active"); });
        this.classList.add("active");
        var filter = this.dataset.filter;
        document.querySelectorAll("article table tbody tr").forEach(function (row) {
          var costCell = row.cells ? row.cells[row.cells.length - 1] : null;
          if (!costCell) return;
          var cost = costCell.textContent.trim().toLowerCase();
          if (filter === "all") { row.style.display = ""; }
          else if (filter === "free") { row.style.display = cost.indexOf("free") !== -1 ? "" : "none"; }
          else if (filter === "azure") { row.style.display = cost.indexOf("azure") !== -1 ? "" : "none"; }
          else if (filter === "m365") { row.style.display = cost.indexOf("m365") !== -1 ? "" : "none"; }
        });
      });
    });
  }

  // ── Stats Dashboard ───────────────────────────────────────────────────
  function addStatsDashboard() {
    var heading = document.querySelector("h1");
    if (!heading) return;
    var text = heading.textContent.trim();
    if (text !== "All Labs" && text !== "Todos os Labs" && text !== "Tous les Labs") return;

    var progress = getProgress();
    var completed = Object.keys(progress).length;
    if (completed === 0) return;

    var total = document.querySelectorAll("article table tbody tr").length;
    var pct = total > 0 ? Math.round((completed / total) * 100) : 0;

    var stats = document.createElement("div");
    stats.className = "hub-stats";
    stats.innerHTML =
      '<div class="stats-card"><span class="stats-number">' + completed + '</span><span class="stats-label">' + t("labsCompleted") + "</span></div>" +
      '<div class="stats-card"><span class="stats-number">' + pct + '%</span><span class="stats-label">' + t("progress") + "</span></div>" +
      '<div class="stats-progress"><div class="progress-fill" style="width: ' + pct + '%"></div></div>';
    heading.after(stats);
  }

  // ── Certificate Generator ─────────────────────────────────────────────
  function addCertificateButton() {
    if (window.location.pathname.indexOf("/paths/") === -1) return;

    var labLinks = document.querySelectorAll('article table a[href*="lab-"]');
    var labIds = [];
    labLinks.forEach(function (a) {
      var m = a.href.match(/lab-(\d+)/);
      if (m) labIds.push("lab-" + m[1]);
    });
    if (!labIds.length) return;

    var completed = labIds.filter(function (id) { return isCompleted(id); }).length;
    var allDone = completed === labIds.length;
    var pct = Math.round((completed / labIds.length) * 100);

    var h2 = Array.from(document.querySelectorAll("h2")).find(function (h) {
      return h.textContent.indexOf("Path Labs") !== -1 ||
             h.textContent.indexOf("Laboratórios") !== -1 ||
             h.textContent.indexOf("Parcours") !== -1;
    });
    if (!h2) return;

    var bar = document.createElement("div");
    bar.className = "path-progress";
    bar.innerHTML =
      '<div class="progress-bar-container">' +
      '<div class="progress-fill" style="width: ' + pct + '%"></div>' +
      '<span class="progress-text">' + completed + "/" + labIds.length + " " + t("completedOf") + " (" + pct + "%)</span>" +
      "</div>";
    h2.after(bar);

    if (allDone) {
      var certBtn = document.createElement("button");
      certBtn.className = "cert-button";
      certBtn.textContent = t("generateCert");
      certBtn.onclick = function () { generateCertificate(); };
      bar.after(certBtn);
    }
  }

  function generateCertificate() {
    var pathName = document.querySelector("h1") ? document.querySelector("h1").textContent.trim() : "Learning Path";
    var userName = prompt(t("enterName"));
    if (!userName) return;

    var date = new Date().toLocaleDateString(getLang() === "pt" ? "pt-BR" : getLang() === "fr" ? "fr-FR" : "en-US", {
      year: "numeric", month: "long", day: "numeric"
    });

    var svg = '<?xml version="1.0" encoding="UTF-8"?>' +
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" font-family="Segoe UI, Arial, sans-serif">' +
      '<rect width="800" height="600" fill="#fafbfc" rx="16"/>' +
      '<rect x="20" y="20" width="760" height="560" fill="none" stroke="#6d28d9" stroke-width="3" rx="12"/>' +
      '<rect x="30" y="30" width="740" height="540" fill="none" stroke="#6d28d9" stroke-width="1" rx="10" stroke-dasharray="8,4"/>' +
      '<text x="400" y="100" text-anchor="middle" font-size="28" font-weight="700" fill="#1e293b">' + t("certTitle") + "</text>" +
      '<text x="400" y="150" text-anchor="middle" font-size="14" fill="#64748b">AI Agents Learning Hub</text>' +
      '<line x1="200" y1="180" x2="600" y2="180" stroke="#e2e8f0" stroke-width="1"/>' +
      '<text x="400" y="230" text-anchor="middle" font-size="16" fill="#475569">' + t("certCertifies") + "</text>" +
      '<text x="400" y="280" text-anchor="middle" font-size="32" font-weight="700" fill="#6d28d9">' + userName + "</text>" +
      '<text x="400" y="330" text-anchor="middle" font-size="16" fill="#475569">' + t("certCompleted") + "</text>" +
      '<text x="400" y="380" text-anchor="middle" font-size="24" font-weight="600" fill="#1e293b">' + pathName + "</text>" +
      '<text x="400" y="440" text-anchor="middle" font-size="14" fill="#64748b">' + date + "</text>" +
      '<line x1="200" y1="480" x2="600" y2="480" stroke="#e2e8f0" stroke-width="1"/>' +
      '<text x="400" y="520" text-anchor="middle" font-size="12" fill="#94a3b8">github.com/lcarli/AI-LearningHub</text>' +
      "</svg>";

    var blob = new Blob([svg], { type: "image/svg+xml" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "certificate-" + pathName.replace(/[^a-zA-Z0-9]/g, "-") + ".svg";
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── Init ──────────────────────────────────────────────────────────────
  function init() {
    cleanup();
    addCompletionCheckbox();
    addCostFilters();
    addStatsDashboard();
    addCertificateButton();
  }

  // MkDocs Material instant loading
  if (typeof document$ !== "undefined") {
    document$.subscribe(function () { init(); });
  } else {
    document.addEventListener("DOMContentLoaded", function () { init(); });
  }
})();
