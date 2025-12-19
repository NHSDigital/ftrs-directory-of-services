import express from 'express';
import cors from 'cors';
import yaml from 'js-yaml';
import { glob } from 'glob';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const NFR_BASE_PATH = path.resolve(__dirname, '../../../requirements/nfrs');
const NFR_META_PATH = path.join(NFR_BASE_PATH, 'cross-references', 'nfr-meta.yaml');

const app = express();
app.use(cors());
app.use(express.json());

// Get list of all NFR domains
app.get('/api/domains', async (_req, res) => {
  try {
    const files = await glob('*/nfrs.yaml', { cwd: NFR_BASE_PATH });
    const domains = files.map(file => {
      const domain = path.dirname(file);
      return {
        name: domain,
        path: file,
        prefix: domain.toUpperCase().substring(0, 3).replace(/[^A-Z]/g, '') + '-'
      };
    }).sort((a, b) => a.name.localeCompare(b.name));
    res.json(domains);
  } catch (error) {
    console.error('Error listing domains:', error);
    res.status(500).json({ error: 'Failed to list domains' });
  }
});

// Get services configuration
app.get('/api/services', async (_req, res) => {
  try {
    const servicesPath = path.join(NFR_BASE_PATH, 'services.yaml');
    const content = await fs.readFile(servicesPath, 'utf-8');
    const data = yaml.load(content);
    res.json(data);
  } catch (error) {
    console.error('Error loading services:', error);
    res.status(500).json({ error: 'Failed to load services' });
  }
});

// Update all services
app.put('/api/services', async (req, res) => {
  try {
    const { services } = req.body;
    const servicesPath = path.join(NFR_BASE_PATH, 'services.yaml');
    const content = await fs.readFile(servicesPath, 'utf-8');
    const data = yaml.load(content) as { services: Record<string, string>; operations: Record<string, Record<string, string>> };

    data.services = services;

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: '"',
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(servicesPath, yamlContent, 'utf-8');
    res.json({ success: true });
  } catch (error) {
    console.error('Error updating services:', error);
    res.status(500).json({ error: 'Failed to update services' });
  }
});

// Add a new service
app.post('/api/services/service', async (req, res) => {
  try {
    const { id, displayName } = req.body;
    const servicesPath = path.join(NFR_BASE_PATH, 'services.yaml');
    const content = await fs.readFile(servicesPath, 'utf-8');
    const data = yaml.load(content) as { services: Record<string, string>; operations: Record<string, Record<string, string>> };

    if (data.services[id]) {
      return res.status(400).json({ error: 'Service already exists' });
    }

    data.services[id] = displayName;

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: '"',
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(servicesPath, yamlContent, 'utf-8');
    res.json({ success: true });
  } catch (error) {
    console.error('Error adding service:', error);
    res.status(500).json({ error: 'Failed to add service' });
  }
});

// Update a service
app.put('/api/services/service/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { displayName } = req.body;
    const servicesPath = path.join(NFR_BASE_PATH, 'services.yaml');
    const content = await fs.readFile(servicesPath, 'utf-8');
    const data = yaml.load(content) as { services: Record<string, string>; operations: Record<string, Record<string, string>> };

    if (!data.services[id]) {
      return res.status(404).json({ error: 'Service not found' });
    }

    data.services[id] = displayName;

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: '"',
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(servicesPath, yamlContent, 'utf-8');
    res.json({ success: true });
  } catch (error) {
    console.error('Error updating service:', error);
    res.status(500).json({ error: 'Failed to update service' });
  }
});

// Delete a service
app.delete('/api/services/service/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const servicesPath = path.join(NFR_BASE_PATH, 'services.yaml');
    const content = await fs.readFile(servicesPath, 'utf-8');
    const data = yaml.load(content) as { services: Record<string, string>; operations: Record<string, Record<string, string>> };

    if (!data.services[id]) {
      return res.status(404).json({ error: 'Service not found' });
    }

    delete data.services[id];
    delete data.operations[id];

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: '"',
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(servicesPath, yamlContent, 'utf-8');
    res.json({ success: true });
  } catch (error) {
    console.error('Error deleting service:', error);
    res.status(500).json({ error: 'Failed to delete service' });
  }
});

// Get NFR teams and releases metadata
app.get('/api/catalog', async (_req, res) => {
  try {
    const content = await fs.readFile(NFR_META_PATH, 'utf-8');
    const data = yaml.load(content);
    res.json(data);
  } catch (error) {
    console.error('Error loading NFR catalog:', error);
    res.status(500).json({ error: 'Failed to load NFR catalog' });
  }
});

