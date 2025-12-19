import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { fetchDomains, fetchServices, fetchExplanations, fetchCatalog } from './api';
import { Domain, ServicesConfig, ExplanationsFile, NfrMetaFile } from './types';
import DomainView from './components/DomainView';
import ServicesView from './components/ServicesView';
import TeamsReleasesView from './components/TeamsReleasesView';

function App() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [services, setServices] = useState<ServicesConfig | null>(null);
  const [explanations, setExplanations] = useState<ExplanationsFile | null>(null);
  const [catalog, setCatalog] = useState<NfrMetaFile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [domainsData, servicesData, explanationsData, catalogData] = await Promise.all([
          fetchDomains(),
          fetchServices(),
          fetchExplanations(),
          fetchCatalog()
        ]);
        setDomains(domainsData);
        setServices(servicesData);
        setExplanations(explanationsData);
         setCatalog(catalogData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="empty-state"><h3>Error</h3><p>{error}</p></div>;
  }

  if (!services || !explanations || !catalog) {
    return <div className="empty-state"><h3>Error</h3><p>Failed to load configuration data.</p></div>;
  }

  return (
    <div className="app">
      <nav className="sidebar">
        <h1>NFR Maintenance</h1>
        <h2>Configuration</h2>
        <ul>
          <li>
            <NavLink
              to="/services"
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              Services
            </NavLink>
          </li>
          <li>
            <NavLink
              to="/teams-releases"
              className={({ isActive }) => isActive ? 'active' : ''}
            >
              Teams & Releases
            </NavLink>
          </li>
        </ul>
        <h2>Domains</h2>
        <ul>
          {domains.map(domain => (
            <li key={domain.name}>
              <NavLink
                to={`/domain/${domain.name}`}
                className={({ isActive }) => isActive ? 'active' : ''}
              >
                {domain.name.charAt(0).toUpperCase() + domain.name.slice(1)}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/" element={
            domains.length > 0
              ? <Navigate to={`/domain/${domains[0].name}`} replace />
              : <div className="empty-state"><h3>No domains found</h3></div>
          } />
          <Route
            path="/services"
            element={
              <ServicesView
                services={services}
                onServicesChange={setServices}
              />
            }
          />
          <Route
            path="/teams-releases"
            element={
              <TeamsReleasesView
                catalog={catalog}
                services={services}
                onCatalogChange={setCatalog}
              />
            }
          />
          <Route
            path="/domain/:domainName"
            element={
              <DomainView
                services={services}
                explanations={explanations}
                catalog={catalog}
                onExplanationsChange={setExplanations}
              />
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
