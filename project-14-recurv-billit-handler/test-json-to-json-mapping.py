# ****************************************************************
# params: no params
# created by: Marc De Krock
# date: 20250714
# ****************************************************************

from flask import jsonify
import json
from data_processing_utils import clean_json_data
import requests
from json_lib import input_json, input_json_recurv1, input_json_recurv2
from webhook_utils_2 import post_data_to_appsheet

input_json_recurv1 = input_json_recurv2
# Constants for Billit API
billit_sandbox_orders_url = "https://api.sandbox.billit.be/v1/orders"
billit_sandbox_send_invoice_url = (
    "https://api.sandbox.billit.be/v1/orders/commands/send"
)

billit_sandbox_apikey = (
    "5f93562b-6b47-48c2-9a61-bd384f4602ed"  # Replace with your actual API key
)


# Function to post an order to Billit
# This function takes a payload, which is a JSON object,
# and sends it to the Billit API to create an order.
# It returns the response from Billit.
# please note that this only posts the order to Billit, next the order needs to be sent
def post_order_to_billit(payload):
    # This function would contain the logic to send the payload to Billit.
    # For now, we will just print the payload.
    print("Sending order to Billit:", json.dumps(payload, indent=2))
    url = billit_sandbox_orders_url  # Replace with the actual Billit API endpoint
    headers = {
        "Content-Type": "text/json",
        "Accept": "application/json",
        "apiKey": billit_sandbox_apikey,
    }  # Replace with your actual API key

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Order posted successfully:", response.json())
    else:
        print("Failed to post order:", response.status_code, response.text)
    return int(response.json())


def send_order(order_id, transport_type):
    """
    Sends an order to Billit using the provided order ID and method of transport.

    :param order_id: str - The ID of the order to send
    :param method_of_transport: str - The method of transport for the order
    :return: dict - The payload containing the order details
    :return: Response from the Billit API
    """
    print(f"Sending order {order_id} with transport type {transport_type} to Billit")
    if transport_type not in [
        "SMTP",
        "API",
        "Peppol",
        "SDI",
        "KSeF",
        "OSA",
        "ANAF",
        "SAT",
    ]:
        return jsonify({"error": "Invalid transport type"}), 400
    url = billit_sandbox_send_invoice_url
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "apiKey": billit_sandbox_apikey,
    }

    payload = {
        "Transporttype": transport_type,
        "OrderIDs": [order_id],
    }
    print("Payload for sending order:", json.dumps(payload, indent=2))
    response = requests.post(url, headers=headers, json=payload)
    response_status = response.status_code
    print("Response status code:", response_status)

    if response_status == 200:
        print("Order sent successfully:", response_status)
        return response_status
    else:
        print("Failed to send order:", response_status)
        return jsonify({"error": "Failed to send order"}), response_status


# Function to merge three nested objects into a single JSON object
# This function takes a JSON body and three nested objects (customer, supplier, order_lines),
# and merges them into a single JSON object.
def merge_objects(json_body, customer, supplier, order_lines):
    # Start with a copy of object 1, but remove any existing conflicting keys
    result = {
        key: value
        for key, value in json_body.items()
        if key not in ("customer", "supplier", "order_lines")
    }

    # Add/override with the three nested objects
    result["Customer"] = customer
    result["Supplier"] = supplier
    result["OrderLines"] = order_lines

    return result


# Function to map JSON keys based on provided rules
# This function takes an input JSON and a set of mapping rules,
# and returns a new JSON with keys transformed according to the rules.
def map_json(input_data, mapping_rules):
    """
    Maps input JSON keys to a new JSON format based on mapping rules.

    :param input_data: dict - incoming JSON
    :param mapping_rules: dict - defines how input keys map to output keys
                               - values can be strings (direct mapping)
                               - or (output_key, transform_fn) tuples
    :return: dict - transformed output JSON
    """
    output_data = {}
    for input_key, rule in mapping_rules.items():
        if input_key in input_data:
            value = input_data[input_key]
            if isinstance(rule, tuple):
                output_key, transform_fn = rule
                output_data[output_key] = transform_fn(value)
            else:
                output_data[rule] = value
        else:
            print(f"Warning: input key '{input_key}' not found in input data.")
    return output_data


