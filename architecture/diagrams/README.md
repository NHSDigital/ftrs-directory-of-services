# FtRS Architecture Diagram Generator

This directory contains tools to generate professional AWS-style deployment diagrams from the LikeC4 architecture model.

## Overview

While LikeC4 is excellent for maintaining a single architecture model with multiple views, its rendering isn't optimized for AWS deployment diagrams. This toolset:

1. **Parses** the LikeC4 `deployment.c4` file to extract nodes, relationships, and views
2. **Generates** AWS-style diagrams using the `diagrams` library with official AWS icons

## Requirements

```bash
# Python diagrams library
pip install diagrams

# Graphviz (required by diagrams)
brew install graphviz  # macOS
apt-get install graphviz  # Ubuntu/Debian
```

## Usage

```bash
# Generate all diagrams as PNG
python generate_deployment.py

# Generate specific diagram
python generate_deployment.py --diagram data-migration

# Generate as SVG or PDF
python generate_deployment.py --format svg

# Debug mode to see parsed architecture
python generate_deployment.py --debug
```

### Available Diagrams

- `overview` - High-level production deployment overview
- `data-migration` - Data migration pipeline (DMS, Lambdas, queues)
- `etl-ods` - ETL ODS pipeline (Extract-Transform-Load)
- `crud-apis` - CRUD APIs deployment (Organisation, HealthcareService, Location)
- `dos-search` - DoS Search API deployment

### Output

Diagrams are generated in the `output/` directory:

```text
output/
├── prod_overview.png
├── data_migration.png
├── etl_ods.png
├── crud_apis.png
└── dos_search.png
```

## How It Works

### Parser (`likec4_parser.py`)

The parser reads LikeC4 files and extracts:

- **Deployment Nodes**: environments, zones, VPCs, lambdas, DynamoDB, SQS, S3, DMS, RDS, etc.
- **Relationships**: connections between nodes with labels
- **Views**: deployment view definitions with includes

### Generator (`generate_deployment.py`)

The generator:

1. Parses the architecture using `likec4_parser.py`
2. Maps LikeC4 node types to `diagrams` library classes
3. Creates clustered diagrams with proper AWS icons
4. Renders relationships with labels

## Adding New Diagrams

To add a new diagram:

- Define the view in `deployment.c4` (optional - for documentation)
- Add a new generator method in `generate_deployment.py`:

```python
def generate_my_diagram(self, fmt: str = "png") -> None:
    # Find relevant nodes from parsed architecture
    my_nodes = [n for n in self.arch.nodes.values()
                if 'my_pattern' in n.id]

    with Diagram("My Diagram", ...):
        # Create clusters and nodes
        with Cluster("AWS"):
            lambda_fn = Lambda("My Lambda")
        # Define relationships
```

- Register it in the `generators` dict in `main()`
    1. Existing entry
    2. New entry

## Keeping Diagrams in Sync

Run the generator whenever the LikeC4 model changes:

```bash
# After updating deployment.c4
python generate_deployment.py --format png
```

Consider adding to CI/CD to auto-generate on merge.

## Troubleshooting

### "ExecutableNotFound: failed to execute dot"

Install Graphviz:

```bash
brew install graphviz  # macOS
```

### Parser not finding nodes

Run with `--debug` to see what's being parsed:

```bash
python generate_deployment.py --debug
```

Check that your LikeC4 syntax matches the expected patterns in `likec4_parser.py`.
