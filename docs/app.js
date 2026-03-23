const dashboardData = window.BENCHMARK_DASHBOARD_DATA || { rows: [], summary: {}, cases: [] };

const state = {
  kind: "sorting",
  datasetType: "",
  size: "",
  scenario: "",
};

const algorithmLabels = {
  bubble: "Bubble Sort",
  insertion: "Insertion Sort",
  merge: "Merge Sort",
  quick: "Quick Sort",
  heap: "Heap Sort",
  linear: "Linear Search",
  binary: "Binary Search",
  jump: "Jump Search",
  exponential: "Exponential Search",
};

const algorithmColors = {
  bubble: "var(--bubble)",
  insertion: "var(--insertion)",
  merge: "var(--merge)",
  quick: "var(--quick)",
  heap: "var(--heap)",
  linear: "var(--linear)",
  binary: "var(--binary)",
  jump: "var(--jump)",
  exponential: "var(--exponential)",
};

const kindColors = {
  sorting: ["#da6a34", "#9b3d1c"],
  searching: ["#1a8b80", "#115e56"],
};

const kindToggle = document.querySelector("#kindToggle");
const datasetSelect = document.querySelector("#datasetSelect");
const sizeSelect = document.querySelector("#sizeSelect");
const scenarioSelect = document.querySelector("#scenarioSelect");

function init() {
  renderKindToggle();
  hydrateStateDefaults();
  bindControls();
  render();
}

function renderKindToggle() {
  ["sorting", "searching"].forEach((kind) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "segment-button";
    button.textContent = kind[0].toUpperCase() + kind.slice(1);
    button.dataset.kind = kind;
    kindToggle.appendChild(button);
  });
}

function hydrateStateDefaults() {
  const rows = dashboardData.rows;
  state.kind = rows.some((row) => row.kind === "sorting") ? "sorting" : rows[0]?.kind || "sorting";
  syncControlOptions();
}

function bindControls() {
  kindToggle.addEventListener("click", (event) => {
    const button = event.target.closest(".segment-button");
    if (!button) {
      return;
    }

    state.kind = button.dataset.kind;
    syncControlOptions();
    render();
  });

  datasetSelect.addEventListener("change", () => {
    state.datasetType = datasetSelect.value;
    syncSizeOptions();
    syncScenarioOptions();
    render();
  });

  sizeSelect.addEventListener("change", () => {
    state.size = Number(sizeSelect.value);
    syncScenarioOptions();
    render();
  });

  scenarioSelect.addEventListener("change", () => {
    state.scenario = scenarioSelect.value;
    render();
  });
}

function syncControlOptions() {
  paintKindToggle();
  fillSelect(datasetSelect, getDatasetTypes(state.kind));
  state.datasetType = datasetSelect.value;
  syncSizeOptions();
  syncScenarioOptions();
}

function syncSizeOptions() {
  fillSelect(sizeSelect, getSizes(state.kind, state.datasetType).map(String));
  state.size = Number(sizeSelect.value);
}

function syncScenarioOptions() {
  fillSelect(scenarioSelect, getScenarios(state.kind, state.datasetType, state.size));
  state.scenario = scenarioSelect.value;
}

function fillSelect(select, options) {
  const previous = select.value;
  select.innerHTML = "";

  options.forEach((optionValue) => {
    const option = document.createElement("option");
    option.value = optionValue;
    option.textContent = optionValue === "-" ? "Standard run" : startCase(optionValue);
    select.appendChild(option);
  });

  if (options.includes(previous)) {
    select.value = previous;
  }
}

function paintKindToggle() {
  const [startColor, endColor] = kindColors[state.kind];
  kindToggle.style.setProperty("--segment-start", startColor);
  kindToggle.style.setProperty("--segment-end", endColor);
  [...kindToggle.querySelectorAll(".segment-button")].forEach((button) => {
    button.classList.toggle("is-active", button.dataset.kind === state.kind);
  });
}

function getDatasetTypes(kind) {
  return [...new Set(dashboardData.rows.filter((row) => row.kind === kind).map((row) => row.dataset_type))];
}

function getSizes(kind, datasetType) {
  return [...new Set(
    dashboardData.rows
      .filter((row) => row.kind === kind && row.dataset_type === datasetType)
      .map((row) => row.size),
  )].sort((left, right) => left - right);
}

function getScenarios(kind, datasetType, size) {
  return [...new Set(
    dashboardData.rows
      .filter((row) => row.kind === kind && row.dataset_type === datasetType && row.size === size)
      .map((row) => row.scenario),
  )];
}

function render() {
  renderTopStats();
  renderMetrics();
  renderLegend();
  renderBars();
  renderAtlas();
  renderTable();
}

function renderTopStats() {
  document.querySelector("#totalRuns").textContent = dashboardData.rows.length;
  document.querySelector("#totalCases").textContent = dashboardData.cases.length;
}