# Function to split supplier address into components
# This function takes a supplier address string and splits it into street, postal code, city,
# and country components. It returns a dictionary with these components.
# If the address format is unexpected, it returns empty strings and an error message.
def split_supplier_address_for_template(address):
    try:
        parts = [part.strip() for part in address.split(",")]

        if len(parts) == 3:
            street_and_nr, postal_city, country = parts
        elif len(parts) == 2:
            street_and_nr, postal_city = parts
            country = ""  # fallback if country is missing
        else:
            raise ValueError("Unexpected address format")

        postal_parts = postal_city.strip().split(" ", 1)
        postalcode = postal_parts[0]
        city = postal_parts[1] if len(postal_parts) > 1 else ""

        return {
            "P_supplier_address_streetname": street_and_nr,
            "P_supplier_address_postalzone": postalcode,
            "P_supplier_address_city": city,
            "P_supplier_address_country": country,
        }

    except Exception as e:
        return {
            "P_supplier_address_streetname": "",
            "P_supplier_address_postalzone": "",
            "P_supplier_address_city": "",
            "P_supplier_address_country": "",
            "error": f"Could not parse address: {str(e)}",
        }


import re


def split_address_advanced(address, address_type):
    try:
        # Split into parts by commas and clean
        parts = [part.strip() for part in address.split(",")]

        # Initialize fields
        street = nr = box = postalcode = city = country = ""

        # Handle country and postal/city
        if len(parts) >= 3:
            country = parts[-1]
            postal_city_part = parts[-2]
            remaining_parts = parts[:-2]
        elif len(parts) == 2:
            postal_city_part = parts[-1]
            remaining_parts = parts[:-1]
        else:
            raise ValueError("Unexpected address format")

        # Parse postalcode and city
        postal_parts = postal_city_part.strip().split(" ", 1)
        postalcode = postal_parts[0]
        city = postal_parts[1] if len(postal_parts) > 1 else ""

        # Look for box in remaining_parts
        box_candidate = None
        street_candidate = []
        for part in remaining_parts:
            if re.match(r"(?i)^box\s*\d+$", part):
                box_candidate = part
            else:
                street_candidate.append(part)

        if box_candidate:
            box_match = re.match(r"(?i)^box\s*(\d+)$", box_candidate)
            if box_match:
                box = box_match.group(1)

        # Join street parts and extract street and number
        street_full = " ".join(street_candidate)
        street_match = re.match(
            r"""^(.*?)              # Street name
                [\s,]+              # Space or comma
                (\d+)               # House number
                (?:\s*[-]\s*(\d+))? # Optional: hyphen followed by box number
            $""",
            street_full,
            re.IGNORECASE | re.VERBOSE,
        )

        if street_match:
            street = street_match.group(1).strip()
            nr = street_match.group(2)
            if not box and street_match.group(3):  # hyphen box as fallback
                box = street_match.group(3)
        if address_type == "supplier":
            return {
                "P_supplier_address_streetname": street,
                "P_supplier_address_streetnumber": nr,
                "P_supplier_address_box": box,
                "P_supplier_address_postalzone": postalcode,
                "P_supplier_address_city": city,
                "P_supplier_address_country": country,
            }
        elif address_type == "customer":
            return {
                "P_customer_address_streetname": street,
                "P_customer_address_streetnumber": nr,
                "P_customer_address_box": box,
                "P_customer_address_postalzone": postalcode,
                "P_customer_address_city": city,
                "P_customer_address_country": country,
            }
        else:
            raise ValueError(
                "Invalid address type specified. Use 'supplier' or 'customer'."
            )

    except Exception as e:
        return {
            "P_supplier_address_streetname": "",
            "P_supplier_address_streetnumber": "",
            "P_supplier_address_box": "",
            "P_supplier_address_postalzone": "",
            "P_supplier_address_city": "",
            "P_supplier_address_country": "",
            "error": f"Could not parse address: {str(e)}",
        }


supplier_address = input_json_recurv1.get("P_supplier_address", "")
if supplier_address:
    address_components = split_address_advanced(supplier_address, "supplier")
    print("Supplier address components:", address_components)
    input_json_recurv1.update(address_components)
