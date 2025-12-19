import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { fetchNFRs, addNFR, updateNFR, deleteNFR, updateExplanation } from '../api';
import { NFR, NFRFile, ServicesConfig, ExplanationsFile } from '../types';
import NFRCard from './NFRCard';
import NFRForm from './NFRForm';
import ConfirmDialog from './ConfirmDialog';

interface Props {
  services: ServicesConfig;
  explanations: ExplanationsFile;
  onExplanationsChange: (explanations: ExplanationsFile) => void;
}

export default function DomainView({ services, explanations, onExplanationsChange }: Props) {
  const { domainName } = useParams<{ domainName: string }>();
  const [nfrFile, setNfrFile] = useState<NFRFile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingNfr, setEditingNfr] = useState<NFR | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [deletingNfr, setDeletingNfr] = useState<NFR | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!domainName) return;

    setLoading(true);
    setError(null);

    fetchNFRs(domainName)
      .then(data => {
        setNfrFile(data);
      })
      .catch(err => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [domainName]);

  const getNextCode = (): string => {
    if (!nfrFile || !domainName) return '';
    const prefix = domainName.toUpperCase().substring(0, 4);
    const existingCodes = nfrFile.nfrs.map(n => {
      const match = n.code.match(/\d+$/);
      return match ? parseInt(match[0], 10) : 0;
    });
    const maxCode = Math.max(0, ...existingCodes);
    return `${prefix}-${String(maxCode + 1).padStart(3, '0')}`;
  };

  const handleCreate = () => {
    setEditingNfr(null);
    setIsCreating(true);
  };

  const handleEdit = (nfr: NFR) => {
    setEditingNfr(nfr);
    setIsCreating(false);
  };

  const handleDelete = (nfr: NFR) => {
    setDeletingNfr(nfr);
  };

  const confirmDelete = async () => {
    if (!deletingNfr || !domainName) return;

    setSaving(true);
    try {
      await deleteNFR(domainName, deletingNfr.code);
      setNfrFile(prev => prev ? {
        ...prev,
        nfrs: prev.nfrs.filter(n => n.code !== deletingNfr.code)
      } : null);
      setDeletingNfr(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete');
    } finally {
      setSaving(false);
    }
  };

  const handleSave = async (nfr: NFR, explanation: string) => {
    if (!domainName) return;

    setSaving(true);
    try {
      if (isCreating) {
        await addNFR(domainName, nfr);
        setNfrFile(prev => prev ? {
          ...prev,
          nfrs: [...prev.nfrs, nfr]
        } : null);
      } else if (editingNfr) {
        await updateNFR(domainName, editingNfr.code, nfr);
        setNfrFile(prev => prev ? {
          ...prev,
          nfrs: prev.nfrs.map(n => n.code === editingNfr.code ? nfr : n)
        } : null);
      }

      // Save explanation to cross-references file
      await updateExplanation(nfr.code, explanation);
      onExplanationsChange({
        ...explanations,
        explanations: {
          ...explanations.explanations,
          [nfr.code]: explanation
        }
      });

      setEditingNfr(null);
      setIsCreating(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditingNfr(null);
    setIsCreating(false);
  };

  if (loading) {
    return <div className="loading">Loading NFRs...</div>;
  }

  if (error) {
    return (
      <div className="empty-state">
        <h3>Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!nfrFile) {
    return (
      <div className="empty-state">
        <h3>No data</h3>
        <p>Could not load NFR data for this domain.</p>
      </div>
    );
  }

  const displayName = domainName
    ? domainName.charAt(0).toUpperCase() + domainName.slice(1)
    : '';

  return (
    <div>
      <div className="header">
        <h1>{displayName} NFRs</h1>
        <button className="btn btn-primary" onClick={handleCreate}>
          + Add NFR
        </button>
      </div>

      {nfrFile.nfrs.length === 0 ? (
        <div className="empty-state">
          <h3>No NFRs defined</h3>
          <p>Click "Add NFR" to create the first non-functional requirement for this domain.</p>
        </div>
      ) : (
        <div className="nfr-list">
          {nfrFile.nfrs.map(nfr => (
            <NFRCard
              key={nfr.code}
              nfr={nfr}
              services={services}
              explanation={explanations.explanations[nfr.code] || ''}
              onEdit={() => handleEdit(nfr)}
              onDelete={() => handleDelete(nfr)}
            />
          ))}
        </div>
      )}

      {(isCreating || editingNfr) && (
        <NFRForm
          nfr={editingNfr}
          defaultCode={isCreating ? getNextCode() : undefined}
          domain={domainName || ''}
          services={services}
          explanation={editingNfr ? (explanations.explanations[editingNfr.code] || '') : ''}
          onSave={handleSave}
          onCancel={handleCancel}
          saving={saving}
        />
      )}

      {deletingNfr && (
        <ConfirmDialog
          title="Delete NFR?"
          message={`Are you sure you want to delete ${deletingNfr.code}? This action cannot be undone.`}
          confirmLabel="Delete"
          onConfirm={confirmDelete}
          onCancel={() => setDeletingNfr(null)}
          loading={saving}
        />
      )}
    </div>
  );
}
