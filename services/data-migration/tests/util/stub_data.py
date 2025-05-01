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
}

mock_gp_practices_B_df = pd.DataFrame({k: [v] for k, v in mock_gp_practices_B.items()})

frames = [mock_gp_practices_df, mock_gp_practices_B_df]
mock_two_gp_practices_df = pd.concat(frames)

mock_gp_endpoints = {
    "id": 1,
    "endpointorder": 1,
    "transport": "email",
    "format": "PDF",
    "interaction": "interaction1",
    "businessscenario": "scenario1",
    "address": "address1",
    "comment": "comment1",
    "iscompressionenabled": "false",
    "serviceid": 1,
}

mock_gp_endpoints_df = pd.DataFrame({k: [v] for k, v in mock_gp_endpoints.items()})

mock_gp_endpoints_B = {
    "id": 2,
    "endpointorder": 1,
    "transport": "sms",
    "format": "XML",
    "interaction": "interaction2",
    "businessscenario": "scenario2",
    "address": "address2",
    "comment": "comment2",
    "iscompressionenabled": "true",
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
    "iscompressionenabled": "false",
    "serviceid": 2,
}

mock_gp_endpoints_formatted = {
    "id": 1,
    "endpointorder": 1,
    "transport": "email",
    "format": "PDF",
    "interaction": "interaction1",
    "businessscenario": "scenario1",
    "address": "address1",
    "comment": "comment1",
    "iscompressionenabled": "false",
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
    "iscompressionenabled": "true",
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
    "iscompressionenabled": "false",
}


mock_services_size_df = pd.DataFrame({"count": [100]})
mock_services_columns_df = pd.DataFrame({"count": [37]})
mock_service_endpoint_columns_df = pd.DataFrame({"count": [5]})
