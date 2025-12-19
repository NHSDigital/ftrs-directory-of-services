import { useState, useEffect } from 'react';
import { NFR, Control, Operation, ServicesConfig } from '../types';
import ControlForm from './ControlForm';
import OperationForm from './OperationForm';

interface Props {
  nfr: NFR | null;
  defaultCode?: string;
  domain: string;
  services: ServicesConfig;
  explanation: string;
  onSave: (nfr: NFR, explanation: string) => void;
  onCancel: () => void;
  saving: boolean;
}

export default function NFRForm({ nfr, defaultCode, domain, services, explanation: initialExplanation, onSave, onCancel, saving }: Props) {
  const [formData, setFormData] = useState<NFR>({
    code: nfr?.code || defaultCode || '',
    requirement: nfr?.requirement || '',
    explanation: nfr?.explanation || '',
    stories: nfr?.stories || [],
    services: nfr?.services || [],
    controls: nfr?.controls || [],
    operations: nfr?.operations || []
  });

  const [explanationText, setExplanationText] = useState(initialExplanation);
  const [storiesText, setStoriesText] = useState((nfr?.stories || []).join(', '));
  const [showControlForm, setShowControlForm] = useState(false);
  const [editingControlIndex, setEditingControlIndex] = useState<number | null>(null);
  const [showOperationForm, setShowOperationForm] = useState(false);
  const [editingOperationIndex, setEditingOperationIndex] = useState<number | null>(null);

  const isPerformanceDomain = domain.toLowerCase() === 'performance';

  useEffect(() => {
    if (nfr) {
      setFormData({
        code: nfr.code,
        requirement: nfr.requirement,
        explanation: nfr.explanation || '',
        stories: nfr.stories || [],
        services: nfr.services || [],
        controls: nfr.controls || [],
        operations: nfr.operations || []
      });
      setStoriesText((nfr.stories || []).join(', '));
    }
    setExplanationText(initialExplanation);
  }, [nfr, initialExplanation]);

  const handleChange = (field: keyof NFR, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleStoriesChange = (text: string) => {
    setStoriesText(text);
    const stories = text.split(',').map(s => s.trim()).filter(s => s);
    handleChange('stories', stories);
  };

  const handleServiceToggle = (serviceId: string) => {
    const current = formData.services || [];
    const updated = current.includes(serviceId)
      ? current.filter(s => s !== serviceId)
      : [...current, serviceId];
    handleChange('services', updated);
  };

  const handleAddControl = () => {
    setEditingControlIndex(null);
    setShowControlForm(true);
  };

  const handleEditControl = (index: number) => {
    setEditingControlIndex(index);
    setShowControlForm(true);
  };

  const handleSaveControl = (control: Control) => {
    const controls = [...(formData.controls || [])];
    if (editingControlIndex !== null) {
      controls[editingControlIndex] = control;
    } else {
      controls.push(control);
    }
    handleChange('controls', controls);
    setShowControlForm(false);
    setEditingControlIndex(null);
  };

  const handleDeleteControl = (index: number) => {
    const controls = [...(formData.controls || [])];
    controls.splice(index, 1);
    handleChange('controls', controls);
  };

  const handleAddOperation = () => {
    setEditingOperationIndex(null);
    setShowOperationForm(true);
  };

  const handleEditOperation = (index: number) => {
    setEditingOperationIndex(index);
    setShowOperationForm(true);
  };

  const handleSaveOperation = (operation: Operation) => {
    const operations = [...(formData.operations || [])];
    if (editingOperationIndex !== null) {
      operations[editingOperationIndex] = operation;
    } else {
      operations.push(operation);
    }
    handleChange('operations', operations);
    setShowOperationForm(false);
    setEditingOperationIndex(null);
  };

  const handleDeleteOperation = (index: number) => {
    const operations = [...(formData.operations || [])];
    operations.splice(index, 1);
    handleChange('operations', operations);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Clean up empty arrays and empty strings
    const cleanedData: NFR = {
      code: formData.code,
      requirement: formData.requirement
    };

    // Note: explanation is now stored separately in cross-references file
    if (formData.stories && formData.stories.length > 0) cleanedData.stories = formData.stories;
    if (formData.services && formData.services.length > 0) cleanedData.services = formData.services;
    if (formData.controls && formData.controls.length > 0) cleanedData.controls = formData.controls;
    if (formData.operations && formData.operations.length > 0) cleanedData.operations = formData.operations;

    onSave(cleanedData, explanationText);
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>{nfr ? `Edit ${nfr.code}` : 'Create NFR'}</h2>
          <button className="btn btn-secondary btn-sm" onClick={onCancel}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="code">Code *</label>
              <input
                id="code"
                type="text"
                value={formData.code}
                onChange={e => handleChange('code', e.target.value)}
                placeholder="e.g., SEC-001"
                required
                disabled={!!nfr}
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="requirement">Requirement *</label>
            <textarea
              id="requirement"
              value={formData.requirement}
              onChange={e => handleChange('requirement', e.target.value)}
              placeholder="The non-functional requirement statement"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="explanation">Explanation (stored in cross-references)</label>
            <textarea
              id="explanation"
              value={explanationText}
              onChange={e => setExplanationText(e.target.value)}
              placeholder="Additional details about the requirement - stored in cross-references/nfr-explanations.yaml"
              style={{ minHeight: '120px' }}
            />
          </div>

          <div className="form-group">
            <label htmlFor="stories">Linked Stories (comma-separated)</label>
            <input
              id="stories"
              type="text"
              value={storiesText}
              onChange={e => handleStoriesChange(e.target.value)}
              placeholder="e.g., FTRS-123, FTRS-456"
            />
          </div>

          <div className="form-group">
            <label>Applicable Services</label>
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

          {/* Controls Section */}
          <div className="controls-section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h3>Controls ({(formData.controls || []).length})</h3>
              <button type="button" className="btn btn-secondary btn-sm" onClick={handleAddControl}>
                + Add Control
              </button>
            </div>

            {(formData.controls || []).map((ctrl, idx) => (
              <div key={idx} className="control-item">
                <div className="control-header">
                  <span className="control-id">{ctrl.control_id}</span>
                  <div>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleEditControl(idx)}
                      style={{ marginRight: '0.25rem' }}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDeleteControl(idx)}
                    >
                      Remove
                    </button>
                  </div>
                </div>
                <p style={{ fontSize: '0.875rem' }}>{ctrl.measure}</p>
              </div>
            ))}
          </div>

          {/* Operations Section (Performance domain) */}
          {isPerformanceDomain && (
            <div className="controls-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <h3>Performance Operations ({(formData.operations || []).length})</h3>
                <button type="button" className="btn btn-secondary btn-sm" onClick={handleAddOperation}>
                  + Add Operation
                </button>
              </div>

              {(formData.operations || []).map((op, idx) => (
                <div key={idx} className="operation-item">
                  <div className="operation-header">
                    <span className="operation-service">{op.service} / {op.operation_id}</span>
                    <div>
                      <button
                        type="button"
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleEditOperation(idx)}
                        style={{ marginRight: '0.25rem' }}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDeleteOperation(idx)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                  <div className="operation-targets">
                    {op.p50_target_ms && <span>P50: {op.p50_target_ms}ms</span>}
                    {op.p95_target_ms && <span>P95: {op.p95_target_ms}ms</span>}
                    {op.absolute_max_ms && <span>Max: {op.absolute_max_ms}ms</span>}
                  </div>
                </div>
              ))}
            </div>
          )}

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save NFR'}
            </button>
          </div>
        </form>

        {showControlForm && (
          <ControlForm
            control={editingControlIndex !== null ? formData.controls?.[editingControlIndex] : undefined}
            services={services}
            onSave={handleSaveControl}
            onCancel={() => {
              setShowControlForm(false);
              setEditingControlIndex(null);
            }}
          />
        )}

        {showOperationForm && (
          <OperationForm
            operation={editingOperationIndex !== null ? formData.operations?.[editingOperationIndex] : undefined}
            services={services}
            onSave={handleSaveOperation}
            onCancel={() => {
              setShowOperationForm(false);
              setEditingOperationIndex(null);
            }}
          />
        )}
      </div>
    </div>
  );
}