// Update NFR teams and releases metadata
app.put('/api/catalog', async (req, res) => {
  try {
    const { teams, releases, version } = req.body;

    const meta = {
      version: version ?? 1.0,
      generated: new Date().toISOString().replace('T', ' ').substring(0, 19) + '+00:00',
      teams: teams ?? [],
      releases: releases ?? []
    };

    const yamlContent = yaml.dump(meta, {
      lineWidth: -1,
      noRefs: true,
      quotingType: '"',
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(NFR_META_PATH, yamlContent, 'utf-8');
    res.json({ success: true });
  } catch (error) {
    console.error('Error updating NFR catalog:', error);
    res.status(500).json({ error: 'Failed to update NFR catalog' });
  }
});

// Get NFRs for a specific domain
app.get('/api/nfrs/:domain', async (req, res) => {
  try {
    const { domain } = req.params;
    const filePath = path.join(NFR_BASE_PATH, domain, 'nfrs.yaml');
    const content = await fs.readFile(filePath, 'utf-8');
    const data = yaml.load(content);
    res.json(data);
  } catch (error) {
    console.error(`Error loading NFRs for domain ${req.params.domain}:`, error);
    res.status(500).json({ error: 'Failed to load NFRs' });
  }
});

// Save NFRs for a specific domain
app.put('/api/nfrs/:domain', async (req, res) => {
  try {
    const { domain } = req.params;
    const data = req.body;
    const filePath = path.join(NFR_BASE_PATH, domain, 'nfrs.yaml');

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: '"',
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(filePath, yamlContent, 'utf-8');
    res.json({ success: true });
  } catch (error) {
    console.error(`Error saving NFRs for domain ${req.params.domain}:`, error);
    res.status(500).json({ error: 'Failed to save NFRs' });
  }
});

// Add a new NFR to a domain
app.post('/api/nfrs/:domain', async (req, res) => {
  try {
    const { domain } = req.params;
    const newNfr = req.body;
    const filePath = path.join(NFR_BASE_PATH, domain, 'nfrs.yaml');

    const content = await fs.readFile(filePath, 'utf-8');
    const data = yaml.load(content) as { nfrs: any[] };

    data.nfrs.push(newNfr);

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: '"',
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(filePath, yamlContent, 'utf-8');
    res.json({ success: true, nfr: newNfr });
  } catch (error) {
    console.error(`Error adding NFR to domain ${req.params.domain}:`, error);
    res.status(500).json({ error: 'Failed to add NFR' });
  }
});

// Delete an NFR from a domain
app.delete('/api/nfrs/:domain/:code', async (req, res) => {
  try {
    const { domain, code } = req.params;
    const filePath = path.join(NFR_BASE_PATH, domain, 'nfrs.yaml');

    const content = await fs.readFile(filePath, 'utf-8');
    const data = yaml.load(content) as { nfrs: any[] };

    data.nfrs = data.nfrs.filter(nfr => nfr.code !== code);

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: '"',
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(filePath, yamlContent, 'utf-8');
    res.json({ success: true });
  } catch (error) {
    console.error(`Error deleting NFR ${req.params.code} from domain ${req.params.domain}:`, error);
    res.status(500).json({ error: 'Failed to delete NFR' });
  }
});

// Update a specific NFR in a domain
app.put('/api/nfrs/:domain/:code', async (req, res) => {
  try {
    const { domain, code } = req.params;
    const updatedNfr = req.body;
    const filePath = path.join(NFR_BASE_PATH, domain, 'nfrs.yaml');

    const content = await fs.readFile(filePath, 'utf-8');
    const data = yaml.load(content) as { nfrs: any[] };

    const index = data.nfrs.findIndex(nfr => nfr.code === code);
    if (index === -1) {
      return res.status(404).json({ error: 'NFR not found' });
    }

    data.nfrs[index] = updatedNfr;

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: '"',
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(filePath, yamlContent, 'utf-8');
    res.json({ success: true, nfr: updatedNfr });
  } catch (error) {
    console.error(`Error updating NFR ${req.params.code} in domain ${req.params.domain}:`, error);
    res.status(500).json({ error: 'Failed to update NFR' });
  }
});

// Get all explanations
app.get('/api/explanations', async (_req, res) => {
  try {
    const explanationsPath = path.join(NFR_BASE_PATH, 'cross-references', 'nfr-explanations.yaml');
    const content = await fs.readFile(explanationsPath, 'utf-8');
    const data = yaml.load(content);
    res.json(data);
  } catch (error) {
    console.error('Error loading explanations:', error);
    res.status(500).json({ error: 'Failed to load explanations' });
  }
});

// Update or create an explanation for a specific NFR code
app.put('/api/explanations/:code', async (req, res) => {
  try {
    const { code } = req.params;
    const { explanation } = req.body;
    const explanationsPath = path.join(NFR_BASE_PATH, 'cross-references', 'nfr-explanations.yaml');
    const content = await fs.readFile(explanationsPath, 'utf-8');
    const data = yaml.load(content) as { version: string | number; generated?: string; explanations: Record<string, string> };

    if (explanation && explanation.trim()) {
      data.explanations[code] = explanation;
    } else {
      delete data.explanations[code];
    }

    // Update generated timestamp
    data.generated = new Date().toISOString().replace('T', ' ').substring(0, 19) + '+00:00';

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: "'",
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(explanationsPath, yamlContent, 'utf-8');
    res.json({ success: true });
  } catch (error) {
    console.error(`Error updating explanation for ${req.params.code}:`, error);
    res.status(500).json({ error: 'Failed to update explanation' });
  }
});

// Delete an explanation for a specific NFR code
app.delete('/api/explanations/:code', async (req, res) => {
  try {
    const { code } = req.params;
    const explanationsPath = path.join(NFR_BASE_PATH, 'cross-references', 'nfr-explanations.yaml');
    const content = await fs.readFile(explanationsPath, 'utf-8');
    const data = yaml.load(content) as { version: string | number; generated?: string; explanations: Record<string, string> };

    delete data.explanations[code];

    // Update generated timestamp
    data.generated = new Date().toISOString().replace('T', ' ').substring(0, 19) + '+00:00';

    const yamlContent = yaml.dump(data, {
      lineWidth: -1,
      noRefs: true,
      quotingType: "'",
      forceQuotes: false,
      indent: 2
    });

    await fs.writeFile(explanationsPath, yamlContent, 'utf-8');
    res.json({ success: true });
  } catch (error) {
    console.error(`Error deleting explanation for ${req.params.code}:`, error);
    res.status(500).json({ error: 'Failed to delete explanation' });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`NFR API server running on http://localhost:${PORT}`);
  console.log(`NFR base path: ${NFR_BASE_PATH}`);
});
