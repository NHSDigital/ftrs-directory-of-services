import { useState } from 'react';
import { NfrMetaFile, TeamMeta, ReleaseMeta, ServicesConfig } from '../types';
import { updateCatalog } from '../api';

interface Props {
  catalog: NfrMetaFile;
  services: ServicesConfig;
  onCatalogChange: (catalog: NfrMetaFile) => void;
}

interface EditState<T> {
  item: T | null;
  isNew: boolean;
}

export default function TeamsReleasesView({ catalog, services, onCatalogChange }: Props) {
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [teamEdit, setTeamEdit] = useState<EditState<TeamMeta>>({ item: null, isNew: false });
  const [releaseEdit, setReleaseEdit] = useState<EditState<ReleaseMeta>>({ item: null, isNew: false });

  const persistCatalog = async (nextCatalog: NfrMetaFile) => {
    setSaving(true);
    setError(null);
    try {
      await updateCatalog(nextCatalog);
      onCatalogChange(nextCatalog);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save catalog');
    } finally {
      setSaving(false);
    }
  };

  const handleAddTeam = () => {
    setTeamEdit({ item: { id: '', name: '', description: '', services: [] }, isNew: true });
    setError(null);
  };

  const handleAddRelease = () => {
    setReleaseEdit({ item: { id: '', name: '', description: '' }, isNew: true });
    setError(null);
  };

  const handleSaveTeamEdit = async () => {
    if (!teamEdit.item) return;
    const { id, name } = teamEdit.item;
    if (!id.trim() || !name.trim()) {
      setError('Team ID and name are required');
      return;
    }
    if (teamEdit.isNew) {
      if (catalog.teams.some(t => t.id === id)) {
        setError('A team with this ID already exists');
        return;
      }
      const nextCatalog: NfrMetaFile = { ...catalog, teams: [...catalog.teams, teamEdit.item] };
      await persistCatalog(nextCatalog);
    } else {
      const teams = catalog.teams.map(t => (t.id === id ? teamEdit.item! : t));
      const nextCatalog: NfrMetaFile = { ...catalog, teams };
      await persistCatalog(nextCatalog);
    }
    setTeamEdit({ item: null, isNew: false });
  };

  const handleSaveReleaseEdit = async () => {
    if (!releaseEdit.item) return;
    const { id, name } = releaseEdit.item;
    if (!id.trim() || !name.trim()) {
      setError('Release ID and name are required');
      return;
    }
    if (releaseEdit.isNew) {
      if (catalog.releases.some(r => r.id === id)) {
        setError('A release with this ID already exists');
        return;
      }
      const nextCatalog: NfrMetaFile = { ...catalog, releases: [...catalog.releases, releaseEdit.item] };
      await persistCatalog(nextCatalog);
    } else {
      const releases = catalog.releases.map(r => (r.id === id ? releaseEdit.item! : r));
      const nextCatalog: NfrMetaFile = { ...catalog, releases };
      await persistCatalog(nextCatalog);
    }
    setReleaseEdit({ item: null, isNew: false });
  };

  const handleDeleteTeam = async (id: string) => {
    const nextCatalog: NfrMetaFile = { ...catalog, teams: catalog.teams.filter(t => t.id !== id) };
    await persistCatalog(nextCatalog);
  };

  const handleDeleteRelease = async (id: string) => {
    const nextCatalog: NfrMetaFile = { ...catalog, releases: catalog.releases.filter(r => r.id !== id) };
    await persistCatalog(nextCatalog);
  };

  const handlePersist = async () => {
    await persistCatalog(catalog);
  };

  return (
    <div>
      <div className="header">
        <h1>Teams & Releases</h1>
        <button className="btn btn-primary" onClick={handlePersist} disabled={saving}>
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>

      {error && (
        <div className="empty-state" style={{ textAlign: 'left', padding: '1rem', border: '1px solid #d5281b', borderRadius: 4, color: '#d5281b' }}>
          <h3>Error</h3>
          <p>{error}</p>
        </div>
      )}

      <div className="controls-section">
        <div className="header" style={{ marginBottom: '1rem' }}>
          <h2>Teams</h2>
          <button className="btn btn-secondary btn-sm" onClick={handleAddTeam}>+ Add Team</button>
        </div>
        {catalog.teams.length === 0 ? (
          <div className="empty-state"><p>No teams defined.</p></div>
        ) : (
          <div className="nfr-list">
            {catalog.teams.map(team => (
              <div key={team.id} className="nfr-card">
                <div className="nfr-card-header">
                  <span className="nfr-code">{team.id}</span>
                  <div className="nfr-card-actions">
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setTeamEdit({ item: { ...team }, isNew: false })}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDeleteTeam(team.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <div className="nfr-requirement">{team.name}</div>
                {team.description && (
                  <div className="nfr-explanation">{team.description}</div>
                )}
                {team.services && team.services.length > 0 && (
                  <div className="tag-list" style={{ marginTop: '0.5rem' }}>
                    {team.services.map(sid => (
                      <span key={sid} className="tag tag-service">
                        {services.services[sid] || sid}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="controls-section" style={{ marginTop: '2rem' }}>
        <div className="header" style={{ marginBottom: '1rem' }}>
          <h2>Releases</h2>
          <button className="btn btn-secondary btn-sm" onClick={handleAddRelease}>+ Add Release</button>
        </div>
        {catalog.releases.length === 0 ? (
          <div className="empty-state"><p>No releases defined.</p></div>
        ) : (
          <div className="nfr-list">
            {catalog.releases.map(release => (
              <div key={release.id} className="nfr-card">
                <div className="nfr-card-header">
                  <span className="nfr-code">{release.id}</span>
                  <div className="nfr-card-actions">
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => setReleaseEdit({ item: { ...release }, isNew: false })}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDeleteRelease(release.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <div className="nfr-requirement">{release.name}</div>
                {release.description && (
                  <div className="nfr-explanation">{release.description}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {(teamEdit.item || releaseEdit.item) && (
        <div className="modal-overlay" onClick={() => { setTeamEdit({ item: null, isNew: false }); setReleaseEdit({ item: null, isNew: false }); }}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            {teamEdit.item && (
              <>
                <div className="modal-header">
                  <h2>{teamEdit.isNew ? 'Add Team' : 'Edit Team'}</h2>
                </div>
                <div className="form-group">
                  <label htmlFor="teamId">Team ID</label>
                  <input
                    id="teamId"
                    type="text"
                    value={teamEdit.item.id}
                    onChange={e => setTeamEdit({ ...teamEdit, item: { ...teamEdit.item!, id: e.target.value } })}
                    disabled={!teamEdit.isNew}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="teamName">Name</label>
                  <input
                    id="teamName"
                    type="text"
                    value={teamEdit.item.name}
                    onChange={e => setTeamEdit({ ...teamEdit, item: { ...teamEdit.item!, name: e.target.value } })}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="teamDesc">Description</label>
                  <textarea
                    id="teamDesc"
                    value={teamEdit.item.description || ''}
                    onChange={e => setTeamEdit({ ...teamEdit, item: { ...teamEdit.item!, description: e.target.value } })}
                  />
                </div>
                <div className="form-group">
                  <label>Services owned</label>
                  <div className="multi-select">
                    {Object.entries(services.services).map(([id, name]) => {
                      const current = teamEdit.item!.services || [];
                      const checked = current.includes(id);
                      return (
                        <label key={id} className="multi-select-option">
                          <input
                            type="checkbox"
                            checked={checked}
                            onChange={() => {
                              const next = checked
                                ? current.filter(s => s !== id)
                                : [...current, id];
                              setTeamEdit({ ...teamEdit, item: { ...teamEdit.item!, services: next } });
                            }}
                          />
                          {name}
                        </label>
                      );
                    })}
                  </div>
                </div>
                <div className="modal-actions">
                  <button className="btn btn-secondary" onClick={() => setTeamEdit({ item: null, isNew: false })}>Cancel</button>
                  <button className="btn btn-primary" onClick={handleSaveTeamEdit}>Save</button>
                </div>
              </>
            )}

            {releaseEdit.item && (
              <>
                <div className="modal-header">
                  <h2>{releaseEdit.isNew ? 'Add Release' : 'Edit Release'}</h2>
                </div>
                <div className="form-group">
                  <label htmlFor="releaseId">Release ID</label>
                  <input
                    id="releaseId"
                    type="text"
                    value={releaseEdit.item.id}
                    onChange={e => setReleaseEdit({ ...releaseEdit, item: { ...releaseEdit.item!, id: e.target.value } })}
                    disabled={!releaseEdit.isNew}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="releaseName">Name</label>
                  <input
                    id="releaseName"
                    type="text"
                    value={releaseEdit.item.name}
                    onChange={e => setReleaseEdit({ ...releaseEdit, item: { ...releaseEdit.item!, name: e.target.value } })}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="releaseDesc">Description</label>
                  <textarea
                    id="releaseDesc"
                    value={releaseEdit.item.description || ''}
                    onChange={e => setReleaseEdit({ ...releaseEdit, item: { ...releaseEdit.item!, description: e.target.value } })}
                  />
                </div>
                <div className="modal-actions">
                  <button className="btn btn-secondary" onClick={() => setReleaseEdit({ item: null, isNew: false })}>Cancel</button>
                  <button className="btn btn-primary" onClick={handleSaveReleaseEdit}>Save</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
