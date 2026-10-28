/**
 * AI Learning Hub — catalog, accessible widgets, and local progress.
 */
(function (root, factory) {
  var api = factory(root);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.AILearningHub = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function (root) {
  "use strict";

  var STORAGE_KEY = "ai-hub-progress";
  var LABELS = {
    en: {
      markComplete: "Mark as completed", completed: "Completed",
      progressSaved: "Saved only in this browser", continueTitle: "Continue learning",
      continueEmpty: "Complete a lab to build your personal learning history.",
      catalogTitle: "Explore the catalog", search: "Search labs",
      results: "labs found", noResults: "No labs match these filters.",
      reset: "Reset filters", all: "All", free: "Free", simulated: "Simulation available",
      tokens: "tokens", remaining: "remaining", deterministic: "more deterministic",
      diverse: "more diverse", balanced: "balanced",
      question: "Question", submit: "Submit answer", next: "Next question",
      correct: "Correct", incorrect: "Review the explanation", score: "Score",
      journey: "Journey", level: "Level", cost: "Cost", simulation: "Simulation",
      role: "Role", time: "Time", technology: "Technology", language: "Language", sort: "Sort",
      challengeValid: "Correct code. Challenge completed!",
      challengeInvalid: "Code not recognized. Run the local validator and try again."
    },
    pt: {
      markComplete: "Marcar como concluído", completed: "Concluído",
      progressSaved: "Salvo somente neste navegador", continueTitle: "Continue aprendendo",
      continueEmpty: "Conclua um lab para criar seu histórico pessoal de aprendizado.",
      catalogTitle: "Explore o catálogo", search: "Buscar labs",
      results: "labs encontrados", noResults: "Nenhum lab corresponde a estes filtros.",
      reset: "Limpar filtros", all: "Todos", free: "Grátis", simulated: "Simulação disponível",
      tokens: "tokens", remaining: "restantes", deterministic: "mais determinística",
      diverse: "mais diversa", balanced: "equilibrada",
      question: "Questão", submit: "Enviar resposta", next: "Próxima questão",
      correct: "Correto", incorrect: "Revise a explicação", score: "Pontuação",
      journey: "Jornada", level: "Nível", cost: "Custo", simulation: "Simulação",
      role: "Papel", time: "Tempo", technology: "Tecnologia", language: "Idioma", sort: "Ordenar",
      challengeValid: "Código correto. Desafio concluído!",
      challengeInvalid: "Código não reconhecido. Rode o validador local e tente novamente."
    },
    fr: {
      markComplete: "Marquer comme terminé", completed: "Terminé",
      progressSaved: "Enregistré uniquement dans ce navigateur", continueTitle: "Continuer à apprendre",
      continueEmpty: "Terminez un lab pour créer votre historique personnel d'apprentissage.",
      catalogTitle: "Explorer le catalogue", search: "Rechercher des labs",
      results: "labs trouvés", noResults: "Aucun lab ne correspond à ces filtres.",
      reset: "Réinitialiser", all: "Tous", free: "Gratuit", simulated: "Simulation disponible",
      tokens: "tokens", remaining: "restants", deterministic: "plus déterministe",
      diverse: "plus diverse", balanced: "équilibrée",
      question: "Question", submit: "Valider la réponse", next: "Question suivante",
      correct: "Correct", incorrect: "Relisez l'explication", score: "Score",
      journey: "Parcours", level: "Niveau", cost: "Coût", simulation: "Simulation",
      role: "Rôle", time: "Durée", technology: "Technologie", language: "Langue", sort: "Trier",
      challengeValid: "Code correct. Défi terminé !",
      challengeInvalid: "Code non reconnu. Relancez le validateur local puis réessayez."
    }
  };

  function getLang(pathname) {
    var path = pathname || (root.location && root.location.pathname) || "";
    if (path.indexOf("/pt/") !== -1) return "pt";
    if (path.indexOf("/fr/") !== -1) return "fr";
    return "en";
  }

  function t(key) {
    var lang = getLang();
    return (LABELS[lang] && LABELS[lang][key]) || LABELS.en[key] || key;
  }

  function readProgress(storage) {
    var source = storage || (root && root.localStorage);
    if (!source) return {};
    try {
      return JSON.parse(source.getItem(STORAGE_KEY) || "{}");
    } catch (error) {
      return {};
    }
  }

  function setCompleted(labId, done, storage) {
    var target = storage || root.localStorage;
    var progress = readProgress(target);
    if (done) progress[labId] = new Date().toISOString();
    else delete progress[labId];
    target.setItem(STORAGE_KEY, JSON.stringify(progress));
  }

  function timeBucket(minutes) {
    if (minutes <= 30) return "short";
    if (minutes <= 60) return "medium";
    return "long";
  }

  function includesValue(values, expected) {
    if (!expected) return true;
    return (values || []).map(String).indexOf(expected) !== -1;
  }

  function filterLabs(labs, filters) {
    var f = filters || {};
    var query = (f.query || "").trim().toLowerCase();
    return labs.filter(function (lab) {
      var haystack = [lab.id, lab.title, lab.summary, lab.journey]
        .concat(lab.tags || [], lab.roles || [], lab.technologies || [])
        .join(" ").toLowerCase();
      return lab.status !== "retired" &&
        (!f.journey || lab.journey === f.journey) &&
        (!f.level || lab.level === f.level) &&
        (!f.cost || lab.cost === f.cost) &&
        (!f.simulation || String(Boolean(lab.simulation)) === f.simulation) &&
        (!f.role || includesValue(lab.roles, f.role)) &&
        (!f.time || timeBucket(lab.time_min) === f.time) &&
        (!f.technology || includesValue(lab.technologies, f.technology)) &&
        (!f.language || lab.language === f.language) &&
        (!query || haystack.indexOf(query) !== -1);
    });
  }

  function sortLabs(labs, mode) {
    var result = labs.slice();
    var level = { L50: 50, L100: 100, L200: 200, L300: 300, L400: 400 };
    result.sort(function (a, b) {
      if (mode === "number-desc") return Number(b.id) - Number(a.id);
      if (mode === "title") return a.title.localeCompare(b.title);
      if (mode === "time") return a.time_min - b.time_min || Number(a.id) - Number(b.id);
      if (mode === "level") return level[a.level] - level[b.level] || Number(a.id) - Number(b.id);
      return Number(a.id) - Number(b.id);
    });
    return result;
  }

  function scoreAnswer(question, selectedIndex) {
    return Number(selectedIndex) === Number(question.correct);
  }

  function escapeHtml(value) {
    return String(value || "").replace(/[&<>"']/g, function (char) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char];
    });
  }

  function unique(labs, field) {
    var values = [];
    labs.forEach(function (lab) {
      var current = Array.isArray(lab[field]) ? lab[field] : [lab[field]];
      current.filter(Boolean).forEach(function (value) {
        if (values.indexOf(value) === -1) values.push(value);
      });
    });
    return values.sort();
  }

  function optionMarkup(values, label) {
    return '<option value="">' + escapeHtml(label) + "</option>" +
      values.map(function (value) {
        return '<option value="' + escapeHtml(value) + '">' + escapeHtml(value) + "</option>";
      }).join("");
  }

  function costLabel(cost) {
    return {
      free: "FREE", "free-gh": "FREE · GH",
      "free-conditional": "FREE · CONDITIONS", paid: "PAID"
    }[cost] || cost;
  }

  function labCard(lab, progress) {
    var complete = Boolean(progress["lab-" + lab.id]);
    return '<article class="catalog-card' + (complete ? " is-complete" : "") + '">' +
      '<div class="catalog-card__meta"><span class="level-badge level-' +
      escapeHtml(lab.level.replace("L", "")) + '">' + escapeHtml(lab.level) + "</span>" +
      '<span class="cost-pill cost-' + escapeHtml(lab.cost) + '">' + escapeHtml(costLabel(lab.cost)) + "</span>" +
      (lab.simulation ? '<span class="simulation-pill">' + escapeHtml(t("simulated")) + "</span>" : "") +
      "</div><h2><a href=\"" + escapeHtml(lab.url) + "\">" + escapeHtml(lab.title) + "</a></h2>" +
      '<p class="catalog-card__summary">' + escapeHtml(lab.summary) + "</p>" +
      '<div class="catalog-card__footer"><span>~' + Number(lab.time_min) + " min</span>" +
      "<span>" + escapeHtml(lab.journey) + "</span>" +
      (complete ? '<span aria-label="' + escapeHtml(t("completed")) + '">✓ ' + escapeHtml(t("completed")) + "</span>" : "") +
      "</div></article>";
  }

  function fetchCatalog() {
    var catalog = document.querySelector("[data-lab-catalog]");
    var home = document.querySelector("[data-home-catalog]");
    if (!catalog && !home) return Promise.resolve([]);
    var url = catalog ? catalog.dataset.source : home.dataset.source;
    return fetch(url).then(function (response) {
      if (!response.ok) throw new Error("Catalog request failed: " + response.status);
      return response.json();
    });
  }

  function buildCatalog(labs) {
    var host = document.querySelector("[data-lab-catalog]");
    if (!host) return;
    var lang = getLang();
    var controls = document.createElement("form");
    controls.className = "catalog-controls";
    controls.setAttribute("role", "search");
    controls.innerHTML =
      '<label class="catalog-search"><span>' + t("search") + '</span><input name="query" type="search" autocomplete="off"></label>' +
      '<label><span>' + t("journey") + '</span><select name="journey">' + optionMarkup(unique(labs, "journey"), t("all")) + "</select></label>" +
      '<label><span>' + t("level") + '</span><select name="level">' + optionMarkup(unique(labs, "level"), t("all")) + "</select></label>" +
      '<label><span>' + t("cost") + '</span><select name="cost">' + optionMarkup(unique(labs, "cost"), t("all")) + "</select></label>" +
      '<label><span>' + t("simulation") + '</span><select name="simulation"><option value="">' + t("all") + '</option><option value="true">' + t("simulated") + "</option></select></label>" +
      '<label><span>' + t("role") + '</span><select name="role">' + optionMarkup(unique(labs, "roles"), t("all")) + "</select></label>" +
      '<label><span>' + t("time") + '</span><select name="time"><option value="">' + t("all") + '</option><option value="short">≤ 30 min</option><option value="medium">31–60 min</option><option value="long">&gt; 60 min</option></select></label>' +
      '<label><span>' + t("technology") + '</span><select name="technology">' + optionMarkup(unique(labs, "technologies"), t("all")) + "</select></label>" +
      '<label><span>' + t("language") + '</span><select name="language">' + optionMarkup(unique(labs, "language"), t("all")) + "</select></label>" +
      '<label><span>' + t("sort") + '</span><select name="sort"><option value="number"># ↑</option><option value="number-desc"># ↓</option><option value="title">A–Z</option><option value="time">' + t("time") + '</option><option value="level">' + t("level") + "</option></select></label>" +
      '<button type="reset" class="catalog-reset">' + t("reset") + "</button>";
    var status = document.createElement("p");
    status.className = "catalog-status";
    status.setAttribute("role", "status");
    status.setAttribute("aria-live", "polite");
    var grid = document.createElement("div");
    grid.className = "catalog-grid";
    host.replaceChildren(controls, status, grid);

    function render() {
      var data = new FormData(controls);
      var filters = {};
      data.forEach(function (value, key) { filters[key] = value; });
      var visible = sortLabs(filterLabs(labs, filters), filters.sort);
      status.textContent = visible.length + " " + t("results");
      grid.innerHTML = visible.length
        ? visible.map(function (lab) { return labCard(lab, readProgress()); }).join("")
        : '<p class="catalog-empty">' + t("noResults") + "</p>";
    }
    controls.addEventListener("input", render);
    controls.addEventListener("reset", function () { root.setTimeout(render, 0); });
    render();
  }

  function buildHomeWidgets(labs) {
    var host = document.querySelector("[data-home-catalog]");
    if (!host) return;
    var progress = readProgress();
    var completed = Object.keys(progress).sort(function (a, b) {
      return String(progress[b]).localeCompare(String(progress[a]));
    });
    var section = document.createElement("section");
    section.className = "continue-widget";
    section.innerHTML = "<h2>" + t("continueTitle") + "</h2>";
    if (!completed.length) {
      section.innerHTML += "<p>" + t("continueEmpty") + "</p>";
    } else {
      var latest = completed[0].replace("lab-", "");
      var index = labs.findIndex(function (lab) { return lab.id === latest; });
      var next = labs.slice(index + 1).find(function (lab) { return lab.status === "active"; });
      var current = labs[index];
      section.innerHTML += '<div class="continue-widget__cards">' +
        (current ? labCard(current, progress) : "") +
        (next ? labCard(next, progress) : "") + "</div>";
    }
    host.replaceChildren(section);
  }

  function addCompletionCheckbox() {
    var match = root.location && root.location.pathname.match(/\/labs\/lab-(\d+)/);
    if (!match) return;
    var labId = "lab-" + match[1];
    var h1 = document.querySelector("article h1");
    if (!h1) return;
    var wrapper = document.createElement("div");
    var checked = Boolean(readProgress()[labId]);
    wrapper.className = "lab-completion";
    wrapper.innerHTML = '<label class="completion-toggle"><input type="checkbox" ' +
      (checked ? "checked" : "") + '><span>' + (checked ? t("completed") : t("markComplete")) +
      '</span></label><span class="completion-note">' + t("progressSaved") + "</span>";
    h1.after(wrapper);
    wrapper.querySelector("input").addEventListener("change", function () {
      setCompleted(labId, this.checked);
      wrapper.querySelector(".completion-toggle span").textContent =
        this.checked ? t("completed") : t("markComplete");
    });
  }

  function addChallengeValidators() {
    document.querySelectorAll(".challenge-validator").forEach(function (wrapper) {
      var input = wrapper.querySelector("input");
      var button = wrapper.querySelector("button");
      var result = wrapper.querySelector(".challenge-validator-result");
      var expected = (wrapper.dataset.answer || "").trim().toUpperCase();
      if (!input || !button || !result || !expected) return;
      button.addEventListener("click", function () {
        var ok = input.value.trim().toUpperCase() === expected;
        result.textContent = ok ? t("challengeValid") : t("challengeInvalid");
        result.className = "challenge-validator-result " + (ok ? "success" : "error");
      });
    });
  }

  function addPhase3Tabs() {
    document.querySelectorAll("[data-phase3-tabs]").forEach(function (wrapper) {
      var tabs = Array.from(wrapper.querySelectorAll("[data-phase3-tab]"));
      var panels = Array.from(wrapper.querySelectorAll("[data-phase3-panel]"));
      if (tabs.length !== 2 || panels.length !== 2) return;

      function select(name, focus) {
        tabs.forEach(function (tab) {
          var active = tab.dataset.phase3Tab === name;
          tab.setAttribute("aria-selected", String(active));
          tab.tabIndex = active ? 0 : -1;
          if (active && focus) tab.focus();
        });
        panels.forEach(function (panel) {
          panel.hidden = panel.dataset.phase3Panel !== name;
        });
      }

      tabs.forEach(function (tab, index) {
        tab.addEventListener("click", function () {
          select(tab.dataset.phase3Tab, false);
        });
        tab.addEventListener("keydown", function (event) {
          if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
          event.preventDefault();
          var offset = event.key === "ArrowRight" ? 1 : -1;
          var next = tabs[(index + offset + tabs.length) % tabs.length];
          select(next.dataset.phase3Tab, true);
        });
      });
      select(tabs.find(function (tab) {
        return tab.getAttribute("aria-selected") === "true";
      }).dataset.phase3Tab, false);
    });
  }

  function addTokenPlaygrounds() {
    document.querySelectorAll("[data-token-playground]").forEach(function (widget) {
      var text = widget.querySelector("textarea");
      var context = widget.querySelector("[data-context-size]");
      var temperature = widget.querySelector("[data-temperature]");
      var topK = widget.querySelector("[data-top-k]");
      var topP = widget.querySelector("[data-top-p]");
      var output = widget.querySelector("[data-token-output]");
      var meter = widget.querySelector("[data-token-meter]");
      var sampling = widget.querySelector("[data-sampling-output]");
      if (!text || !context || !temperature || !topK || !topP || !output || !meter || !sampling) return;

      function render() {
        var chars = text.value.length;
        var words = text.value.trim() ? text.value.trim().split(/\s+/).length : 0;
        var tokens = Math.max(0, Math.round(chars / 4 + words * 0.15));
        var windowSize = Number(context.value);
        var percent = Math.min(100, Math.round(tokens / windowSize * 100));
        var temp = Number(temperature.value);
        output.textContent = "≈ " + tokens + " " + t("tokens") + " · " + percent + "% context · " +
          Math.max(0, windowSize - tokens) + " " + t("remaining");
        meter.style.width = percent + "%";
        sampling.textContent = "temperature " + temp.toFixed(1) + " · top-k " + topK.value +
          " · top-p " + Number(topP.value).toFixed(2) + " → " +
          (temp <= 0.3 ? t("deterministic") : temp >= 1.2 ? t("diverse") : t("balanced"));
      }

      widget.addEventListener("input", render);
      render();
    });
  }

  function addGh300Quiz() {
    var host = document.querySelector("[data-gh300-quiz]");
    if (!host) return;
    fetch(host.dataset.source).then(function (response) {
      if (!response.ok) throw new Error("Question bank request failed: " + response.status);
      return response.json();
    }).then(function (questions) {
      var index = 0;
      var score = 0;
      function render() {
        var question = questions[index];
        host.innerHTML = '<section class="gh300-quiz-card"><p><strong>' + t("question") +
          " " + (index + 1) + "/" + questions.length + '</strong></p><h3>' +
          escapeHtml(question.prompt) + '</h3><form><fieldset><legend class="sr-only">' +
          escapeHtml(question.prompt) + "</legend>" +
          question.options.map(function (option, optionIndex) {
            return '<label><input type="radio" name="answer" value="' + optionIndex +
              '"> <span>' + escapeHtml(option) + "</span></label>";
          }).join("") + '</fieldset><button type="submit" class="hub-button hub-button--primary">' +
          t("submit") + '</button></form><p class="gh300-feedback" aria-live="polite"></p>' +
          '<p class="gh300-score">' + t("score") + ": " + score + "/" + index + "</p></section>";
        var form = host.querySelector("form");
        form.addEventListener("submit", function (event) {
          event.preventDefault();
          var selected = form.querySelector('input[name="answer"]:checked');
          if (!selected) return;
          var correct = scoreAnswer(question, selected.value);
          if (correct) score += 1;
          var feedback = host.querySelector(".gh300-feedback");
          feedback.textContent = (correct ? t("correct") : t("incorrect")) + ": " + question.explanation;
          form.querySelectorAll("input, button").forEach(function (control) { control.disabled = true; });
          var next = document.createElement("button");
          next.type = "button";
          next.className = "hub-button";
          next.textContent = index + 1 === questions.length ? t("score") : t("next");
          next.addEventListener("click", function () {
            index += 1;
            if (index < questions.length) render();
            else {
              localStorage.setItem("ai-hub-gh300-score", JSON.stringify({ score: score, total: questions.length }));
              host.innerHTML = '<div class="gh300-final"><h3>' + t("score") + ": " +
                score + "/" + questions.length + "</h3></div>";
            }
          });
          feedback.after(next);
        });
      }
      render();
    }).catch(function (error) {
      host.textContent = error.message;
    });
  }

  function init() {
    document.querySelectorAll(".lab-completion").forEach(function (node) { node.remove(); });
    addCompletionCheckbox();
    addChallengeValidators();
    addPhase3Tabs();
    addTokenPlaygrounds();
    addGh300Quiz();
    fetchCatalog().then(function (labs) {
      buildCatalog(labs);
      buildHomeWidgets(labs);
    }).catch(function (error) {
      var status = document.querySelector("[data-catalog-error]");
      if (status) status.textContent = error.message;
    });
  }

  if (root.document) {
    if (typeof root.document$ !== "undefined") root.document$.subscribe(init);
    else root.document.addEventListener("DOMContentLoaded", init);
  }

  return {
    filterLabs: filterLabs,
    sortLabs: sortLabs,
    readProgress: readProgress,
    timeBucket: timeBucket,
    scoreAnswer: scoreAnswer
  };
});
