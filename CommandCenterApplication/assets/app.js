const decimal = value => {
  const text = String(value);
  if (!/^-?\d+(\.\d+)?$/.test(text)) return "Unavailable";
  const [raw, fraction] = text.split(".");
  const sign = raw.startsWith("-") ? "-" : "";
  const digits = sign ? raw.slice(1) : raw;
  const grouped = digits.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return sign + grouped + (fraction ? "." + fraction : "");
};
const money = value => value === null ? "Unavailable" : decimal(value) + " KRW";
const esc = value => String(value ?? "").replace(
  /[&<>'"]/g,
  character => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"})[character],
);
const row = (label, value) => `<div class="row"><span>${esc(label)}</span><strong>${esc(value)}</strong></div>`;
const state = value => `<span class="state ${
  value === "NORMAL" || value === "FRESH" ? "normal" :
  value.includes("BLOCK") || value.includes("LIVE") ? "blocked" : "attention"
}">${esc(value)}</span>`;
const items = (values, render) => values.length
  ? values.map(render).join("")
  : '<p class="empty">No authoritative records available.</p>';

async function start() {
  try {
    const data = await fetch("/api/v1/command-center", {cache: "no-store"}).then(response => {
      if (!response.ok) throw Error("HTTP " + response.status);
      return response.json();
    });
    document.querySelector("#app").replaceChildren(
      document.querySelector("#layout").content.cloneNode(true),
    );
    const mode = document.querySelector("#modeBadge");
    mode.textContent = data.mode_label;
    mode.classList.add(data.mode === "FIXTURE" ? "fixture" : "normal");
    document.querySelector("#blocker").textContent = data.execution.blocker_detail;
    document.querySelector("#refresh").textContent =
      "Last factual refresh · " + (data.system_health.last_factual_refresh || "Unavailable");
    document.querySelector("#metrics").innerHTML = [
      ["Portfolio value", money(data.portfolio_value_krw)],
      ["Orderable cash", money(data.capital.orderable_cash_krw)],
      ["Positions", data.position_count],
      ["Attention", data.attention.filter(item => item.state === "UNRESOLVED").length],
      ["Execution", data.execution.state],
    ].map(item => `<div class="metric"><label>${esc(item[0])}</label><strong>${esc(item[1])}</strong></div>`).join("");
    document.querySelector("#positions").innerHTML = items(data.positions, position =>
      `<tr><td>${esc(position.security)}</td><td>${esc(position.quantity)}</td><td>${esc(money(position.market_value_krw))}</td><td>${esc(position.weight_percent === null ? "Unavailable" : position.weight_percent + "%")}</td><td>${esc(position.cap_status)}</td></tr>`,
    );
    document.querySelector("#attention").innerHTML = items(data.attention, item =>
      `<article class="item"><div class="item-head"><strong>${esc(item.category)}</strong>${state(item.state)}</div><p>${esc(item.what_happened)}</p><p><b>Why:</b> ${esc(item.why_it_matters)}</p><p><b>Action:</b> ${esc(item.required_action)}</p><p class="evidence-id">${esc(item.evidence_ids.join(" · "))}</p></article>`,
    );
    document.querySelector("#cio").innerHTML =
      row("Research", data.ai_pipeline.research_state) +
      row("Committee", data.ai_pipeline.committee_state) +
      row("Contradiction", data.ai_pipeline.contradiction_state) +
      row("State", data.cio.state) +
      row("Posture", data.cio.posture || "Unavailable") +
      row("What changed", data.cio.what_changed || "Unavailable") +
      row("Why it matters", data.cio.why_it_matters || "Unavailable") +
      row("Decision ID", data.cio.decision_id || "Unavailable") +
      row("Evidence", data.cio.evidence_ids.join(" · ") || "Unavailable") +
      row("Unresolved / contradictions", data.cio.unresolved_reasons.join(" · ") || "None recorded");
    document.querySelector("#change").innerHTML =
      row("Classification", data.change.classification) +
      items(data.change.statements, value => `<article class="item"><p>${esc(value)}</p></article>`);
    document.querySelector("#capital").innerHTML =
      row("Deployed capital", money(data.capital.deployed_capital_krw)) +
      row("Available capacity", money(data.capital.available_allocation_capacity_krw)) +
      row("Deployable policy", data.capital.deployable_policy) +
      row("Reserve", money(data.capital.explicit_reserve_krw)) +
      row("Position hard cap", money(data.capital.max_position_krw)) +
      row("Broker account valuation", money(data.capital.broker_account_valuation_krw) + " · " + data.capital.broker_account_valuation_authority);
    document.querySelector("#execution").innerHTML =
      row("Mutation mode", data.execution.mutation_mode) +
      row("Investment approval", data.investment_approval.state) +
      row("TEA", data.execution.tea_state) +
      row("Order kind", data.execution.order_kind) +
      row("UNKNOWN recovery", data.execution.unknown_recovery) +
      row("Open LIMIT attention", data.execution.open_limit_attention ? "REQUIRED" : "NONE");
    document.querySelector("#ev").innerHTML = items(data.expected_values, evaluation =>
      `<article class="item"><div class="item-head"><strong>${esc(evaluation.opportunity_id)}</strong>${state(evaluation.status)}</div><p>${esc(evaluation.portfolio_subject_id)} · ${esc(evaluation.value === null ? "Unavailable" : evaluation.value + " " + evaluation.unit_id)}</p><p class="evidence-id">${esc(evaluation.evidence_record_id || "No EV record")}</p></article>`,
    );
    document.querySelector("#allocation").innerHTML =
      row("Proposal state", data.allocation.state) +
      row("Proposal ID", data.allocation.proposal_id || "Unavailable") +
      row("Executable", data.allocation.executable ? "YES" : "NO") +
      row("Blocked reasons", data.allocation.blocked_reasons.join(" · ") || "None recorded") +
      row("IHA state", data.investment_approval.state) +
      row("IHA principal", data.investment_approval.principal || "Unavailable") +
      items(data.allocation.legs, leg => `<article class="item"><p><b>${esc(leg.portfolio_subject_id)}</b> · ${esc(leg.action)}</p><p>${esc(money(leg.current_market_value_krw))} → ${esc(money(leg.proposed_market_value_krw))} · Δ ${esc(money(leg.delta_market_value_krw))}</p></article>`);
    document.querySelector("#evidence").innerHTML = items(data.evidence.slice(0, 10), evidence =>
      `<article class="item"><div class="item-head"><span class="evidence-id">${esc(evidence.fact_id)}</span><strong>${esc(evidence.truth_class)}</strong></div><p>${esc(evidence.provider)} · ${esc(evidence.authority)} · ${esc(evidence.collected_at)}</p><p class="evidence-id">raw ${esc(evidence.raw_fact_id || "Unavailable")}</p></article>`,
    );
    document.querySelector("#health").innerHTML =
      row("Overall", data.system_health.state) +
      row("Factual freshness", data.system_health.factual_freshness) +
      row("FactStore", data.system_health.fact_store_state) +
      row("DecisionJournal", data.system_health.decision_journal_state) +
      row("Command Center", data.system_health.command_center_state) +
      row("Attention", data.system_health.attention_state) +
      row("Mutation", data.system_health.broker_mutation_mode) +
      row("Ownership boundary", data.system_health.durable_ownership);
    document.querySelector("#exclusions").innerHTML = items(data.foreign_exclusions, exclusion =>
      `<article class="item"><div class="item-head"><strong>${esc(exclusion.provider_symbol)}</strong><span>${esc(exclusion.raw_currency_code)}</span></div><p>${esc(exclusion.position_class)} · ${esc(exclusion.reason)} · <span class="evidence-id">${esc(exclusion.evidence_fact_id)}</span></p></article>`,
    );
  } catch (error) {
    document.querySelector("#app").innerHTML =
      `<section class="error">Command Center failed closed: ${esc(error.message)}</section>`;
  }
}

start();
