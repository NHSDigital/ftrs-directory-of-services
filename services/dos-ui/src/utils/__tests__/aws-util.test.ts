import { describe, it, expect, vi } from 'vitest';
import { getawsSecret, getawsParameter } from '../aws-util.ts';

vi.mock('@aws-lambda-powertools/parameters/secrets', () => ({
  getSecret: vi.fn(async (name) => `mocked-secret-for-${name}`)
}));
vi.mock('@aws-lambda-powertools/parameters/ssm', () => ({
  getParameter: vi.fn(async (name, opts) => opts?.sdkOptions?.WithDecryption ? `decrypted-${name}` : `plain-${name}`)
}));

describe('getawsSecret', () => {
  it('returns the secret value', async () => {
    const secret = await getawsSecret('test-secret');
    expect(secret).toBe('mocked-secret-for-test-secret');
  });
});

describe('getawsParameter', () => {
  it('returns decrypted parameter value', async () => {
    const param = await getawsParameter('test-param');
    expect(param).toBe('decrypted-test-param');
  });
});