else:
    print("No supplier address found in input JSON.")

customer_address = input_json_recurv1.get("P_customer_address", "")
if customer_address:
    address_components = split_address_advanced(customer_address, "customer")
    print("Customer address components:", address_components)
    input_json_recurv1.update(address_components)
else:
    print("No customer address found in input JSON.")
input_json_recurv1["P_supplier_address_streetname"] = input_json_recurv1.get(
    "P_supplier_address_streetname", ""
)
input_json_recurv1["P_supplier_address_postalzone"] = input_json_recurv1.get(
    "P_supplier_address_postalzone", ""
)
input_json_recurv1["P_supplier_address_city"] = input_json_recurv1.get(
    "P_supplier_address_city", ""
)
input_json_recurv1["P_supplier_address_country"] = input_json_recurv1.get(
    "P_supplier_address_country", ""
)
input_json_recurv1["P_supplier_address_box"] = input_json_recurv1.get(
    "P_supplier_address_box", ""
)
input_json_recurv1["P_supplier_address_streetnumber"] = input_json_recurv1.get(
    "P_supplier_address_streetnumber", ""
)


input_json_recurv1["P_customer_address_streetname"] = input_json_recurv1.get(
    "P_customer_address_streetname", ""
)
input_json_recurv1["P_customer_address_postalzone"] = input_json_recurv1.get(
    "P_customer_address_postalzone", ""
)
input_json_recurv1["P_customer_address_city"] = input_json_recurv1.get(
    "P_customer_address_city", ""
)
input_json_recurv1["P_customer_address_country"] = input_json_recurv1.get(
    "P_customer_address_country", ""
)

print("Input JSON after address parsing:", json.dumps(input_json_recurv1, indent=2))

# Print the invoice lines for debugging
input_json_recurv1["Invoice lines"] = input_json_recurv1.get("Invoice lines", [])
if not isinstance(input_json_recurv1["Invoice lines"], list):
    input_json_recurv1["Invoice lines"] = [input_json_recurv1["Invoice lines"]]
input_json_recurv1["Invoice lines"] = [
    {k: v for k, v in line.items() if k not in ["Invoice ID", "invoice_line_type"]}
    for line in input_json_recurv1["Invoice lines"]
]
input_json_recurv1["Invoice lines"] = [
    {
        k: v
        for k, v in line.items()
        if k
        not in [
            "Project team assignment",
            "Related actuals",
            "Related project team assignment fees",
        ]
    }
    for line in input_json_recurv1["Invoice lines"]
]


invoice_lines = input_json_recurv1["Invoice lines"]
print("Invoice lines:", json.dumps(invoice_lines, indent=2))
# Define how to map input keys to output keys (and optionally transform types)
# left side = input, right side is output
mapping_rules_body = {
    "invoice_type": "OrderType",
    "invoice nr": "OrderNumber",
    "Invoice date": "OrderDate",
    "invoice_description": "OrderTitle",
    "Payment Terms": "PaymentTerms",
    "To be paid before": "ExpiryDate",
    "Date from": "PeriodFrom",
    "Date til": "PeriodTill",
    "Total ex VAT": "TotalExcl",
    "Total VAT": "TotalVAT",
    "Total incl VAT": "TotalIncl",
    "Company": "Name",
    "Vat nr": "VATNumber",
    "PO": "Reference",
    "Date from EU": "PeriodFrom",
    "Date til EU": "PeriodTill",
    "P_payment_terms_note": "PaymentTerms",
}
mapping_rules_invoice_lines = {
    "Invoice line description": "Description",
    "Quantity": "Quantity",
    "Units": "Unit",
    "Unit fee": "UnitPriceExcl",
    "VAT percentage": "VATPercentage",
    "Note": "Reference",
    "Total ex VAT": "TotalExcl",
    "Total VAT": "TotalVAT",
}
mapping_rules_customer = {
    "P_customer_trade_name": "CommercialName",
    "P_customer_address_streetname": "Street",
    "P_customer_address_streetnumber": "StreetNumber",
    "P_customer_address_box": "Box",
    "P_customer_address_postalzone": "Zipcode",
    "P_customer_address_city": "City",
    "P_customer_address_country": "Country",
    "P_customer_address_postalzone": "Zipcode",
    "P_customer_country_id": "CountryCode",
    "P_customer_legal_name": "Name",
    "P_customer_contact_name": "Contact",
    "P_customer_contact_tel": "Phone",
    "P_customer_contact_email": "Email",
    "P_customer_vat_nr": "VATNumber",
    "P_customer_endpoint": "Identifier",
}
mapping_rules_supplier = {
    "P_supplier_trade_name": "CommercialName",
    "P_supplier_address_streetname": "Street",
    "P_supplier_address_streetnumber": "StreetNumber",
    "P_supplier_address_box": "Box",
    "P_supplier_address_postalzone": "Zipcode",
    "P_supplier_address_city": "City",
    "P_supplier_address_country": "Country",
    "P_supplier_country_id": "CountryCode",
    "P_supplier_legal_name": "Name",
    "P_supplier_contact_name": "Contact",
    "P_supplier_contact_tel": "Phone",
    "P_supplier_contact_email": "Email",
    "P_supplier_vat_nr": "VATNumber",
    "P_supplier_endpoint": "Identifier",
}

