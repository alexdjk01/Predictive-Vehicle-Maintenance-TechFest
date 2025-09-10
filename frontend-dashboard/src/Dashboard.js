import './Dashboard.css';

function Dashboard({ response }) {
  if (!response) {
    return <div>No data received yet.</div>;
  }

  // Safe lookups & fallbacks
  const vehicle = response.vehicle ?? {};
  const brand = vehicle.brand ?? null;
  const brandLogo = brand ? `/logos/${String(brand).toLowerCase()}.png` : null;

  const timeMin   = response.totals?.time_min ?? 0;
  const budgetMin = response.ui?.time_budget_min ?? timeMin;           // fallback = 100%
  const usedPct   = budgetMin > 0 ? Math.min(100, Math.round((timeMin / budgetMin) * 100)) : 0;
  const totalCo2 = response.totals?.co2_saved_kg ?? (response.selected_order || []).reduce((s, i) => s + (i.co2_saved_kg ?? 0), 0);

  // helper: clean step labels (remove underscores, trim)
  const cleanStep = (s) => {
  const str = String(s ?? '').replace(/_/g, ' ').trim();
  return str.charAt(0).toUpperCase() + str.slice(1);
};

  const mandatorySteps = Array.isArray(response.mandatory_first) ? response.mandatory_first : [];


  return (
    <div className="dashboard-container">

      {/* Vehicle strip (robust if backend omits vehicle) */}
      <section className="vehicle-strip">
        <div className="vehicle-main">
          {brandLogo && <img src={brandLogo} alt={`${brand} logo`} className="brand-inline" />}
          <div className="vehicle-heading">
            <div className="vehicle-line">
              <span className="veh-title">{brand ?? 'Plan Summary'}</span>
              {vehicle.year && <span className="veh-meta">• {vehicle.year}</span>}
            </div>
            <div className="veh-badges">
              {vehicle.vehicletype && <span className={`chip chip-${vehicle.vehicletype}`}>{vehicle.vehicletype}</span>}
              {typeof vehicle.odometer_km === 'number' && (
                <span className="chip chip-neutral">
                  {new Intl.NumberFormat().format(vehicle.odometer_km)} km
                </span>
              )}
            </div>
          </div>
        </div>

        {/* KPI row */}
        <div className="vehicle-kpis">
          <div className="kpi kpi-box">
            <div className="kpi-label">Time used</div>
            <div
              className="kpi-gauge"
              aria-label={`Time used ${usedPct}%`}
              style={{ '--kpi': `${usedPct}%` }}
            >
              <div className="kpi-gauge-text">{usedPct}%</div>
            </div>
          </div>

          <div className="kpi kpi-box">
            <div className="kpi-label">Expected Profit</div>
            <div className="kpi-big">
              €{Number(response.totals?.expected_profit_eur ?? 0).toFixed(2)}
            </div>
          </div>

          <div className="kpi kpi-box">
            <div className="kpi-label">CO₂ Saved</div>
            <div className="kpi-big">{totalCo2.toFixed(2)} kg</div>
          </div>

          <div className="kpi kpi-box">
            <div className="kpi-label">Total Time</div>
            <div className="kpi-big">{Number(timeMin).toFixed(2)} min</div>
          </div>
        </div>
      </section>

      {/* Mandatory step */}
      {mandatorySteps.length > 0 && (
        <section className="dashboard-section">
          <div className="mandatory-banner" role="alert" aria-label="Mandatory initial steps">
            <div>
              <div className="mandatory-title">
                Mandatory Initial Steps <span className="mandatory-icon" aria-hidden>⚠️</span>
              </div>
              <ol className="mandatory-steps">
                {mandatorySteps.map((s, i) => (
                  <li key={`${i}-${s}`}>{cleanStep(s)}</li>
                ))}
              </ol>
            </div>
          </div>
        </section>
      )}

      {/* Selected components */}
      <section className="dashboard-section">
        <h2 className="dashboard-subtitle">Selected Components</h2>
        <ul className="sel-list">
          {(response.selected_order ?? []).map((item) => (
            <li className="sel-item" key={`${item.component}-${item.pred_time_min}`}>
              <div className="sel-head">
                <span className="sel-name">{String(item.component).replace(/_/g, ' ')}</span>
                <span
                  className={`status-chip ${
                    item.decision === 'reuse'
                      ? 'ok'
                      : item.decision === 'recycle'
                      ? 'warn'
                      : 'muted'
                  }`}
                >
                  {item.decision || '—'}
                </span>
              </div>

              <div className="stat-grid">
                <div className="stat-card">
                  <div className="stat-label">Time</div>
                  <div className="stat-value">{Number(item.pred_time_min ?? 0).toFixed(2)} min</div>
                </div>

                <div className="stat-card">
                  <div className="stat-label">Success</div>
                  <div className="stat-value">{Math.round((item.success_prob ?? 0) * 100)}%</div>
                </div>

                <div className="stat-card">
                  <div className="stat-label">Profit</div>
                  <div className="stat-value">
                    €{(() => {
                        const best = Math.max(
                          item.reuse_profit_eur ?? Number.NEGATIVE_INFINITY,
                          item.recycle_profit_eur ?? Number.NEGATIVE_INFINITY,
                          item.expected_profit_eur ?? Number.NEGATIVE_INFINITY
                        );
                        return Number.isFinite(best) ? best.toFixed(2) : '0.00';
                      })()}
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-label">CO₂ Saved</div>
                  <div className="stat-value">{Number(item.co2_saved_kg ?? 0).toFixed(2)} kg</div>
                </div>
              </div>

            </li>
          ))}
        </ul>
      </section>

      {/* Skipped list */}
      {response.skipped && (
        <section className="dashboard-section">
          <h2 className="dashboard-subtitle">Skipped Components</h2>
          <ul className="skipped-ul">
            {Object.entries(response.skipped).map(([comp, reason]) => (
              <li key={comp}>
                <span className="skipped-name">{String(comp).replace(/_/g, ' ')}</span>
                <span className="skipped-reason"> — {reason}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

export default Dashboard;
