import { useState, useEffect } from 'react';
import { Operation, ServicesConfig } from '../types';

interface Props {
  operation?: Operation;
  services: ServicesConfig;
  onSave: (operation: Operation) => void;
  onCancel: () => void;
}

const STATUSES = ['draft', 'approved', 'implemented', 'verified', 'deprecated'];

export default function OperationForm({ operation, services, onSave, onCancel }: Props) {
  const [formData, setFormData] = useState<Operation>({
    service: operation?.service || '',
    operation_id: operation?.operation_id || '',
    p50_target_ms: operation?.p50_target_ms || '',
    p95_target_ms: operation?.p95_target_ms || '',
    absolute_max_ms: operation?.absolute_max_ms || '',
    burst_tps_target: operation?.burst_tps_target || '',
    sustained_tps_target: operation?.sustained_tps_target || '',
    max_request_payload_bytes: operation?.max_request_payload_bytes || '',
    status: operation?.status || 'draft',
    rationale: operation?.rationale || '',
    stories: operation?.stories || []
  });

  const [storiesText, setStoriesText] = useState((operation?.stories || []).join(', '));
  const [selectedService, setSelectedService] = useState(operation?.service || '');

  useEffect(() => {
    if (operation) {
      setFormData({
        service: operation.service,
        operation_id: operation.operation_id,
        p50_target_ms: operation.p50_target_ms || '',
        p95_target_ms: operation.p95_target_ms || '',
        absolute_max_ms: operation.absolute_max_ms || '',
        burst_tps_target: operation.burst_tps_target || '',
        sustained_tps_target: operation.sustained_tps_target || '',
        max_request_payload_bytes: operation.max_request_payload_bytes || '',
        status: operation.status || 'draft',
        rationale: operation.rationale || '',
        stories: operation.stories || []
      });
      setStoriesText((operation.stories || []).join(', '));
      setSelectedService(operation.service);
    }
  }, [operation]);

  const handleChange = (field: keyof Operation, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleServiceChange = (serviceId: string) => {
    setSelectedService(serviceId);
    handleChange('service', serviceId);
    // Reset operation_id when service changes
    if (serviceId !== formData.service) {
      handleChange('operation_id', '');
    }
  };

  const handleStoriesChange = (text: string) => {
    setStoriesText(text);
    const stories = text.split(',').map(s => s.trim()).filter(s => s);
    handleChange('stories', stories);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Clean up and convert numeric fields
    const cleanedData: Operation = {
      service: formData.service,
      operation_id: formData.operation_id
    };

    // Convert numeric fields
    if (formData.p50_target_ms) {
      cleanedData.p50_target_ms = Number(formData.p50_target_ms) || formData.p50_target_ms;
    }
    if (formData.p95_target_ms) {
      cleanedData.p95_target_ms = Number(formData.p95_target_ms) || formData.p95_target_ms;
    }
    if (formData.absolute_max_ms) {
      cleanedData.absolute_max_ms = Number(formData.absolute_max_ms) || formData.absolute_max_ms;
    }
    if (formData.burst_tps_target) {
      cleanedData.burst_tps_target = Number(formData.burst_tps_target) || formData.burst_tps_target;
    }
    if (formData.sustained_tps_target) {
      cleanedData.sustained_tps_target = Number(formData.sustained_tps_target) || formData.sustained_tps_target;
    }
    if (formData.max_request_payload_bytes) {
      cleanedData.max_request_payload_bytes = Number(formData.max_request_payload_bytes) || formData.max_request_payload_bytes;
    }

    if (formData.status) cleanedData.status = formData.status;
    if (formData.rationale) cleanedData.rationale = formData.rationale;
    if (formData.stories && formData.stories.length > 0) cleanedData.stories = formData.stories;

    onSave(cleanedData);
  };

  // Get available operations for selected service
  const availableOperations = selectedService && services.operations[selectedService]
    ? Object.entries(services.operations[selectedService])
    : [];

  return (
    <div className="modal-overlay" style={{ zIndex: 1001 }}>
      <div className="modal" style={{ maxWidth: '600px' }}>
        <div className="modal-header">
          <h2>{operation ? 'Edit Operation' : 'Add Performance Operation'}</h2>
          <button className="btn btn-secondary btn-sm" onClick={onCancel}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="service">Service *</label>
              <select
                id="service"
                value={formData.service}
                onChange={e => handleServiceChange(e.target.value)}
                required
              >
                <option value="">Select a service</option>
                {Object.entries(services.services).map(([id, name]) => (
                  <option key={id} value={id}>{name}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="operation_id">Operation ID *</label>
              {availableOperations.length > 0 ? (
                <select
                  id="operation_id"
                  value={formData.operation_id}
                  onChange={e => handleChange('operation_id', e.target.value)}
                  required
                >
                  <option value="">Select an operation</option>
                  {availableOperations.map(([id, name]) => (
                    <option key={id} value={id}>{name} ({id})</option>
                  ))}
                </select>
              ) : (
                <input
                  id="operation_id"
                  type="text"
                  value={formData.operation_id}
                  onChange={e => handleChange('operation_id', e.target.value)}
                  placeholder="Enter operation ID"
                  required
                />
              )}
            </div>
          </div>

          <h4 style={{ marginTop: '1rem', marginBottom: '0.5rem', color: '#4c6272' }}>
            Latency Targets (ms)
          </h4>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="p50_target_ms">P50 Target</label>
              <input
                id="p50_target_ms"
                type="number"
                value={formData.p50_target_ms}
                onChange={e => handleChange('p50_target_ms', e.target.value)}
                placeholder="e.g., 150"
              />
            </div>

            <div className="form-group">
              <label htmlFor="p95_target_ms">P95 Target</label>
              <input
                id="p95_target_ms"
                type="number"
                value={formData.p95_target_ms}
                onChange={e => handleChange('p95_target_ms', e.target.value)}
                placeholder="e.g., 300"
              />
            </div>

            <div className="form-group">
              <label htmlFor="absolute_max_ms">Absolute Max</label>
              <input
                id="absolute_max_ms"
                type="number"
                value={formData.absolute_max_ms}
                onChange={e => handleChange('absolute_max_ms', e.target.value)}
                placeholder="e.g., 500"
              />
            </div>
          </div>

          <h4 style={{ marginTop: '1rem', marginBottom: '0.5rem', color: '#4c6272' }}>
            Throughput Targets
          </h4>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="burst_tps_target">Burst TPS</label>
              <input
                id="burst_tps_target"
                type="number"
                value={formData.burst_tps_target}
                onChange={e => handleChange('burst_tps_target', e.target.value)}
                placeholder="e.g., 100"
              />
            </div>

            <div className="form-group">
              <label htmlFor="sustained_tps_target">Sustained TPS</label>
              <input
                id="sustained_tps_target"
                type="number"
                value={formData.sustained_tps_target}
                onChange={e => handleChange('sustained_tps_target', e.target.value)}
                placeholder="e.g., 50"
              />
            </div>

            <div className="form-group">
              <label htmlFor="max_request_payload_bytes">Max Payload (bytes)</label>
              <input
                id="max_request_payload_bytes"
                type="number"
                value={formData.max_request_payload_bytes}
                onChange={e => handleChange('max_request_payload_bytes', e.target.value)}
                placeholder="e.g., 10240"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="op-status">Status</label>
              <select
                id="op-status"
                value={formData.status}
                onChange={e => handleChange('status', e.target.value)}
              >
                {STATUSES.map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="op-rationale">Rationale</label>
            <textarea
              id="op-rationale"
              value={formData.rationale}
              onChange={e => handleChange('rationale', e.target.value)}
              placeholder="Why these targets are set"
            />
          </div>

          <div className="form-group">
            <label htmlFor="op-stories">Linked Stories (comma-separated)</label>
            <input
              id="op-stories"
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
              {operation ? 'Update Operation' : 'Add Operation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
