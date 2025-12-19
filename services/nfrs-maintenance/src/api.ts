import { Domain, NFRFile, ServicesConfig, NFR, ExplanationsFile } from './types';

const API_BASE = '/api';

export async function fetchDomains(): Promise<Domain[]> {
  const response = await fetch(`${API_BASE}/domains`);
  if (!response.ok) throw new Error('Failed to fetch domains');
  return response.json();
}

export async function fetchServices(): Promise<ServicesConfig> {
  const response = await fetch(`${API_BASE}/services`);
  if (!response.ok) throw new Error('Failed to fetch services');
  return response.json();
}

export async function fetchNFRs(domain: string): Promise<NFRFile> {
  const response = await fetch(`${API_BASE}/nfrs/${domain}`);
  if (!response.ok) throw new Error(`Failed to fetch NFRs for ${domain}`);
  return response.json();
}

export async function saveNFRs(domain: string, data: NFRFile): Promise<void> {
  const response = await fetch(`${API_BASE}/nfrs/${domain}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error(`Failed to save NFRs for ${domain}`);
}

export async function addNFR(domain: string, nfr: NFR): Promise<NFR> {
  const response = await fetch(`${API_BASE}/nfrs/${domain}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(nfr)
  });
  if (!response.ok) throw new Error(`Failed to add NFR to ${domain}`);
  const result = await response.json();
  return result.nfr;
}

export async function updateNFR(domain: string, code: string, nfr: NFR): Promise<NFR> {
  const response = await fetch(`${API_BASE}/nfrs/${domain}/${code}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(nfr)
  });
  if (!response.ok) throw new Error(`Failed to update NFR ${code}`);
  const result = await response.json();
  return result.nfr;
}

export async function deleteNFR(domain: string, code: string): Promise<void> {
  const response = await fetch(`${API_BASE}/nfrs/${domain}/${code}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error(`Failed to delete NFR ${code}`);
}

// Services API
export async function updateServices(services: { [key: string]: string }): Promise<void> {
  const response = await fetch(`${API_BASE}/services`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ services })
  });
  if (!response.ok) throw new Error('Failed to update services');
}

export async function addService(id: string, displayName: string): Promise<void> {
  const response = await fetch(`${API_BASE}/services/service`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, displayName })
  });
  if (!response.ok) throw new Error('Failed to add service');
}

export async function updateService(id: string, displayName: string): Promise<void> {
  const response = await fetch(`${API_BASE}/services/service/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ displayName })
  });
  if (!response.ok) throw new Error('Failed to update service');
}

export async function deleteService(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/services/service/${id}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error('Failed to delete service');
}

// Explanations API
export async function fetchExplanations(): Promise<ExplanationsFile> {
  const response = await fetch(`${API_BASE}/explanations`);
  if (!response.ok) throw new Error('Failed to fetch explanations');
  return response.json();
}

export async function updateExplanation(code: string, explanation: string): Promise<void> {
  const response = await fetch(`${API_BASE}/explanations/${code}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ explanation })
  });
  if (!response.ok) throw new Error('Failed to update explanation');
}

export async function deleteExplanation(code: string): Promise<void> {
  const response = await fetch(`${API_BASE}/explanations/${code}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error('Failed to delete explanation');
}
