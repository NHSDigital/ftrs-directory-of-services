resource "aws_apigatewayv2_route_response" "sandbox_organization" {
  count              = var.environment == "sandbox" ? 1 : 0
  api_id             = module.api_gateway.api_id
  route_id           = module.api_gateway.route_ids["GET /Organization"]
  route_response_key = "$default"
}

resource "aws_apigatewayv2_integration_response" "sandbox_organization" {
  count                    = var.environment == "sandbox" ? 1 : 0
  api_id                   = module.api_gateway.api_id
  integration_id           = module.api_gateway.integration_ids["GET /Organization"]
  integration_response_key = "$default"

  response_templates = {
    "application/json" = <<EOT
#set($code = $input.params('querystring').get('identifier'))
#set($odsCode = "")
#if($code.startsWith("odsOrganisationCode|"))
  #set($odsCode = $code.substring($code.indexOf("|") + 1))
#end

#if($odsCode == "C88006")
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 1,
  "entry": [
    {
      "resource": {
        "resourceType": "Organization",
        "id": "c6016de0-7ce0-5320-9496-1d13046ad46d",
        "meta": {
          "profile": [
            "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
          ]
        },
        "identifier": [
          {
            "use": "official",
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "C88006"
          }
        ],
        "active": true,
        "type": [
          {
            "coding": [
              {
                "system": "TO-DO",
                "code": "GP Practice",
                "display": "GP Practice"
              }
            ],
            "text": "GP Practice"
          }
        ],
        "name": "Dr Margaret Mckenna And Partners Norfolk Park",
        "telecom": []
      }
    }
  ]
}
#else
{
  "resourceType": "Bundle",
  "type": "searchset",
  "total": 0,
  "entry": []
}
#end
EOT
  }
}
