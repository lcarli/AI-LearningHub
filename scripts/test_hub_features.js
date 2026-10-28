"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const hub = require("../docs/docs/en/js/hub-features.js");

const labs = [
  {
    id: "085",
    title: "Instructions",
    summary: "Repository guidance",
    journey: "copilot",
    level: "L100",
    cost: "free-gh",
    simulation: false,
    roles: ["developer"],
    time_min: 30,
    technologies: ["copilot"],
    language: "en",
    status: "active"
  },
  {
    id: "091",
    title: "Enterprise controls",
    summary: "Governance simulation",
    journey: "enterprise",
    level: "L300",
    cost: "paid",
    simulation: true,
    roles: ["admin"],
    time_min: 90,
    technologies: ["governance"],
    language: "en",
    status: "active"
  }
];

test("combined filters use AND semantics", () => {
  const result = hub.filterLabs(labs, {
    journey: "enterprise",
    level: "L300",
    cost: "paid",
    simulation: "true",
    role: "admin",
    time: "long",
    technology: "governance",
    language: "en",
    query: "controls"
  });
  assert.deepEqual(result.map((lab) => lab.id), ["091"]);
});

test("free and simulated filters remain independent", () => {
  assert.equal(hub.filterLabs(labs, { cost: "free-gh" }).length, 1);
  assert.equal(hub.filterLabs(labs, { simulation: "true" }).length, 1);
});

test("sorting supports number, title, time, and level", () => {
  assert.deepEqual(hub.sortLabs(labs, "number-desc").map((lab) => lab.id), ["091", "085"]);
  assert.deepEqual(hub.sortLabs(labs, "title").map((lab) => lab.id), ["091", "085"]);
  assert.deepEqual(hub.sortLabs(labs, "time").map((lab) => lab.id), ["085", "091"]);
  assert.deepEqual(hub.sortLabs(labs, "level").map((lab) => lab.id), ["085", "091"]);
});

test("progress storage survives invalid JSON", () => {
  const invalid = { getItem: () => "{bad json" };
  const valid = { getItem: () => '{"lab-085":"2026-10-27T00:00:00Z"}' };
  assert.deepEqual(hub.readProgress(invalid), {});
  assert.equal(hub.readProgress(valid)["lab-085"], "2026-10-27T00:00:00Z");
});

test("GH-300 answers are scored by the declared correct index", () => {
  const question = { correct: 2 };
  assert.equal(hub.scoreAnswer(question, "2"), true);
  assert.equal(hub.scoreAnswer(question, 1), false);
});

test("each language ships a 50-question GH-300 bank", () => {
  ["en", "pt", "fr"].forEach((lang) => {
    const bank = JSON.parse(fs.readFileSync(
      path.join(__dirname, `../docs/docs/${lang}/paths/gh-300/questions.json`),
      "utf8"
    ));
    assert.equal(bank.length, 50);
    assert.equal(new Set(bank.map((question) => question.id)).size, 50);
    assert.ok(bank.every((question) => question.options.length === 4));
  });
});

test("catalog CSS includes accessible focus, responsive, and reduced-motion states", () => {
  const css = fs.readFileSync(
    path.join(__dirname, "../docs/docs/en/css/custom.css"),
    "utf8"
  );
  assert.match(css, /\.catalog-controls/);
  assert.match(css, /:focus-visible/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /\.token-playground/);
  assert.match(css, /\.phase3-path-tabs/);
});

test("Phase 3 local and real tabs are initialized", () => {
  const source = fs.readFileSync(
    path.join(__dirname, "../docs/docs/en/js/hub-features.js"),
    "utf8"
  );
  assert.match(source, /function addPhase3Tabs/);
  assert.match(source, /data-phase3-panel/);
});
