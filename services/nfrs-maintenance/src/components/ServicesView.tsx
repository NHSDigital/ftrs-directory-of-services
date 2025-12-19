import { useState } from 'react';
import { ServicesConfig } from '../types';
import { addService, updateService, deleteService } from '../api';
import ConfirmDialog from './ConfirmDialog';

interface Props {
  services: ServicesConfig;
  onServicesChange: (services: ServicesConfig) => void;
}

interface ServiceFormData {
  id: string;
  displayName: string;
}

export default function ServicesView({ services, onServicesChange }: Props) {
  const [editingService, setEditingService] = useState<ServiceFormData | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [deletingServiceId, setDeletingServiceId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<ServiceFormData>({ id: '', displayName: '' });

  const servicesList = Object.entries(services.services).map(([id, displayName]) => ({
    id,
    displayName
  })).sort((a, b) => a.displayName.localeCompare(b.displayName));

  const handleCreate = () => {
    setFormData({ id: '', displayName: '' });
    setIsCreating(true);
    setEditingService(null);
    setError(null);
  };

  const handleEdit = (service: ServiceFormData) => {
    setFormData({ ...service });
    setEditingService(service);
    setIsCreating(false);
    setError(null);
  };

  const handleDelete = (id: string) => {
    setDeletingServiceId(id);
  };

  const confirmDelete = async () => {
    if (!deletingServiceId) return;

    setSaving(true);
    setError(null);
    try {
      await deleteService(deletingServiceId);
      const newServices = { ...services.services };
      delete newServices[deletingServiceId];

      // Also remove from operations if present
      const newOperations = { ...services.operations };
      delete newOperations[deletingServiceId];

      onServicesChange({
        services: newServices,
        operations: newOperations
      });
      setDeletingServiceId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete service');
    } finally {
      setSaving(false);
    }
  };

  const handleSave = async () => {
    if (!formData.id.trim() || !formData.displayName.trim()) {
      setError('Both ID and Display Name are required');
      return;
    }

    // Validate ID format (lowercase, hyphens, no spaces)
    if (!/^[a-z0-9-]+$/.test(formData.id)) {
      setError('Service ID must be lowercase letters, numbers, and hyphens only');
      return;
    }

    setSaving(true);
    setError(null);
    try {
      if (isCreating) {
        if (services.services[formData.id]) {
          setError('A service with this ID already exists');
          setSaving(false);
          return;
        }
        await addService(formData.id, formData.displayName);
        onServicesChange({
          ...services,
          services: {
            ...services.services,
            [formData.id]: formData.displayName
          }
        });
      } else if (editingService) {
        await updateService(editingService.id, formData.displayName);
        onServicesChange({
          ...services,
          services: {
            ...services.services,
            [editingService.id]: formData.displayName
          }
        });
      }
      setEditingService(null);
      setIsCreating(false);
      setFormData({ id: '', displayName: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save service');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditingService(null);
    setIsCreating(false);
    setFormData({ id: '', displayName: '' });
    setError(null);
  };

  const getOperationCount = (serviceId: string): number => {
    return services.operations[serviceId]
      ? Object.keys(services.operations[serviceId]).length
      : 0;
  };

  return (
    <div>
      <div className="header">
        <h1>Services</h1>
        <button className="btn btn-primary" onClick={handleCreate}>
          + Add Service
        </button>
      </div>

      {error && (
        <div className="error-banner" style={{
          background: '#fce4e4',
          border: '1px solid #d5281b',
          borderRadius: '4px',
          padding: '0.75rem 1rem',
          marginBottom: '1rem',
          color: '#d5281b'
        }}>
          {error}
        </div>
      )}

      {servicesList.length === 0 ? (
        <div className="empty-state">
          <h3>No services defined</h3>
          <p>Click "Add Service" to create a new service.</p>
        </div>
      ) : (
        <div className="nfr-list">
          {servicesList.map(service => (
            <div key={service.id} className="nfr-card">
              <div className="nfr-card-header">
                <span className="nfr-code">{service.id}</span>
                <div className="nfr-card-actions">
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleEdit(service)}
                  >
                    Edit
                  </button>
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleDelete(service.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="nfr-requirement">{service.displayName}</div>
              <div className="nfr-meta">
                <span>{getOperationCount(service.id)} operations defined</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {(isCreating || editingService) && (
        <div className="modal-overlay" onClick={handleCancel}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{isCreating ? 'Add Service' : 'Edit Service'}</h2>
            </div>

            <div className="form-group">
              <label htmlFor="serviceId">Service ID</label>
              <input
                id="serviceId"
                type="text"
                value={formData.id}
                onChange={e => setFormData({ ...formData, id: e.target.value })}
                placeholder="e.g., crud-apis"
                disabled={!isCreating}
              />
              {isCreating && (
                <small style={{ color: '#768692', fontSize: '0.75rem' }}>
                  Lowercase letters, numbers, and hyphens only
                </small>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="displayName">Display Name</label>
              <input
                id="displayName"
                type="text"
                value={formData.displayName}
                onChange={e => setFormData({ ...formData, displayName: e.target.value })}
                placeholder="e.g., Ingress API"
              />
            </div>

            <div className="modal-actions">
              <button
                className="btn btn-secondary"
                onClick={handleCancel}
                disabled={saving}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}

      {deletingServiceId && (
        <ConfirmDialog
          title="Delete Service?"
          message={`Are you sure you want to delete "${services.services[deletingServiceId]}" (${deletingServiceId})? This will also remove any associated operations.`}
          confirmLabel="Delete"
          onConfirm={confirmDelete}
          onCancel={() => setDeletingServiceId(null)}
          loading={saving}
        />
      )}
    </div>
  );
}
