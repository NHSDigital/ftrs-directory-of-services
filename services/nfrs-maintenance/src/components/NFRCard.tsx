import { NFR, ServicesConfig } from '../types';

interface Props {
  nfr: NFR;
  services: ServicesConfig;
  explanation: string;
  onEdit: () => void;
  onDelete: () => void;
}

export default function NFRCard({ nfr, services, explanation, onEdit, onDelete }: Props) {
  const getServiceName = (id: string): string => {
    return services.services[id] || id;
  };

  const allServices = new Set<string>();

  // Collect services from NFR level
  nfr.services?.forEach(s => allServices.add(s));

  // Collect services from controls
  nfr.controls?.forEach(ctrl => {
    ctrl.services?.forEach(s => allServices.add(s));
  });

  // Collect services from operations
  nfr.operations?.forEach(op => {
    allServices.add(op.service);
  });

  const allEnvironments = new Set<string>();
  nfr.controls?.forEach(ctrl => {
    ctrl.environments?.forEach(e => allEnvironments.add(e));
  });

  return (
    <div className="nfr-card">
      <div className="nfr-card-header">
        <span className="nfr-code">{nfr.code}</span>
        <div className="nfr-card-actions">
          <button className="btn btn-secondary btn-sm" onClick={onEdit}>
            Edit
          </button>
          <button className="btn btn-danger btn-sm" onClick={onDelete}>
            Delete
          </button>
        </div>
      </div>

      <div className="nfr-requirement">{nfr.requirement}</div>

      {explanation && (
        <div className="nfr-explanation">{explanation}</div>
      )}

      <div className="nfr-meta">
        {allServices.size > 0 && (
          <div className="tag-list">
            {Array.from(allServices).map(s => (
              <span key={s} className="tag tag-service">{getServiceName(s)}</span>
            ))}
          </div>
        )}
        {allEnvironments.size > 0 && (
          <div className="tag-list">
            {Array.from(allEnvironments).map(e => (
              <span key={e} className="tag tag-env">{e}</span>
            ))}
          </div>
        )}
        {nfr.teams && nfr.teams.length > 0 && (
          <div className="tag-list">
            {nfr.teams.map(team => (
              <span key={team} className="tag tag-team">{team}</span>
            ))}
          </div>
        )}
        {nfr.releases && nfr.releases.length > 0 && (
          <div className="tag-list">
            {nfr.releases.map(rel => (
              <span key={rel.id} className="tag tag-release">
                {rel.id}{rel.overall_status ? ` (${rel.overall_status})` : ''}
              </span>
            ))}
          </div>
        )}
        {nfr.stories && nfr.stories.length > 0 && (
          <span>{nfr.stories.length} linked stories</span>
        )}
      </div>

      {nfr.controls && nfr.controls.length > 0 && (
        <div className="controls-section">
          <h3>Controls ({nfr.controls.length})</h3>
          {nfr.controls.map((ctrl, idx) => (
            <div key={idx} className="control-item">
              <div className="control-header">
                <span className="control-id">{ctrl.control_id}</span>
                {ctrl.status && <span className="tag">{ctrl.status}</span>}
              </div>
              <p style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>{ctrl.measure}</p>
              <div className="control-details">
                {ctrl.threshold && (
                  <span>
                    <label>Threshold</label>
                    {ctrl.threshold}
                  </span>
                )}
                {ctrl.cadence && (
                  <span>
                    <label>Cadence</label>
                    {ctrl.cadence}
                  </span>
                )}
                {ctrl.tooling && (
                  <span>
                    <label>Tooling</label>
                    {ctrl.tooling}
                  </span>
                )}
                {ctrl.operation_ids && ctrl.operation_ids.length > 0 && (
                  <span>
                    <label>Operations</label>
                    <div className="tag-list">
                      {(ctrl.operation_ids || []).map(opId => {
                        const op = nfr.operations?.find(o => o.operation_id === opId);
                        const serviceName = op ? getServiceName(op.service) : undefined;
                        const label = serviceName ? `${serviceName} / ${opId}` : opId;
                        return (
                          <span key={opId} className="tag tag-operation">
                            {label}
                          </span>
                        );
                      })}
                    </div>
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {nfr.operations && nfr.operations.length > 0 && (
        <div className="controls-section">
          <h3>Performance Operations ({nfr.operations.length})</h3>
          {nfr.operations.map((op, idx) => (
            <div key={idx} className="operation-item">
              <div className="operation-header">
                <span className="operation-service">
                  {getServiceName(op.service)} / {op.operation_id}
                </span>
                {op.status && <span className="tag">{op.status}</span>}
              </div>
              <div className="operation-targets">
                {op.p50_target_ms && (
                  <span>
                    <label>P50</label>
                    {op.p50_target_ms}ms
                  </span>
                )}
                {op.p95_target_ms && (
                  <span>
                    <label>P95</label>
                    {op.p95_target_ms}ms
                  </span>
                )}
                {op.absolute_max_ms && (
                  <span>
                    <label>Max</label>
                    {op.absolute_max_ms}ms
                  </span>
                )}
                {op.burst_tps_target && (
                  <span>
                    <label>Burst TPS</label>
                    {op.burst_tps_target}
                  </span>
                )}
              </div>
              {op.rationale && (
                <p style={{ fontSize: '0.75rem', color: '#5c4b00', marginTop: '0.5rem' }}>
                  {op.rationale}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
