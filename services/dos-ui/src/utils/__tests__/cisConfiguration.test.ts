import { describe, it, expect, vi } from 'vitest';
import { validateConfig, getAuthConfig } from '../cisConfiguration.ts';

vi.mock('../aws-util.ts', () => ({
  getawsParameter: vi.fn(async () => JSON.stringify({
    issuerUrl: 'http://issuer',
    clientId: 'client-id',
    redirectUri: 'http://localhost/callback',
    scope: 'openid',
  }))
}));

describe('validateConfig', () => {
  it('throws error if issuerUrl or clientId missing', () => {
    expect(() => validateConfig({ clientId: '', issuerUrl: '', redirectUri: '', scope: '' })).toThrow();
  });
  it('does not throw if config is valid', () => {
    expect(() => validateConfig({issuerUrl: 'url', clientId: 'id', redirectUri: '', scope: ''})).not.toThrow();
  });
});

describe('getAuthConfig', () => {
  it('returns parsed config and calls validateConfig', async () => {
    const config = await getAuthConfig();
    expect(config.issuerUrl).toBe('http://issuer');
    expect(config.clientId).toBe('client-id');
  });
});