# left side = input, right side is output


# Transform it
output_json_body = map_json(input_json_recurv1, mapping_rules_body)
output_json_body["OrderType"] = (
    "Invoice"  # Assuming the invoice type is always "Invoice"
)
output_json_body["OrderDirection"] = "Income"  # Assuming the invoice is an income type

output_json_customer = map_json(input_json_recurv1, mapping_rules_customer)
output_json_supplier = map_json(input_json_recurv1, mapping_rules_supplier)
output_json_invoice_lines = [
    map_json(line, mapping_rules_invoice_lines) for line in invoice_lines
]
print("Output JSON Body:", json.dumps(output_json_body, indent=2))
print("Output JSON Customer:", json.dumps(output_json_customer, indent=2))
print("Output JSON Supplier:", json.dumps(output_json_supplier, indent=2))
print("Output JSON Invoice Lines:", json.dumps(output_json_invoice_lines, indent=2))


billit_payload_invoice_out = merge_objects(
    output_json_body,
    output_json_customer,
    output_json_supplier,
    output_json_invoice_lines,
)
print("Billit Payload Invoice Out:", json.dumps(billit_payload_invoice_out, indent=2))
billit_payload_invoice_out_cleaned = clean_json_data(billit_payload_invoice_out)
print(
    "Billit Payload Invoice Out Cleaned:",
    json.dumps(billit_payload_invoice_out_cleaned, indent=2),
)

# now send this json to billit to create the order
# please note that this only posts the order to Billit, next the order needs to be sent
# using the send_order function
print("Posting order to Billit...")
try:
    response_post_order = post_order_to_billit(billit_payload_invoice_out_cleaned)
    order_id = response_post_order
    print("Response from Billit:", response_post_order)
except Exception as e:
    print("Error posting order to Billit:", str(e))

try:
    if order_id:
        print(f"Order ID received: {order_id}")
        transport_type = "Peppol"  # Example transport type, can be changed as needed
        send_response = send_order(order_id, transport_type)
        print("Send Order Response:", send_response)
        if send_response == 200:
            print(
                f"Order {order_id} sent successfully with transport type {transport_type}."
            )
        else:
            print(
                f"Failed to send order {order_id} with transport type {transport_type}."
            )
    else:
        print("No Order ID found in the response.")
except Exception as e:
    print("Error sending order to Billit:", str(e))
# now update Appsheet with the created order info
try:
    appsheet_response = post_data_to_appsheet(
        table="invoices",
        rows=[billit_payload_invoice_out_cleaned],
        action="Add",
        app_name="Recurv Billit Handler",
        app_id="your_app_id_here",  # Replace with your actual AppSheet app ID
        app_access_key="your_app_access_key_here",  # Replace with your actual AppSheet access key
    )
    print("AppSheet Response:", appsheet_response.status_code)
    if appsheet_response.status_code == 200:
        print("Data posted to AppSheet successfully.")
    else:
        print(
            f"Failed to post data to AppSheet. Status code: {appsheet_response.status_code}, Response: {appsheet_response.text}"
        )
except Exception as e:
    print("Error posting data to AppSheet:", str(e))