function renderMetrics() {
  const rows = getCurrentRows();
  const fastest = rows[0];
  const recommended = rows.find((row) => row.algorithm === rows[0]?.recommended_algorithm) || rows[0];
  const summary = dashboardData.summary;
  const hits = summary.recommendation_hits?.[state.kind] ?? 0;
  const totals = summary.scenario_totals?.[state.kind] ?? 0;
  const gap = recommended && fastest
    ? `${(recommended.average_time_seconds / fastest.average_time_seconds).toFixed(2)}x`
    : "-";

  document.querySelector("#fastestMetric").textContent = labelFor(fastest?.algorithm);
  document.querySelector("#fastestMeta").textContent = fastest
    ? `${formatTime(fastest.average_time_seconds)} average runtime in the selected case.`
    : "No measurements for this selection.";

  document.querySelector("#recommendedMetric").textContent = labelFor(recommended?.recommended_algorithm);
  document.querySelector("#recommendedMeta").textContent = recommended
    ? rows[0].recommended_algorithm === fastest?.algorithm
      ? "The selector matches the measured winner here."
      : "The selector chooses a different algorithm for this case."
    : "No recommendation available.";

  document.querySelector("#hitRateMetric").textContent = totals ? `${hits}/${totals}` : "-";
  document.querySelector("#hitRateMeta").textContent = totals
    ? `${Math.round((hits / totals) * 100)}% recommendation accuracy across ${startCase(state.kind)} cases.`
    : "No aggregate data available.";

  document.querySelector("#gapMetric").textContent = gap;
  document.querySelector("#gapMeta").textContent = recommended && fastest
    ? `${labelFor(recommended.recommended_algorithm)} compared with ${labelFor(fastest.algorithm)}.`
    : "No comparison available.";
}

function renderLegend() {
  const rows = getCurrentRows();
  const legend = document.querySelector("#legend");
  legend.innerHTML = "";

  rows.forEach((row) => {
    const chip = document.createElement("div");
    chip.className = "legend-chip";
    chip.innerHTML = `
      <span class="legend-swatch" style="background:${algorithmColors[row.algorithm]};"></span>
      <span class="legend-label">${labelFor(row.algorithm)}</span>
    `;
    legend.appendChild(chip);
  });
}

function renderBars() {
  const rows = getCurrentRows();
  const container = document.querySelector("#performanceBars");
  container.innerHTML = "";

  if (!rows.length) {
    container.textContent = "No benchmark rows match this filter.";
    return;
  }

  const fastest = rows[0];
  document.querySelector("#caseTitle").textContent = `${startCase(state.kind)} comparison`;
  document.querySelector("#caseSubtitle").textContent = caseDescription(rows[0]);

  rows.forEach((row) => {
    const relativeScore = Math.max(
      8,
      Math.round((fastest.average_time_seconds / row.average_time_seconds) * 100),
    );
    const bar = document.createElement("article");
    bar.className = "bar-row";
    bar.innerHTML = `
      <div class="bar-label">${labelFor(row.algorithm)}</div>
      <div class="bar-track">
        <div class="bar-fill" style="--bar-width:${relativeScore}%; --bar-color:${algorithmColors[row.algorithm]};"></div>
      </div>
      <div class="bar-meta">
        <strong>${formatTime(row.average_time_seconds)}</strong>
        <div class="bar-status">
          ${row.algorithm === fastest.algorithm ? '<span class="status-pill fastest">Fastest</span>' : ""}
          ${row.algorithm === row.recommended_algorithm ? '<span class="status-pill recommended">Recommended</span>' : ""}
        </div>
      </div>
    `;
    container.appendChild(bar);
  });
}

function renderAtlas() {
  const atlas = document.querySelector("#caseAtlas");
  atlas.innerHTML = "";

  const relevantCases = dashboardData.cases.filter((entry) => entry.kind === state.kind);
  relevantCases.forEach((entry) => {
    const card = document.createElement("article");
    card.className = `atlas-card ${entry.recommendation_hit ? "hit" : "miss"}`;
    card.innerHTML = `
      <p class="eyebrow">${entry.dataset_type}</p>
      <h3>${entry.size.toLocaleString()} ${entry.scenario === "-" ? "elements" : `| ${startCase(entry.scenario)}`}</h3>
      <p class="atlas-meta">Fastest: <strong>${labelFor(entry.fastest_algorithm)}</strong></p>
      <p class="atlas-meta">Recommended: <strong>${labelFor(entry.recommended_algorithm)}</strong></p>
      <span class="status-pill ${entry.recommendation_hit ? "fastest" : "recommended"}">
        ${entry.recommendation_hit ? "Match" : "Miss"}
      </span>
    `;
    atlas.appendChild(card);
  });
}

function renderTable() {
  const body = document.querySelector("#resultsTableBody");
  body.innerHTML = "";
  const rows = getCurrentRows();
  const fastest = rows[0];

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const relative = `${(row.average_time_seconds / fastest.average_time_seconds).toFixed(2)}x`;
    const status = [
      row.algorithm === fastest.algorithm ? "Fastest" : "",
      row.algorithm === row.recommended_algorithm ? "Recommended" : "",
    ].filter(Boolean).join(" · ") || "Measured";

    tr.innerHTML = `
      <td>${labelFor(row.algorithm)}</td>
      <td>${formatTime(row.average_time_seconds)}</td>
      <td>${relative}</td>
      <td>${status}</td>
    `;
    body.appendChild(tr);
  });
}

function getCurrentRows() {
  return dashboardData.rows
    .filter((row) =>
      row.kind === state.kind &&
      row.dataset_type === state.datasetType &&
      row.size === state.size &&
      row.scenario === state.scenario,
    )
    .slice()
    .sort((left, right) => left.average_time_seconds - right.average_time_seconds);
}

function caseDescription(row) {
  if (!row) {
    return "No case selected.";
  }

  const pieces = [
    `${row.size.toLocaleString()} elements`,
    `${startCase(row.dataset_type)} input`,
  ];

  if (row.scenario !== "-") {
    pieces.push(`${startCase(row.scenario)} target`);
  }

  return pieces.join(" · ");
}

function labelFor(algorithm) {
  return algorithmLabels[algorithm] || startCase(algorithm || "-");
}

function startCase(value) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function formatTime(seconds) {
  if (seconds < 0.001) {
    return `${(seconds * 1_000_000).toFixed(2)} µs`;
  }
  if (seconds < 1) {
    return `${(seconds * 1_000).toFixed(2)} ms`;
  }
  return `${seconds.toFixed(3)} s`;
}

init();
