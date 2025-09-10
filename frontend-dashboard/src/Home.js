import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Home.css';

const brands = [
  { name: 'BMW', logo: '/logos/bmw.png' },
  { name: 'Audi', logo: '/logos/audi.png' },
  { name: 'VW', logo: '/logos/vw.png' },
  { name: 'Skoda', logo: '/logos/skoda.png' },
  { name: 'Mazda', logo: '/logos/mazda.png' },
  { name: 'Honda', logo: '/logos/honda.png' },
  { name: 'Toyota', logo: '/logos/toyota.png' },
  { name: 'Lexus', logo: '/logos/lexus.png' },
];

const VEHICLE_TYPES = ['combustion', 'ev', 'hybrid'];
const CURRENT_YEAR = new Date().getFullYear();

function Home({ setBackendResponse }) {
  const [rust, setRust] = useState(0);
  const [severity, setSeverity] = useState(0);
  const [flooded, setFlooded] = useState(false);
  const [selectedBrand, setSelectedBrand] = useState(null);
  const [showBrandDropdown, setShowBrandDropdown] = useState(false);
  const [accidentZone, setAccidentZone] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();

  function hasErrors() {
  const brandMissing = !selectedBrand;
  return brandMissing;
  }

  const handleBrandSelect = (brand) => {
    setSelectedBrand(brand);
    setShowBrandDropdown(false);
  };

  const handleZoneChange = (e) => {
    const val = e.target.value;
    setAccidentZone(val);
    if (val === 'none') setSeverity(0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitted(true);

    const form = e.currentTarget;
    const formInvalid = !e.currentTarget.checkValidity() || hasErrors();
    if (formInvalid) {
      form.reportValidity();
      const firstInvalid = form.querySelector(':invalid');
      if (firstInvalid) {
        firstInvalid.focus({ preventScroll: true });
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
      return;
    }

    if (!selectedBrand) {
      alert('Please select a brand.');
      return;
    }

    const zone = accidentZone || e.target.accidentzone.value;
    const severityToSend = zone === 'none' ? 0 : severity;

    const data = {
      brand: selectedBrand.name,
      year: parseInt(e.target.year.value, 10),
      odometer: parseInt(e.target.odometer.value, 10),
      vehicle_type: e.target.vehicletype.value,
      accident_zone: zone,
      grade_of_rust: rust,
      severity_of_accident: severityToSend,
      is_flooded: flooded,
      timebudget: parseInt(e.target.timebudget.value, 10),
    };
    
    try {
      const response = await fetch('http://localhost:5000/home/post-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const result = await response.json();
        setBackendResponse(result); 
        navigate('/dashboard');    
      } else {
        const text = await response.text();
        console.error('Backend error:', response.status, text);
      }
    } catch (error) {
      console.error('Error sending data:', error);
    }
  };

  const severityDisabled = accidentZone === 'none' || accidentZone === '';

  return (
    <div className="home-root">
      <h1>Predictive Vehicle Component Dismantling</h1>

      <form onSubmit={handleSubmit} noValidate className={submitted ? 'show-errors' : ''}>
        {/* Brand */}
        <div className="form-row-brand">
          <label className="brand-label">Brand</label>

          <div className="brand-dropdown-container">
            <button
              type="button"
              className={`brand-dropdown-toggle ${submitted && !selectedBrand ? 'error' : ''}`}
              aria-haspopup="listbox"
              aria-expanded={showBrandDropdown}
              aria-invalid={submitted && !selectedBrand ? 'true' : 'false'}
              onClick={() => setShowBrandDropdown((v) => !v)}
            >
              {selectedBrand ? (
                <span className="brand-selected">
                  <img
                    src={selectedBrand.logo}
                    alt={`${selectedBrand.name} logo`}
                    className="brand-logo"
                  />
                  {selectedBrand.name}
                </span>
              ) : (
                <span>Select a brand</span>
              )}
              <span className="dropdown-arrow" aria-hidden>▾</span>
            </button>

            {showBrandDropdown && (
              <div className="brand-dropdown-list" role="listbox">
                {brands.map((brand) => (
                  <button
                    type="button"
                    key={brand.name}
                    role="option"
                    className="brand-card"
                    onClick={() => handleBrandSelect(brand)}
                    aria-label={`Choose ${brand.name}`}
                  >
                    <img
                      src={brand.logo}
                      alt={`${brand.name} logo`}
                      className="brand-card-logo"
                    />
                    <span>{brand.name}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Grid fields */}
        <div className="form-grid">
          {/* Row 1 */}
          <div className="form-group">
            <label htmlFor="year">Manufacture Year</label>
            <input
              type="number"
              id="year"
              name="year"
              placeholder="Production year"
              required
              min="1980"
              max={CURRENT_YEAR}
            />
          </div>

          <div className="form-group">
            <label htmlFor="odometer">Odometer (km)</label>
            <input
              type="number"
              id="odometer"
              name="odometer"
              placeholder="Odometer reading"
              required
              min="5"
              step="1"
            />
          </div>

          <div className="form-group">
            <label htmlFor="vehicletype">Vehicle Type</label>
            <select id="vehicletype" name="vehicletype" required defaultValue="">
              <option value="" disabled hidden>Select vehicle type</option>
              {VEHICLE_TYPES.map((t) => (
                <option key={t} value={t}>{t[0].toUpperCase() + t.slice(1)}</option>
              ))}
            </select>
          </div>

          {/* Row 2: Rust + Accident Zone + Severity */}
          <div className="form-group">
            <label htmlFor="rust">Rust Level</label>
            <div className="range-inline">
              <input
                type="range"
                id="rust"
                name="rust"
                min="0"
                max="5"
                value={rust}
                onChange={(e) => setRust(Number(e.target.value))}
              />
              <span className="range-value">{rust}</span>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="accidentzone">Accident Zone</label>
            <select
              id="accidentzone"
              name="accidentzone"
              required
              value={accidentZone}
              onChange={handleZoneChange}
            >
              <option value="" disabled hidden>Select accident zone</option>
              <option value="none">None</option>
              <option value="front">Front</option>
              <option value="rear">Rear</option>
              <option value="side">Side</option>
            </select>
          </div>

          <div className={`inline-field form-group ${severityDisabled ? 'is-disabled' : ''}`}>
            <label htmlFor="severity">Accident Severity</label>
            <div className="range-inline">
              <input
                type="range"
                id="severity"
                name="severity"
                min="0"
                max="5"
                value={severity}
                onChange={(e) => setSeverity(Number(e.target.value))}
                disabled={severityDisabled}
                aria-disabled={severityDisabled}
              />
              <span className="range-value">{severity}</span>
            </div>
          </div>

          {/* Row 3: Time Budget (span 2) + Flooded */}
          <div className="form-group col-span-2">
            <label htmlFor="timebudget">Time Budget (min)</label>
            <input
              type="number"
              id="timebudget"
              name="timebudget"
              placeholder="Enter the time budget"
              required
              min="10"
            />
          </div>

          <div className="form-group">
            <label htmlFor="flooded">Flooded</label>
            <label className="switch">
              <input
                type="checkbox"
                id="flooded"
                name="flooded"
                checked={flooded}
                onChange={() => setFlooded((v) => !v)}
              />
              <span className="slider" />
            </label>
            <span className={`switch-state ${flooded ? 'on' : 'off'}`}>
            </span>
          </div>
        </div>


        <button type="submit" className="btn-submit">Submit</button>
      </form>
    </div>
  );
}

export default Home;
