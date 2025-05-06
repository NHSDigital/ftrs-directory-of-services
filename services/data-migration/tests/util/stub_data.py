import pandas as pd

mock_gp_practices_A = {
    "name": "Practice A",
    "type": "GP",
    "odscode": "A12345",
    "uid": "uid123",
    "serviceid": 1,
    "publicphone": "0000 8888",
    "nonpublicphone": "1111 2222",
    "email": "test@nhs.net",
    "web": "www.fakeweb.co.uk",
    "address": "1 fake road",
    "town": "thingyplace",
    "postcode": "TP00 9ZZ",
    "latitude": "0.000003",
    "longitude": "-1.000005",
}

mock_gp_practices_df = pd.DataFrame({k: [v] for k, v in mock_gp_practices_A.items()})

mock_gp_practices_B = {
    "name": "Practice B",
    "type": "GP",
    "odscode": "B67890",
    "uid": "uid456",
    "serviceid": 2,
    "publicphone": "12345678901",
    "nonpublicphone": "09876543210#EXT0123",
    "email": None,
    "web": None,
    "address": "2 fake road",
    "town": "otherplace",
    "postcode": "TP990AB",
    "latitude": "-50.123456",
    "longitude": "64.123456",
}

mock_gp_practices_B_df = pd.DataFrame({k: [v] for k, v in mock_gp_practices_B.items()})

frames = [mock_gp_practices_df, mock_gp_practices_B_df]
mock_two_gp_practices_df = pd.concat(frames)

mock_gp_endpoints_A = {
    "id": 1,
    "endpointorder": 1,
    "transport": "email",
    "format": "PDF",
    "interaction": "interaction1",
    "businessscenario": "scenario1",
    "address": "address1",
    "comment": "comment1",
    "iscompressionenabled": "uncompressed",
    "serviceid": 1,
}

mock_gp_endpoints_df = pd.DataFrame({k: [v] for k, v in mock_gp_endpoints_A.items()})

mock_gp_endpoints_B = {
    "id": 2,
    "endpointorder": 1,
    "transport": "sms",
    "format": "XML",
    "interaction": "interaction2",
    "businessscenario": "scenario2",
    "address": "address2",
    "comment": "comment2",
    "iscompressionenabled": "compressed",
    "serviceid": 1,
}

mock_gp_endpoints_C = {
    "id": 3,
    "endpointorder": 2,
    "transport": "fax",
    "format": "TXT",
    "interaction": "interaction3",
    "businessscenario": "scenario3",
    "address": "address3",
    "comment": "comment3",
    "iscompressionenabled": "uncompressed",
    "serviceid": 2,
}

mock_gp_endpoints_formatted_A = {
    "id": 1,
    "endpointorder": 1,
    "transport": "email",
    "format": "PDF",
    "interaction": "interaction1",
    "businessscenario": "scenario1",
    "address": "address1",
    "comment": "comment1",
    "iscompressionenabled": "uncompressed",
}

mock_gp_endpoints_formatted_B = {
    "id": 2,
    "endpointorder": 1,
    "transport": "sms",
    "format": "XML",
    "interaction": "interaction2",
    "businessscenario": "scenario2",
    "address": "address2",
    "comment": "comment2",
    "iscompressionenabled": "compressed",
}

mock_gp_endpoints_formatted_C = {
    "id": 3,
    "endpointorder": 2,
    "transport": "fax",
    "format": "TXT",
    "interaction": "interaction3",
    "businessscenario": "scenario3",
    "address": "address3",
    "comment": "comment3",
    "iscompressionenabled": "uncompressed",
}

mock_gp_endpoint_json_dump_B = {
    "id": "123e4567-e89b-12d3-a456-42661417400a",
    "identifier_oldDoS_id": 2,
    "status": "active",
    "connectionType": "sms",
    "name": None,
    "description": "scenario2",
    "payloadType": "interaction2",
    "address": "address2",
    "managedByOrganisation": "123e4567-e89b-12d3-a456-42661417400a",
    "service": None,
    "order": 1,
    "isCompressionEnabled": True,
    "format": "XML",
    "createdBy": "ROBOT",
    "createdDateTime": "2025-03-27T12:00:00Z",
    "modifiedBy": "ROBOT",
    "modifiedDateTime": "2025-03-27T12:00:00Z",
}

