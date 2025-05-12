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

mock_service_opening_times_df = pd.DataFrame(
    {
        "serviceid": [1, 1, 1, 1, 1, 1, 1, 2, 2],
        "availableStartTime": [
            "9:00:00",
            "9:00:00",
            "9:00:00",
            "9:00:00",
            "9:00:00",
            "10:30:00",
            "10:30:00",
            "9:00:00",
            "11:30:00",
        ],
        "availableEndTime": [
            "17:00:00",
            "17:00:00",
            "17:00:00",
            "17:00:00",
            "17:00:00",
            "16:00:00",
            "16:00:00",
            "17:00:00",
            "14:30:00",
        ],
        "dayOfWeek": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
            "Monday",
            "BankHoliday",
        ],
    }
)

mock_service_specified_opening_times_df = pd.DataFrame(
    {
        "serviceid": [1, 2, 1, 2],
        "date": ["2024-02-22", "2024-03-12", "2024-05-14", "2024-06-12"],
        "starttime": ["8:00:00", "8:15:00", "8:30:00", "9:00:00"],
        "endtime": ["13:00:00", "13:00:00", "13:00:00", "13:00:00"],
        "isclosed": [False, False, False, False],
    }
)


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

mock_gp_openingTimes_formatted_A = {
    "serviceid": 1,
    "availability": {
        "availableTime": [
            {
                "dayOfWeek": ["mon"],
                "availableStartTime": "9:00:00",
                "availableEndTime": "17:00:00",
            },
            {
                "dayOfWeek": ["tue"],
                "availableStartTime": "9:00:00",
                "availableEndTime": "17:00:00",
            },
            {
                "dayOfWeek": ["wed"],
                "availableStartTime": "9:00:00",
                "availableEndTime": "17:00:00",
            },
            {
                "dayOfWeek": ["thu"],
                "availableStartTime": "9:00:00",
                "availableEndTime": "17:00:00",
            },
            {
                "dayOfWeek": ["fri"],
                "availableStartTime": "9:00:00",
                "availableEndTime": "17:00:00",
            },
            {
                "dayOfWeek": ["sat"],
                "availableStartTime": "10:30:00",
                "availableEndTime": "16:00:00",
            },
            {
                "dayOfWeek": ["sun"],
                "availableStartTime": "10:30:00",
                "availableEndTime": "16:00:00",
            },
        ],
        "availableTimePublicHolidays": None,
        "availableTimeVariations": [
            {
                "description": "special",
                "during": {
                    "start": "2024-02-22T08:00:00",
                    "end": "2024-02-22T13:00:00",
                },
            },
            {
                "description": "special",
                "during": {
                    "start": "2024-05-14T08:30:00",
                    "end": "2024-05-14T13:00:00",
                },
            },
        ],
        "notAvailable": None,
    },
}

mock_gp_openingTimes_formatted_B = {
    "serviceid": 2,
    "availability": {
        "availableTime": [
            {
                "dayOfWeek": ["mon"],
                "availableStartTime": "9:00:00",
                "availableEndTime": "17:00:00",
            }
        ],
        "availableTimePublicHolidays": [
            {"availableStartTime": "11:30:00", "availableEndTime": "14:30:00"}
        ],
        "availableTimeVariations": [
            {
                "description": "special",
                "during": {
                    "start": "2024-03-12T08:15:00",
                    "end": "2024-03-12T13:00:00",
                },
            },
            {
                "description": "special",
                "during": {
                    "start": "2024-06-12T09:00:00",
                    "end": "2024-06-12T13:00:00",
                },
            },
        ],
        "notAvailable": None,
    },
}


mock_gp_openingTimes_formatted_df = pd.DataFrame(
    dict(
        {
            key: [
                mock_gp_openingTimes_formatted_A[key],
                mock_gp_openingTimes_formatted_B[key],
            ]
            for key in mock_gp_openingTimes_formatted_A.keys()
        },
    )
)

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
    "availability": None,
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
        "latitude": "0.000003",
        "longitude": "-1.000005",
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
    "openingTime": None,
}
