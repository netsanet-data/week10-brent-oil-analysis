import { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ReferenceLine, ResponsiveContainer
} from 'recharts';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://127.0.0.1:5000/api';

const CATEGORY_COLORS = {
  'Geopolitical Conflict': '#C0392B',
  'OPEC Policy': '#27AE60',
  'Economic Shock': '#8E44AD',
  'Sanctions/Policy': '#F39C12',
  'Market Event': '#16A085',
  'Geopolitical Shock': '#C0392B',
};

function App() {
  const [prices, setPrices] = useState([]);
  const [events, setEvents] = useState([]);
  const [changepoint, setChangepoint] = useState(null);
  const [startDate, setStartDate] = useState('1987-05-20');
  const [endDate, setEndDate] = useState('2022-11-14');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchChangepoint();
    fetchEvents();
  }, []);

  useEffect(() => {
    fetchPrices();
  }, [startDate, endDate]);

  const fetchPrices = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`${API_BASE}/prices`, {
        params: { start_date: startDate, end_date: endDate }
      });
      setPrices(res.data.data);
    } catch (err) {
      setError('Failed to load price data. Is the Flask backend running on port 5000?');
    } finally {
      setLoading(false);
    }
  };

  const fetchEvents = async () => {
    try {
      const res = await axios.get(`${API_BASE}/events`);
      setEvents(res.data.data);
    } catch (err) {
      console.error('Failed to load events', err);
    }
  };

  const fetchChangepoint = async () => {
    try {
      const res = await axios.get(`${API_BASE}/changepoint`);
      setChangepoint(res.data);
    } catch (err) {
      console.error('Failed to load change point results', err);
    }
  };

  const filteredEvents = categoryFilter === 'All'
    ? events
    : events.filter(e => e.category === categoryFilter);

  const visibleEvents = filteredEvents.filter(
    e => e.date >= startDate && e.date <= endDate
  );

  const categories = ['All', ...new Set(events.map(e => e.category))];

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Brent Crude Oil — Change Point Analysis Dashboard</h1>
        <p className="subtitle">Birhan Energies | Week 10 Challenge</p>
      </header>

      {changepoint && (
        <div className="stats-panel">
          <div className="stat-card">
            <span className="stat-label">Detected Change Point</span>
            <span className="stat-value">{changepoint.tau_date}</span>
            <span className="stat-sub">94% CI: {changepoint.credible_interval_lower} to {changepoint.credible_interval_upper}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Mean Price Before</span>
            <span className="stat-value">${changepoint.mu1_mean}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Mean Price After</span>
            <span className="stat-value">${changepoint.mu2_mean}</span>
          </div>
          <div className="stat-card highlight">
            <span className="stat-label">Change</span>
            <span className="stat-value">+{changepoint.pct_change}%</span>
            <span className="stat-sub">{(changepoint.prob_increase * 100).toFixed(1)}% posterior probability</span>
          </div>
        </div>
      )}

      <div className="filters">
        <div className="filter-group">
          <label>Start Date</label>
          <input type="date" value={startDate} min="1987-05-20" max="2022-11-14"
                 onChange={e => setStartDate(e.target.value)} />
        </div>
        <div className="filter-group">
          <label>End Date</label>
          <input type="date" value={endDate} min="1987-05-20" max="2022-11-14"
                 onChange={e => setEndDate(e.target.value)} />
        </div>
        <div className="filter-group">
          <label>Event Category</label>
          <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
            {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
          </select>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {loading && <div className="loading-banner">Loading price data...</div>}

      <div className="chart-container">
        <ResponsiveContainer width="100%" height={500}>
          <LineChart data={prices} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={60} />
            <YAxis label={{ value: 'Price (USD/barrel)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="price" stroke="#1f4e79" dot={false}
                  strokeWidth={1.2} name="Brent Price (USD)" />

            {changepoint && changepoint.tau_date >= startDate && changepoint.tau_date <= endDate && (
              <ReferenceLine
                x={changepoint.tau_date}
                stroke="#000000"
                strokeWidth={2}
                label={{ value: 'Change Point', position: 'top', fontSize: 11 }}
              />
            )}

            {visibleEvents.map((evt, idx) => (
              <ReferenceLine
                key={idx}
                x={evt.date}
                stroke={CATEGORY_COLORS[evt.category] || '#999'}
                strokeDasharray="4 4"
                strokeOpacity={0.6}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="events-list">
        <h2>Events in Selected Range ({visibleEvents.length})</h2>
        <table>
          <thead>
            <tr><th>Date</th><th>Event</th><th>Category</th><th>Expected Impact</th></tr>
          </thead>
          <tbody>
            {visibleEvents.map((evt, idx) => (
              <tr key={idx}>
                <td>{evt.date}</td>
                <td>{evt.event_name}</td>
                <td>
                  <span className="category-badge" style={{ backgroundColor: CATEGORY_COLORS[evt.category] || '#999' }}>
                    {evt.category}
                  </span>
                </td>
                <td>{evt.expected_impact}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="transparency-panel">
        <h2>Model Transparency: Quantifying Uncertainty</h2>
        <p className="transparency-note">
          This model is a Bayesian change point model, not a classifier, so
          traditional feature-attribution tools (e.g. SHAP) do not apply.
          Instead, transparency comes from the full posterior distribution
          below: rather than a single point estimate, the model reports a
          <em> range</em> of plausible change point dates and price levels,
          each with an explicit probability. A narrow, sharply peaked
          posterior (as seen here) indicates high model confidence in the
          detected shift.
        </p>
        <img
          src="/posterior_distributions.png"
          alt="Posterior distributions of the change point date (tau) and mean price before/after the shift"
          className="posterior-image"
        />
        <p className="transparency-caption">
          Left: posterior distribution of the change point date (tau).
          Center: posterior distributions of mean price before (mu1) vs.
          after (mu2). Right: posterior of the price shift (mu2 - mu1).
        </p>
      </div>
    </div>
  );
}

export default App;