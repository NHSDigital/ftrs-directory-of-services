# OpenAPI Specifications (OAS)

This directory contains OpenAPI specifications for the FTRS Directory of Services APIs.

## Prerequisites

For publishing specifications, you need:

- `yq` - YAML processor
- `proxygen-cli` - tool for interacting with the NHS API platform

## Manual Publishing

Publishing a spec is currently a manual process that should be automated in the future.

Prepare a spec for publishing by filtering servers.

We only want to include the servers that connecting parties can use, avoiding internal ones.

For dos-search:

```shell
yq eval '.servers = [
  .servers[] | select(
    .description == "Sandbox" or
    .description == "Integration" or
    .description == "Reference" or
    .description == "Production"
  )
]' dos-search.yaml > dos-search-filtered.yaml
```

Then publish the spec via Proxygen:

To UAT:

```shell
proxygen spec publish dos-search-filtered.yaml --uat
```

To Production:

```shell
proxygen spec publish dos-search-filtered.yaml
```
