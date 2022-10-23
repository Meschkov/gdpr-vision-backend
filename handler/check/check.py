import google.cloud.dlp
import csv
import requests

dlp = google.cloud.dlp_v2.DlpServiceClient()

project = "one-record"

INFO_TYPES = [
    "PERSON_NAME",
    "AGE",
    "DATE_OF_BIRTH",
    "ETHNIC_GROUP",
    "GENDER",

    "EMAIL_ADDRESS",
    "PHONE_NUMBER",

    "CREDIT_CARD_NUMBER",
    "IBAN_CODE",
    "PASSPORT",

    "VEHICLE_IDENTIFICATION_NUMBER",

    "US_SOCIAL_SECURITY_NUMBER"
]

blacklist = ["@id", "@type", "https://onerecord.iata.org/ExternalReference#documentLink", "https://onerecord.iata.org/Product#hsType",
             "https://onerecord.iata.org/Product#hsCode", "https://onerecord.iata.org/Product#hsCommodityDescription"]

hs_codes = {}
with open("handler/check/harmonized-system.csv", 'r') as file:
    csvreader = csv.reader(file)
    for row in csvreader:
        hs_codes[row[1]] = row[2]


def iterate_logistic_object(obj, key, identifier, result):
    if key in blacklist:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            iterate_logistic_object(v, k, obj["@id"], result)
        return
    elif isinstance(obj, list):
        for i in obj:
            iterate_logistic_object(i, key, identifier, result)
        return
    else:
        result.append([identifier, key, str(obj)])


def check_logistic_object(request_body: dict) -> tuple[dict, int]:
    lo = requests.get(request_body["uri"]).json()

    pieces = lo.get("https://onerecord.iata.org/Shipment#containedPieces", [])

    hs_commodity_descriptions = []
    for piece in pieces:
        for product in piece.get("https://onerecord.iata.org/Piece#product"):
            hs_commodity_descriptions.append(get_hs_commodity_description(product))

    table_rows = []
    iterate_logistic_object(lo, None, lo.get("@id"), table_rows)

    piis = pii_detection(table_rows)

    response = {
        "hsCommodityDescriptions": hs_commodity_descriptions,
        "piis": piis
    }

    return response, 200


def get_hs_commodity_description(obj):
    if obj.get("https://onerecord.iata.org/Product#hsCode"):
        return {
            "identifier": obj.get("@id"),
            "hsCode": obj.get("https://onerecord.iata.org/Product#hsCode"),
            "hsCommodityDescription": hs_codes.get(obj.get("https://onerecord.iata.org/Product#hsCode"), None)
        }
    else:
        return {
            "identifier": obj.get("@id"),
            "hsCode": None,
            "hsCommodityDescription": None
        }


def pii_detection(rows):
    inspect_config = {
        "info_types": [{"name": info_type} for info_type in INFO_TYPES],
        "include_quote": True,
    }

    piis = []

    for row in rows:
        item = {"value": row[2]}
        parent = f"projects/one-record"

        response = dlp.inspect_content(
            request={"parent": parent, "inspect_config": inspect_config, "item": item}
        )

        for finding in response.result.findings:
            piis.append({
                "id": row[0],
                "attribute": row[1],
                "quote": finding.quote,
                "info_type": finding.info_type.name,
                "likelihood": finding.likelihood,
                "start": finding.location.byte_range.start,  # codepoint_range
                "end": finding.location.byte_range.end
            })

    return piis
