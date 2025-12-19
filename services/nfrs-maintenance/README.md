# NFR Maintenance UI

A React-based user interface for managing Non-Functional Requirements (NFRs) in the FtRS Directory of Services project.

## Features

- **Browse NFR Domains**: Navigate through all NFR domains (security, performance, governance, etc.)
- **View NFRs**: See all NFRs with their requirements, explanations, controls, and operations
- **Create NFRs**: Add new non-functional requirements with auto-generated codes
- **Edit NFRs**: Modify existing requirements, controls, and performance operations
- **Delete NFRs**: Remove requirements that are no longer needed
- **Manage Controls**: Add, edit, or remove control definitions with services, environments, and thresholds
- **Manage Operations**: For performance NFRs, define per-operation latency and throughput targets
- **Manage Services**: Add, edit, or remove service definitions used across NFRs
- **Edit Explanations**: Modify NFR explanations stored in the cross-references file alongside the NFR

## Prerequisites

- Node.js 18+
- npm or yarn

## Installation

```bash
cd services/nfrs-maintenance
npm install
```

## Running the Application

Start both the backend API server and the React development server:

```bash
npm run dev
```

This will start:
- **API Server**: http://localhost:3001 - Express server that reads/writes YAML files
- **UI**: http://localhost:5174 - React application (Vite dev server)

## Architecture

### Backend (`server/`)

The Express.js API server provides endpoints for:
- `GET /api/domains` - List all NFR domains
- `GET /api/services` - Get service configurations
- `PUT /api/services` - Update all services
- `POST /api/services/service` - Add a new service
- `PUT /api/services/service/:id` - Update a service
- `DELETE /api/services/service/:id` - Delete a service
- `GET /api/nfrs/:domain` - Get NFRs for a domain
- `PUT /api/nfrs/:domain` - Update all NFRs for a domain
- `POST /api/nfrs/:domain` - Add a new NFR
- `PUT /api/nfrs/:domain/:code` - Update a specific NFR
- `DELETE /api/nfrs/:domain/:code` - Delete an NFR
- `GET /api/explanations` - Get all NFR explanations from cross-references
- `PUT /api/explanations/:code` - Update/create an explanation for an NFR
- `DELETE /api/explanations/:code` - Delete an explanation

### Frontend (`src/`)

React application with:
- **Components**: Reusable UI components for NFR cards, forms, and modals
- **API Layer**: Fetch functions for communicating with the backend
- **Types**: TypeScript definitions matching the YAML schema

## Data Files

The application reads and writes to YAML files in:
```
requirements/nfrs/
├── services.yaml                        # Service and operation definitions
├── cross-references/
│   └── nfr-explanations.yaml            # NFR explanations (editable via UI)
├── security/nfrs.yaml                   # Security NFRs
├── performance/nfrs.yaml                # Performance NFRs
├── governance/nfrs.yaml                 # Governance NFRs
└── ...                                  # Other domain NFRs
```

## Development

### Running individual parts

```bash
# Just the API server
npm run dev:server

# Just the React UI
npm run dev:client
```

### Building for production

```bash
npm run build
```

## NFR Data Structure

NFRs follow this structure:

```yaml
code: SEC-001
requirement: "Requirement statement"
explanation: "Additional details"
stories:
  - FTRS-123
services:
  - crud-apis
controls:
  - control_id: some-control
    measure: "What is measured"
    threshold: "Acceptance criteria"
    environments: [dev, prod]
    services: [crud-apis]
    status: draft
operations:  # For performance domain
  - service: dos-search
    operation_id: dos-search
    p50_target_ms: 150
    p95_target_ms: 300
```

## Use Of AI

This app was built entirely using AI - GitHub CoPilot and the Claude Opus 4.5 model.

The prompts that were used:

### To create the application

```
What I'd like you to do next is to create a user interface, using React that allows a user to manage the NFR data. It will need to be able to leverage the exisrting nfrs.yaml files in the repo as the source data and should be able to update that data. This will have the result of changing the yaml files which the user can then commit. It should be able to create new NFRs, specify the service/s they apply to and any operation parameters needed. They should be able to modify the data as well as remove it. Let's start with that. Create the new UI in the services/nfrs-maintenance folder.
```

### Adding a services maintenance section

```
Please add a section into the nfrs-maintenance project to edit the services - their data is in requirements/nfrs/services.yaml
```

### Adding in explanation maintenance functionality

```
Now I'd like you to modify the infividual NFRs maintenance to bring in the explanation details. This data is in the requiremenets/nfrs/cross-reference.yaml file. I want to be able to edit an individual NFRs explanation at the same time as editing the NFR
```