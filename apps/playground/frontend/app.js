/* First-party static UI: no CDN dependencies, persistent token storage, or arbitrary script execution. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const state = { token: "", catalog: null, config: null };
  const titles = { overview: "Overview", patterns: "Pattern library", playground: "Playground", compare: "Compare" };
  const format = (value) => value == null ? "N/A" : String(value);
  const tidy = (id) => id.replaceAll("_", " ").replace(/\b\w/g, (s) => s.toUpperCase());

  function element(tag, className, content) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined) node.textContent = content;
    return node;
  }
  function clear(node) { node.replaceChildren(); }
  function showToast(message) {
    const toast = $("toast"); toast.textContent = message; toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 4200);
  }
  async function call(path, options = {}) {
    const headers = { "Content-Type": "application/json" };
    if (state.token) headers.Authorization = `Bearer ${state.token}`;
    const response = await fetch(path, { ...options, headers: { ...headers, ...(options.headers || {}) } });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = typeof body.detail === "object" ? (body.detail.message || JSON.stringify(body.detail)) : body.detail;
      if (response.status === 401 && !$("auth-dialog").open) $("auth-dialog").showModal();
      throw new Error(message || `Request failed (${response.status})`);
    }
    return body;
  }
  function go(section) {
    document.querySelectorAll(".view").forEach((el) => el.classList.toggle("active", el.id === section));
    document.querySelectorAll(".nav-item").forEach((el) => el.classList.toggle("active", el.dataset.section === section));
    $("breadcrumb").textContent = titles[section] || section;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  document.querySelectorAll("[data-section]").forEach((el) => el.addEventListener("click", () => go(el.dataset.section)));
  document.querySelectorAll("[data-go]").forEach((el) => el.addEventListener("click", () => go(el.dataset.go)));
  $("auth-button").addEventListener("click", () => $("auth-dialog").showModal());
  $("save-token").addEventListener("click", () => { state.token = $("auth-input").value; $("auth-input").value = ""; void initialize(); });

  function renderPatterns() {
    const filter = $("pattern-filter").value;
    const query = $("pattern-search").value.toLowerCase();
    const grid = $("pattern-grid"); clear(grid);
    (state.catalog?.patterns || []).filter((p) => (!filter || filter === p.category) &&
      `${p.name} ${p.category} ${p.id}`.toLowerCase().includes(query)).forEach((p) => {
      const card = element("article", "pattern-card");
      card.append(element("div", "card-id", p.category.replaceAll("_", " ")));
      card.append(element("h3", "", p.name));
      const bottom = element("div", "card-bottom");
      bottom.append(element("span", "chip", p.offline ? "OFFLINE READY" : "OPTIONAL LIVE"));
      if (p.playground_example) {
        const button = element("button", "text-link", "Explore ↗");
        button.addEventListener("click", () => { $("example-select").value = p.playground_example; updateExample(); go("playground"); });
        bottom.append(button);
      }
      card.append(bottom); grid.append(card);
    });
    if (!grid.children.length) grid.append(element("div", "empty-card", "No matching patterns"));
  }
  $("pattern-filter").addEventListener("change", renderPatterns);
  $("pattern-search").addEventListener("input", renderPatterns);

  function updateExample() {
    const spec = state.catalog?.examples.find((e) => e.id === $("example-select").value);
    if (!spec) return;
    $("example-input-label").textContent = spec.parameter_name.toUpperCase();
    $("example-input").value = spec.default;
    $("example-input").placeholder = spec.placeholder;
    $("example-description").textContent = spec.summary;
    $("char-count").textContent = spec.default.length;
    $("live-toggle").checked = false;
    $("live-toggle").disabled = !state.config?.live_enabled || !spec.live_supported;
  }
  $("example-select").addEventListener("change", updateExample);
  $("example-input").addEventListener("input", () => { $("char-count").textContent = $("example-input").value.length; });
  $("compare-select").addEventListener("change", () => {
    const current = state.catalog?.comparisons.find((item) => item.id === $("compare-select").value);
    $("compare-description").textContent = current?.description || "";
  });

  function renderResult(result) {
    $("output-empty").hidden = true; $("output-content").hidden = false;
    $("result-provider").textContent = `${result.provider} / ${result.model}`;
    $("result-attempts").textContent = format(result.attempts);
    $("result-latency").textContent = `${result.latency_ms} ms`;
    $("result-cost").textContent = result.cost_usd == null ? "N/A" : `$${result.cost_usd}`;
    const responseText = $("result-text");
    const responseToggle = $("response-toggle");
    responseText.classList.remove("expanded");
    responseText.textContent = result.output;
    responseToggle.hidden = false;
    requestAnimationFrame(() => {
      const overflowing = responseText.scrollHeight > responseText.clientHeight + 1;
      responseToggle.hidden = !overflowing;
      responseToggle.textContent = "Expand response";
      responseToggle.setAttribute("aria-expanded", "false");
    });
    $("result-validation").textContent = JSON.stringify(result.validation, null, 2);
    $("result-usage").textContent = result.usage == null ? "Provider usage unavailable" : JSON.stringify(result.usage, null, 2);
    $("result-notes").textContent = `${result.notes} · ${result.cost_note}`;
    clear($("result-trace"));
    result.trace.forEach((step, idx) => $("result-trace").append(element("div", "trace-item", `${idx + 1}. ${step.step} — ${step.status}${step.attempt ? ` (attempt ${step.attempt})` : ""}`)));
    $("run-state").textContent = "COMPLETED";
  }
  $("response-toggle").addEventListener("click", () => {
    const responseText = $("result-text");
    const expanded = responseText.classList.toggle("expanded");
    const toggle = $("response-toggle");
    toggle.textContent = expanded ? "Collapse response" : "Expand response";
    toggle.setAttribute("aria-expanded", String(expanded));
  });
  $("run-button").addEventListener("click", async () => {
    const btn = $("run-button"); btn.disabled = true; btn.textContent = "Running…";
    $("run-state").textContent = "RUNNING";
    try {
      const response = await call("/api/run", { method: "POST", body: JSON.stringify({ example_id: $("example-select").value, value: $("example-input").value, live: $("live-toggle").checked }) });
      renderResult(response.result); $("quota-left").textContent = response.quota.remaining;
    } catch (err) { $("run-state").textContent = "ERROR"; showToast(err.message); }
    finally { btn.disabled = false; btn.textContent = "▶   Run example    ↗"; }
  });
  $("compare-button").addEventListener("click", async () => {
    const btn = $("compare-button"); btn.disabled = true;
    try {
      const response = await call("/api/compare", { method: "POST", body: JSON.stringify({ comparison_id: $("compare-select").value, value: $("compare-input").value }) });
      const grid = $("compare-results"); clear(grid);
      response.result.results.forEach((row) => {
        const card = element("article", "comparison-card");
        card.append(element("div", "tiny-label", "IMPLEMENTATION"));
        card.append(element("h3", "", tidy(row.implementation)));
        card.append(element("div", "status", row.status));
        card.append(element("pre", "", row.output));
        card.append(element("small", "", `${row.attempts} attempt(s) · ${format(row.latency_ms)} ms · cost N/A`));
        grid.append(card);
      });
      $("compare-scope").textContent = response.result.scope;
      $("quota-left").textContent = response.quota.remaining;
    } catch (err) { showToast(err.message); }
    finally { btn.disabled = false; }
  });

  function populateCatalog() {
    const catalog = state.catalog;
    $("pattern-count").textContent = String(catalog.patterns.length).padStart(2, "0");
    $("pattern-total").textContent = `${catalog.patterns.length} PATTERNS`;
    $("demo-count").textContent = String(catalog.examples.length).padStart(2, "0");
    const quick = $("quick-list"); clear(quick);
    catalog.examples.slice(0, 4).forEach((spec, index) => {
      const button = element("button", "quick-item");
      button.append(element("span", "quick-num", String(index + 1).padStart(2, "0")));
      const middle = element("div"); middle.append(element("strong", "", spec.title)); middle.append(element("small", "", spec.category));
      button.append(middle, element("span", "arrow", "→"));
      button.addEventListener("click", () => { $("example-select").value = spec.id; updateExample(); go("playground"); });
      quick.append(button);
    });
    const filter = $("pattern-filter"); clear(filter); filter.append(new Option("All categories", ""));
    [...new Set(catalog.patterns.map((p) => p.category))].sort().forEach((c) => filter.append(new Option(c.replaceAll("_", " "), c)));
    const examples = $("example-select"); clear(examples);
    catalog.examples.forEach((e) => examples.append(new Option(`${e.category} — ${e.title}`, e.id)));
    const comparisons = $("compare-select"); clear(comparisons);
    catalog.comparisons.forEach((c) => comparisons.append(new Option(c.title, c.id)));
    updateExample(); comparisons.dispatchEvent(new Event("change")); renderPatterns();
  }
  async function initialize() {
    try {
      const [config, catalog] = await Promise.all([call("/api/settings"), call("/api/catalog")]);
      state.config = config; state.catalog = catalog;
      $("mode-badge").textContent = config.live_enabled ? "LIVE ENABLED / OPT-IN" : "OFFLINE FIRST";
      $("connection").textContent = "Backend connected";
      $("quota-left").textContent = config.quotas.remaining;
      populateCatalog();
    } catch (err) { $("connection").textContent = "Connection unavailable"; showToast(err.message); }
  }
  void initialize();
})();
