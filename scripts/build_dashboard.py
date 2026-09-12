import json

with open("/home/claude/project/data/dashboard_data.json") as f:
    data = json.load(f)

data_json = json.dumps(data)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Customer Analytics Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1"></script>
<style>
  :root {
    --bg-page: #f4f6f9;
    --bg-card: #ffffff;
    --bg-header: #1f2a44;
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --text-on-dark: #f9fafb;
    --accent: #4C72B0;
    --positive: #2f9e44;
    --negative: #e03131;
    --warning: #f08c00;
    --radius: 10px;
    --gap: 16px;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg-page); color: var(--text-primary);
  }
  .dashboard-container { max-width: 1400px; margin: 0 auto; padding: 20px; }
  .dashboard-header {
    background: var(--bg-header); color: var(--text-on-dark);
    padding: 20px 24px; border-radius: var(--radius); margin-bottom: var(--gap);
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  }
  .dashboard-header h1 { font-size: 20px; font-weight: 600; margin: 0 0 4px 0; }
  .dashboard-header p { margin: 0; font-size: 12px; color: rgba(255,255,255,0.7); }
  .filters { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  .filter-group { display: flex; flex-direction: column; gap: 4px; }
  .filter-group label { font-size: 11px; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 0.5px; }
  .filter-group select {
    padding: 6px 10px; border: 1px solid rgba(255,255,255,0.25); border-radius: 6px;
    background: rgba(255,255,255,0.1); color: var(--text-on-dark); font-size: 13px; min-width: 140px;
  }
  .filter-group select option { background: var(--bg-header); color: var(--text-on-dark); }
  .reset-btn {
    padding: 7px 14px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.3);
    background: transparent; color: var(--text-on-dark); font-size: 12px; cursor: pointer; align-self: flex-end;
  }
  .reset-btn:hover { background: rgba(255,255,255,0.12); }
  .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: var(--gap); margin-bottom: var(--gap); }
  .kpi-card { background: var(--bg-card); border-radius: var(--radius); padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-left: 4px solid var(--accent); }
  .kpi-card.risk { border-left-color: var(--negative); }
  .kpi-card.warn { border-left-color: var(--warning); }
  .kpi-card.good { border-left-color: var(--positive); }
  .kpi-label { font-size: 12px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
  .kpi-value { font-size: 24px; font-weight: 700; }
  .kpi-sub { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
  .chart-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: var(--gap); margin-bottom: var(--gap); }
  .chart-container { background: var(--bg-card); border-radius: var(--radius); padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .chart-container h3 { font-size: 14px; font-weight: 600; margin: 0 0 12px 0; color: var(--text-primary); }
  .chart-container canvas { max-height: 280px; }
  .table-section { background: var(--bg-card); border-radius: var(--radius); padding: 18px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); overflow-x: auto; margin-bottom: var(--gap); }
  .table-section h3 { font-size: 14px; font-weight: 600; margin: 0 0 4px 0; }
  .table-section .table-note { font-size: 12px; color: var(--text-secondary); margin-bottom: 12px; }
  .data-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
  .data-table thead th { text-align: left; padding: 8px 10px; border-bottom: 2px solid #e5e7eb; color: var(--text-secondary); font-weight: 600; font-size: 11px; text-transform: uppercase; cursor: pointer; white-space: nowrap; }
  .data-table thead th:hover { color: var(--text-primary); background: #f8f9fa; }
  .data-table tbody td { padding: 8px 10px; border-bottom: 1px solid #f0f0f0; }
  .data-table tbody tr:hover { background: #f8f9fa; }
  .badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
  .badge.Active { background: #d3f9d8; color: #2b8a3e; }
  .badge.Inactive { background: #e9ecef; color: #495057; }
  .badge.At.Risk, .badge[data-a="At Risk"] { background: #ffe3e3; color: #c92a2a; }
  .dashboard-footer { text-align: center; font-size: 12px; color: var(--text-secondary); padding: 12px; }
  @media (max-width: 768px) {
    .kpi-row { grid-template-columns: repeat(2, 1fr); }
    .chart-row { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="dashboard-container">
  <header class="dashboard-header">
    <div>
      <h1>Customer Analytics Dashboard</h1>
      <p>994 customers &middot; Segmentation, Acquisition, Activity &amp; Retention Insights</p>
    </div>
    <div class="filters">
      <div class="filter-group"><label>Segment</label><select id="f-segment"><option value="">All</option></select></div>
      <div class="filter-group"><label>Activity</label><select id="f-activity"><option value="">All</option></select></div>
      <div class="filter-group"><label>Acquisition Channel</label><select id="f-channel"><option value="">All</option></select></div>
      <div class="filter-group"><label>City</label><select id="f-city"><option value="">All</option></select></div>
      <button class="reset-btn" id="reset-filters">Reset</button>
    </div>
  </header>

  <section class="kpi-row">
    <div class="kpi-card"><div class="kpi-label">Total Customers</div><div class="kpi-value" id="kpi-customers">-</div></div>
    <div class="kpi-card good"><div class="kpi-label">Total Revenue</div><div class="kpi-value" id="kpi-revenue">-</div></div>
    <div class="kpi-card"><div class="kpi-label">Avg Order Value</div><div class="kpi-value" id="kpi-aov">-</div></div>
    <div class="kpi-card"><div class="kpi-label">Total Orders</div><div class="kpi-value" id="kpi-orders">-</div></div>
    <div class="kpi-card warn"><div class="kpi-label">At Risk Customers</div><div class="kpi-value" id="kpi-atrisk">-</div></div>
    <div class="kpi-card risk"><div class="kpi-label">Revenue at Risk</div><div class="kpi-value" id="kpi-revrisk">-</div><div class="kpi-sub" id="kpi-revrisk-pct"></div></div>
  </section>

  <section class="chart-row">
    <div class="chart-container"><h3>Revenue by Customer Segment</h3><canvas id="chart-segment"></canvas></div>
    <div class="chart-container"><h3>Customer Activity Status</h3><canvas id="chart-activity"></canvas></div>
  </section>

  <section class="chart-row">
    <div class="chart-container"><h3>Avg Spend by Acquisition Channel</h3><canvas id="chart-channel"></canvas></div>
    <div class="chart-container"><h3>Top 10 Cities by Revenue</h3><canvas id="chart-city"></canvas></div>
  </section>

  <section class="chart-row">
    <div class="chart-container"><h3>Avg Spend by Tenure Band</h3><canvas id="chart-tenure"></canvas></div>
    <div class="chart-container"><h3>Customers by Age Group</h3><canvas id="chart-age"></canvas></div>
  </section>

  <section class="table-section">
    <h3>High-Value Customers At Risk</h3>
    <div class="table-note">Top-quartile spenders whose activity status is "At Risk" — prioritize these for retention outreach.</div>
    <table class="data-table" id="risk-table">
      <thead><tr>
        <th data-key="customer_id">ID</th><th data-key="customer_name">Name</th><th data-key="city">City</th>
        <th data-key="customer_segment">Segment</th><th data-key="total_spend">Total Spend</th>
        <th data-key="total_orders">Orders</th><th data-key="days_since_last_purchase">Days Since Purchase</th>
        <th data-key="rfm_score">RFM Score</th>
      </tr></thead>
      <tbody></tbody>
    </table>
  </section>

  <footer class="dashboard-footer">Customer Analytics &amp; ETL Pipeline Project &middot; Data as of dataset extract</footer>
</div>

<script>
const RAW_DATA = __DATA_JSON__;
const COLORS = ["#4C72B0","#DD8452","#55A868","#C44E52","#8172B2","#937860","#CCB974","#64B5CD"];

function fmtCurrency(v) {
  if (Math.abs(v) >= 1e7) return "₹" + (v/1e7).toFixed(2) + "Cr";
  if (Math.abs(v) >= 1e5) return "₹" + (v/1e5).toFixed(2) + "L";
  if (Math.abs(v) >= 1e3) return "₹" + (v/1e3).toFixed(1) + "K";
  return "₹" + v.toFixed(0);
}
function fmtNum(v) {
  return v.toLocaleString();
}

function uniqueSorted(arr, key) {
  return [...new Set(arr.map(r => r[key]))].sort();
}

function populateSelect(id, values) {
  const sel = document.getElementById(id);
  values.forEach(v => {
    const opt = document.createElement("option");
    opt.value = v; opt.textContent = v;
    sel.appendChild(opt);
  });
}

populateSelect("f-segment", uniqueSorted(RAW_DATA, "customer_segment"));
populateSelect("f-activity", uniqueSorted(RAW_DATA, "customer_activity"));
populateSelect("f-channel", uniqueSorted(RAW_DATA, "acquisition_channel"));
populateSelect("f-city", uniqueSorted(RAW_DATA, "city"));

let charts = {};

function groupSum(rows, key, valKey) {
  const m = {};
  rows.forEach(r => { m[r[key]] = (m[r[key]] || 0) + r[valKey]; });
  return m;
}
function groupAvg(rows, key, valKey) {
  const sum = {}, cnt = {};
  rows.forEach(r => { sum[r[key]] = (sum[r[key]]||0) + r[valKey]; cnt[r[key]] = (cnt[r[key]]||0) + 1; });
  const out = {};
  Object.keys(sum).forEach(k => out[k] = sum[k]/cnt[k]);
  return out;
}
function groupCount(rows, key) {
  const m = {};
  rows.forEach(r => { m[r[key]] = (m[r[key]] || 0) + 1; });
  return m;
}

function makeBar(id, labels, values, horizontal, color) {
  if (charts[id]) charts[id].destroy();
  const ctx = document.getElementById(id).getContext("2d");
  charts[id] = new Chart(ctx, {
    type: "bar",
    data: { labels, datasets: [{ data: values, backgroundColor: color || COLORS[0], borderRadius: 4 }] },
    options: {
      indexAxis: horizontal ? "y" : "x",
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { x: { grid: { display: false } }, y: { grid: { color: "#f0f0f0" } } }
    }
  });
}

function makeDoughnut(id, labels, values) {
  if (charts[id]) charts[id].destroy();
  const ctx = document.getElementById(id).getContext("2d");
  charts[id] = new Chart(ctx, {
    type: "doughnut",
    data: { labels, datasets: [{ data: values, backgroundColor: COLORS }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }
  });
}

const AGE_ORDER = ["18-25","26-35","36-45","46-55","56+"];
const TENURE_ORDER = ["<1 yr","1-2 yrs","2-3 yrs","3+ yrs"];

function render(rows) {
  // KPIs
  const totalRevenue = rows.reduce((a,r) => a + r.total_spend, 0);
  const totalOrders = rows.reduce((a,r) => a + r.total_orders, 0);
  const avgAOV = rows.length ? rows.reduce((a,r) => a + r.average_order_value, 0) / rows.length : 0;
  const atRisk = rows.filter(r => r.customer_activity === "At Risk");
  const revAtRisk = rows.filter(r => r.customer_activity === "At Risk" || r.customer_activity === "Inactive")
                         .reduce((a,r) => a + r.total_spend, 0);

  document.getElementById("kpi-customers").textContent = fmtNum(rows.length);
  document.getElementById("kpi-revenue").textContent = fmtCurrency(totalRevenue);
  document.getElementById("kpi-aov").textContent = fmtCurrency(avgAOV);
  document.getElementById("kpi-orders").textContent = fmtNum(totalOrders);
  document.getElementById("kpi-atrisk").textContent = fmtNum(atRisk.length);
  document.getElementById("kpi-revrisk").textContent = fmtCurrency(revAtRisk);
  document.getElementById("kpi-revrisk-pct").textContent = totalRevenue ? ((100*revAtRisk/totalRevenue).toFixed(1) + "% of filtered revenue (At Risk + Inactive)") : "";

  // Segment revenue
  const segSum = groupSum(rows, "customer_segment", "total_spend");
  const segLabels = Object.keys(segSum).sort((a,b)=>segSum[b]-segSum[a]);
  makeBar("chart-segment", segLabels, segLabels.map(k=>segSum[k]), false, COLORS[0]);

  // Activity doughnut
  const actCnt = groupCount(rows, "customer_activity");
  const actLabels = Object.keys(actCnt);
  makeDoughnut("chart-activity", actLabels, actLabels.map(k=>actCnt[k]));

  // Channel avg spend
  const chAvg = groupAvg(rows, "acquisition_channel", "total_spend");
  const chLabels = Object.keys(chAvg).sort((a,b)=>chAvg[b]-chAvg[a]);
  makeBar("chart-channel", chLabels, chLabels.map(k=>chAvg[k]), true, COLORS[1]);

  // Top cities
  const citySum = groupSum(rows, "city", "total_spend");
  const cityLabels = Object.keys(citySum).sort((a,b)=>citySum[b]-citySum[a]).slice(0,10);
  makeBar("chart-city", cityLabels, cityLabels.map(k=>citySum[k]), true, COLORS[2]);

  // Tenure band avg spend
  const tenAvg = groupAvg(rows, "tenure_band", "total_spend");
  const tenLabels = TENURE_ORDER.filter(k => k in tenAvg);
  makeBar("chart-tenure", tenLabels, tenLabels.map(k=>tenAvg[k]), false, COLORS[4]);

  // Age group counts
  const ageCnt = groupCount(rows, "age_group");
  const ageLabels = AGE_ORDER.filter(k => k in ageCnt);
  makeBar("chart-age", ageLabels, ageLabels.map(k=>ageCnt[k]), false, COLORS[3]);

  // Risk table: top-quartile spend AND at risk
  const spendVals = rows.map(r=>r.total_spend).sort((a,b)=>a-b);
  const p75 = spendVals.length ? spendVals[Math.floor(0.75*(spendVals.length-1))] : 0;
  const riskRows = rows.filter(r => r.customer_activity === "At Risk" && r.total_spend >= p75)
                        .sort((a,b) => b.total_spend - a.total_spend)
                        .slice(0, 25);
  const tbody = document.querySelector("#risk-table tbody");
  tbody.innerHTML = "";
  riskRows.forEach(r => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${r.customer_id}</td><td>${r.customer_name}</td><td>${r.city}</td>
      <td>${r.customer_segment}</td><td>${fmtCurrency(r.total_spend)}</td>
      <td>${r.total_orders}</td><td>${r.days_since_last_purchase}</td><td>${r.rfm_score}</td>`;
    tbody.appendChild(tr);
  });
  if (riskRows.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;color:#999;">No high-value at-risk customers in the current filter</td></tr>';
  }
}

function applyFilters() {
  const seg = document.getElementById("f-segment").value;
  const act = document.getElementById("f-activity").value;
  const ch = document.getElementById("f-channel").value;
  const city = document.getElementById("f-city").value;
  const filtered = RAW_DATA.filter(r =>
    (!seg || r.customer_segment === seg) &&
    (!act || r.customer_activity === act) &&
    (!ch || r.acquisition_channel === ch) &&
    (!city || r.city === city)
  );
  render(filtered);
}

["f-segment","f-activity","f-channel","f-city"].forEach(id => {
  document.getElementById(id).addEventListener("change", applyFilters);
});
document.getElementById("reset-filters").addEventListener("click", () => {
  ["f-segment","f-activity","f-channel","f-city"].forEach(id => document.getElementById(id).value = "");
  applyFilters();
});

render(RAW_DATA);
</script>
</body>
</html>
"""

html = html.replace("__DATA_JSON__", data_json)

with open("/home/claude/project/outputs/customer_analytics_dashboard.html", "w") as f:
    f.write(html)

print("Dashboard written:", len(html), "bytes")
