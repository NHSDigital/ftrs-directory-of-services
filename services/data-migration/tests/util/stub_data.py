import pandas as pd

mock_gp_practices_df = pd.DataFrame(
    {
        "name": ["Practice A"],
        "type": ["GP"],
        "odscode": ["A12345"],
        "uid": ["uid123"],
        "serviceid": [1],
    }
)


mock_gp_endpoints_df = pd.DataFrame(
    {
        "id": [1],
        "endpointorder": [1],
        "transport": ["email"],
        "format": ["PDF"],
        "interaction": ["interaction1"],
        "businessscenario": ["scenario1"],
        "address": ["address1"],
        "comment": ["comment1"],
        "iscompressionenabled": ["false"],
        "serviceid": [1],
    }
)

mock_services_size_df = pd.DataFrame({"count": [100]})
mock_services_columns_df = pd.DataFrame({"count": [37]})
mock_service_endpoint_columns_df = pd.DataFrame({"count": [5]})

mock_gp_endpoints_formatted_df = pd.DataFrame(
    {
        "serviceid": [1],
        "endpoints": [
            [
                {
                    "endpointid": 1,
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
            ]
        ],
    }
)


mock_gp_practice_extract_df = pd.DataFrame(
    {
        "name": ["Practice A"],
        "type": ["GP"],
        "odscode": ["A12345"],
        "uid": ["uid123"],
        "endpoints": [
            [
                {
                    "endpointid": 1,
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
            ]
        ],
    }
)
