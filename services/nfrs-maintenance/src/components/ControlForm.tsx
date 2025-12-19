import { useState, useEffect } from 'react';
import { Control, Operation, ServicesConfig } from '../types';

interface Props {
  control?: Control;
  services: ServicesConfig;
  operations: Operation[];
  onSave: (control: Control) => void;
  onCancel: () => void;
}

const ENVIRONMENTS = ['dev', 'int', 'ref', 'prod'];
const STATUSES = ['draft', 'approved', 'implemented', 'verified', 'deprecated'];

export default function ControlForm({ control, services, operations, onSave, onCancel }: Props) {
  const getServiceName = (id: string): string => {
    return services.services[id] || id;
  };

  const [formData, setFormData] = useState<Control>({
    control_id: control?.control_id || '',
    measure: control?.measure || '',
    threshold: control?.threshold || '',
    tooling: control?.tooling || '',
    cadence: control?.cadence || '',
    environments: control?.environments || [],
    services: control?.services || [],
    operation_id: control?.operation_id || '',
    operation_ids: control?.operation_ids || (control?.operation_id ? [control.operation_id] : []),
    status: control?.status || 'draft',
    rationale: control?.rationale || '',
    stories: control?.stories || []
  });

  const [storiesText, setStoriesText] = useState((control?.stories || []).join(', '));

  useEffect(() => {
    if (control) {
      setFormData({
        control_id: control.control_id,
        measure: control.measure,
        threshold: control.threshold || '',
        tooling: control.tooling || '',
        cadence: control.cadence || '',
        environments: control.environments || [],
        services: control.services || [],
        operation_id: control.operation_id || '',
        operation_ids: control.operation_ids || (control.operation_id ? [control.operation_id] : []),
        status: control.status || 'draft',
        rationale: control.rationale || '',
        stories: control.stories || []
      });
      setStoriesText((control.stories || []).join(', '));
    }
  }, [control]);

  const handleChange = (field: keyof Control, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleStoriesChange = (text: string) => {
    setStoriesText(text);
    const stories = text.split(',').map(s => s.trim()).filter(s => s);
    handleChange('stories', stories);
  };

  const handleEnvironmentToggle = (env: string) => {
    const current = formData.environments || [];
    const updated = current.includes(env)
      ? current.filter(e => e !== env)
      : [...current, env];
    handleChange('environments', updated);
  };

  const handleServiceToggle = (serviceId: string) => {
    const current = formData.services || [];
    const updated = current.includes(serviceId)
      ? current.filter(s => s !== serviceId)
      : [...current, serviceId];
    handleChange('services', updated);
  };

  const handleOperationToggle = (operationId: string) => {
    const current = formData.operation_ids || [];
    const updated = current.includes(operationId)
      ? current.filter(id => id !== operationId)
      : [...current, operationId];
    handleChange('operation_ids', updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Clean up empty fields
    const cleanedData: Control = {
      control_id: formData.control_id,
      measure: formData.measure
    };

    if (formData.threshold) cleanedData.threshold = formData.threshold;
    if (formData.tooling) cleanedData.tooling = formData.tooling;
    if (formData.cadence) cleanedData.cadence = formData.cadence;
    if (formData.environments && formData.environments.length > 0) cleanedData.environments = formData.environments;
    if (formData.services && formData.services.length > 0) cleanedData.services = formData.services;
    if (formData.operation_ids && formData.operation_ids.length > 0) cleanedData.operation_ids = formData.operation_ids;
    if (formData.status) cleanedData.status = formData.status;
    if (formData.rationale) cleanedData.rationale = formData.rationale;
    if (formData.stories && formData.stories.length > 0) cleanedData.stories = formData.stories;

    onSave(cleanedData);
  };

  return (
    <div className="modal-overlay" style={{ zIndex: 1001 }}>
      <div className="modal" style={{ maxWidth: '600px' }}>
        <div className="modal-header">
          <h2>{control ? 'Edit Control' : 'Add Control'}</h2>
          <button className="btn btn-secondary btn-sm" onClick={onCancel}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="control_id">Control ID *</label>
            <input
              id="control_id"
              type="text"
              value={formData.control_id}
              onChange={e => handleChange('control_id', e.target.value)}
              placeholder="e.g., crypto-cipher-policy"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="measure">Measure *</label>
            <textarea
              id="measure"
              value={formData.measure}
              onChange={e => handleChange('measure', e.target.value)}
              placeholder="What is being measured/enforced"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="threshold">Threshold</label>
            <textarea
              id="threshold"
              value={formData.threshold}
              onChange={e => handleChange('threshold', e.target.value)}
              placeholder="Acceptance criteria or target"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tooling">Tooling</label>
              <input
                id="tooling"
                type="text"
                value={formData.tooling}
                onChange={e => handleChange('tooling', e.target.value)}
                placeholder="Tools used for verification"
              />
            </div>

            <div className="form-group">
              <label htmlFor="cadence">Cadence</label>
              <input
                id="cadence"
                type="text"
                value={formData.cadence}
                onChange={e => handleChange('cadence', e.target.value)}
                placeholder="e.g., CI per change, weekly"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="status">Status</label>
              <select
                id="status"
                value={formData.status}
                onChange={e => handleChange('status', e.target.value)}
              >
                {STATUSES.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Operations covered</label>
              {operations.length === 0 ? (
                <p style={{ fontSize: '0.875rem', color: '#6f777b' }}>
                  No operations defined for this NFR.
                </p>
              ) : (
                <div className="multi-select">
                  {operations.map(op => {
                    const label = `${getServiceName(op.service)} / ${op.operation_id}`;
                    return (
                      <label key={`${op.service}:${op.operation_id}`} className="multi-select-option">
                        <input
                          type="checkbox"
                          checked={(formData.operation_ids || []).includes(op.operation_id)}
                          onChange={() => handleOperationToggle(op.operation_id)}
                        />
                        {label}
                      </label>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          <div className="form-group">
            <label>Environments</label>
            <div className="multi-select">
              {ENVIRONMENTS.map(env => (
                <label key={env} className="multi-select-option">
                  <input
                    type="checkbox"
                    checked={(formData.environments || []).includes(env)}
                    onChange={() => handleEnvironmentToggle(env)}
                  />
                  {env}
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Services</label>
            <div className="multi-select">
              {Object.entries(services.services).map(([id, name]) => (
                <label key={id} className="multi-select-option">
                  <input
                    type="checkbox"
                    checked={(formData.services || []).includes(id)}
                    onChange={() => handleServiceToggle(id)}
                  />
                  {name}
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="rationale">Rationale</label>
            <textarea
              id="rationale"
              value={formData.rationale}
              onChange={e => handleChange('rationale', e.target.value)}
              placeholder="Why this control is needed"
            />
          </div>

          <div className="form-group">
            <label htmlFor="control-stories">Linked Stories (comma-separated)</label>
            <input
              id="control-stories"
              type="text"
              value={storiesText}
              onChange={e => handleStoriesChange(e.target.value)}
              placeholder="e.g., FTRS-123, FTRS-456"
            />
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              {control ? 'Update Control' : 'Add Control'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