mock_gp_endpoint_json_dump_C = {
    "id": "123e4567-e89b-12d3-a456-42661417400a",
    "identifier_oldDoS_id": 3,
    "status": "active",
    "connectionType": "fax",
    "name": None,
    "description": "scenario3",
    "payloadType": "interaction3",
    "address": "address3",
    "managedByOrganisation": "123e4567-e89b-12d3-a456-42661417400a",
    "service": None,
    "order": 2,
    "isCompressionEnabled": False,
    "format": "TXT",
    "createdBy": "ROBOT",
    "createdDateTime": "2025-03-27T12:00:00Z",
    "modifiedBy": "ROBOT",
    "modifiedDateTime": "2025-03-27T12:00:00Z",
}


mock_services_size_df = pd.DataFrame({"count": [100]})
mock_services_columns_df = pd.DataFrame({"count": [37]})
mock_service_endpoint_columns_df = pd.DataFrame({"count": [5]})


extracted_GP_Practice = {
    "odscode": "A123",
    "name": "Test Org",
    "type": "GP Practice",
    "uid": "00000000-0000-0000-0000-00000000000a",
    "serviceid": 192040,
    "publicphone": "0000 8888",
    "nonpublicphone": "12345678901",
    "email": "test@nhs.net",
    "web": "www.test.co.uk",
    "address": "10 made up road",
    "town": "thingyplace",
    "postcode": "TP00 9ZZ",
    "latitude": "0.000003",
    "longitude": "-1.000005",
    "endpoints": [[mock_gp_endpoints_formatted_A]],
}

transformed_GP_Practice_Org = {
    "id": "123e4567-e89b-12d3-a456-42661417400a",
    "identifier_ODS_ODSCode": "A123",
    "active": True,
    "name": "Test Org",
    "telecom": None,
    "type": "GP Practice",
    "createdBy": "ROBOT",
    "createdDateTime": "2025-03-27T12:00:00Z",
    "modifiedBy": "ROBOT",
    "modifiedDateTime": "2025-03-27T12:00:00Z",
    "endpoints": [
        {
            "id": "123e4567-e89b-12d3-a456-42661417400a",
            "identifier_oldDoS_id": 1,
            "status": "active",
            "connectionType": "email",
            "name": None,
            "description": "scenario1",
            "format": "PDF",
            "payloadType": "interaction1",
            "address": "address1",
            "managedByOrganisation": "123e4567-e89b-12d3-a456-42661417400a",
            "service": None,
            "order": 1,
            "isCompressionEnabled": False,
            "createdBy": "ROBOT",
            "createdDateTime": "2025-03-27T12:00:00Z",
            "modifiedBy": "ROBOT",
            "modifiedDateTime": "2025-03-27T12:00:00Z",
        }
    ],
}

transformed_GP_Practice_Loc = {
    "id": "123e4567-e89b-12d3-a456-42661417400a",
    "active": True,
    "managingOrganisation": "123e4567-e89b-12d3-a456-42661417400a",
    "name": None,
    "address": {
        "street": "10 made up road",
        "town": "thingyplace",
        "postcode": "TP00 9ZZ",
    },
    "positionGCS": {
        "latitude": float("0.000003"),
        "longitude": float("-1.000005"),
    },
    "positionReferenceNumber_UPRN": None,
    "positionReferenceNumber_UBRN": None,
    "partOf": None,
    "primaryAddress": True,
    "createdBy": "ROBOT",
    "createdDateTime": "2025-03-27T12:00:00Z",
    "modifiedBy": "ROBOT",
    "modifiedDateTime": "2025-03-27T12:00:00Z",
}


transformed_GP_Practice_HS = {
    "id": "123e4567-e89b-12d3-a456-42661417400a",
    "createdBy": "ROBOT",
    "createdDateTime": "2025-03-27T12:00:00Z",
    "modifiedBy": "ROBOT",
    "modifiedDateTime": "2025-03-27T12:00:00Z",
    "identifier_oldDoS_uid": "00000000-0000-0000-0000-00000000000a",
    "active": True,
    "category": "unknown",
    "providedBy": "123e4567-e89b-12d3-a456-42661417400a",
    "location": "123e4567-e89b-12d3-a456-42661417400a",
    "name": "Test Org",
    "telecom": {
        "phone_public": "0000 8888",
        "phone_private": "12345678901",
        "email": "test@nhs.net",
        "web": "www.test.co.uk",
    },
    "type": "GP Practice",
}
