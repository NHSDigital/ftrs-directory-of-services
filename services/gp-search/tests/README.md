# Tests

This directory contains tests for the application.

## Unit Tests

The unit tests are located in the `unit` directory and are organized to mirror the structure of the application.

### Running the Tests

To run all the tests, use the following command from the root directory:

```bash
python -m unittest discover -s tests
```

To run a specific test file, use:

```bash
python -m unittest tests/unit/application/services/fhir_mapper/test_endpoint_mapper.py
```

### Test Structure

The tests are organized as follows:

- `tests/unit/services/fhir_mapper/test_endpoint_mapper.py`: Tests for the EndpointMapper class
- `tests/unit/services/fhir_mapper/test_fhir_mapper.py`: Tests for the FhirMapper class

### Recent Changes

The endpoint mapper has been updated to use `organization_record.value.endpoints` instead of `raw_endpoint.model_dump()`. This change ensures that the endpoint mapper correctly accesses the endpoints from the organization record.

The tests verify that:

1. The endpoint mapper correctly maps endpoints from an organization record
2. The FHIR mapper correctly passes the organization record to the endpoint mapper
