
import re
from datetime import datetime

#*****************************************************
def capitalize_keys(data):
    if isinstance(data, dict):
        return {
            key[0].upper() + key[1:] if key else key: capitalize_keys(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [capitalize_keys(item) for item in data]
    else:
        return data
#*****************************************************
def replace_empty_values(data):
    if isinstance(data, dict):
        return {
            key: replace_empty_values(value) if isinstance(value, (dict, list)) else ("-" if value in ("", None) else value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [replace_empty_values(item) for item in data]
    else:
        return "-" if data in ("", None) else data
#*****************************************************
def clean_money_in_json(data):
    if isinstance(data, dict):
        return {k: clean_money_in_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_money_in_json(item) for item in data]
    elif isinstance(data, str):
        # Match and clean Euro-formatted money strings like "€1,752.66"
        match = re.match(r"^€?\s*[\d,]+\.\d{2}$", data.strip())
        if match:
            clean = data.replace("€", "").replace(",", "").strip()
            return clean
        return data
    else:
        return data

#*****************************************************
def clean_currency_string(value):
    """
    Cleans a string representation of a price, removing currency symbols,
    handling EU/US number formats (prioritizing EU interpretation as per request),
    and converting it to a float.

    Args:
        value (str): The input string that might represent a currency amount.

    Returns:
        float: The cleaned numerical value as a float if successfully parsed.
        str: The original string if it cannot be parsed as a currency amount.
        Any: The original value if it's not a string.
    """
    if not isinstance(value, str):
        return value # Return original value if it's not a string (e.g., int, float, bool, None)

    # Define common currency symbols for detection
    currency_symbols_patterns = r'[€$£¥₹₽₴฿]'

    # Remove common currency symbols and strip leading/trailing whitespace
    cleaned_value = re.sub(currency_symbols_patterns, '', value).strip()
    # Remove spaces used as thousands separators (e.g., "2 600,23")
    cleaned_value = cleaned_value.replace(' ', '') 

    # Handle empty string after cleaning (e.g. from just currency symbol or empty input)
    if not cleaned_value:
        return value # Cannot convert empty string to float properly, return original.

    # --- Format Detection and Conversion Logic ---
    # Determine number format based on separator presence and position
    last_comma_idx = cleaned_value.rfind(',')
    last_dot_idx = cleaned_value.rfind('.')
    
    # Case 1: Contains both '.' and ',' (e.g., '1.234,56' or '1,234.56')
    if last_comma_idx != -1 and last_dot_idx != -1:
        if last_comma_idx > last_dot_idx:
            # EU format: comma is decimal, dot is thousands (e.g., '1.234,56')
            cleaned_value = cleaned_value.replace('.', '')  # Remove thousands separators
            cleaned_value = cleaned_value.replace(',', '.')  # Replace decimal separator
        else:
            # US format: dot is decimal, comma is thousands (e.g., '1,234.56')
            cleaned_value = cleaned_value.replace(',', '')  # Remove thousands separators
            # Dot is already the standard decimal for float conversion
    
    # Case 2: Contains only ',' (e.g., '123,45')
    elif last_comma_idx != -1:
        # EU decimal format: comma is decimal
        cleaned_value = cleaned_value.replace(',', '.')

    # Case 3: Contains only '.' (most ambiguous case: '123.45' vs '1.234')
    elif last_dot_idx != -1:
        # If it matches a clear US thousands pattern (like '1.234') AND it's not clearly a decimal (e.g., '1.23' or '123.45'), remove the dots.
        # This regex ensures we only remove dots if they are clearly structured as thousands separators (xxx.xxx).
        # Example: '1.234' -> removed to '1234'. '123.45' -> left as '123.45'.
        if re.fullmatch(r'\d{1,3}(?:\.\d{3})+$', cleaned_value) and not re.fullmatch(r'\d+\.\d{1,2}$', cleaned_value):
            cleaned_value = cleaned_value.replace('.', '')

    # --- Final Conversion ---
    try:
        return float(cleaned_value)
    except ValueError:
        # If, after all cleaning, it still cannot be converted to a float,
        # return the original string to avoid data loss.
        return value 

def process_json_recursively(data, key_name=None):
    """
    Recursively processes a JSON-like structure (dict or list).
    Applies the `clean_currency_string` function to all string values found.
    Handles specific formatting requirements for floats and integers.

    Args:
        data (dict | list | any): The JSON data to process.
        key_name (str, optional): The name of the current key being processed. Used for
                                  special handling of "P_invoice_typecode". Defaults to None.

    Returns:
        dict | list | any: The processed JSON data with currency strings converted to floats,
                           and whole number floats converted to integers, and floats rounded.
    """
    if isinstance(data, dict):
        # Recursively process dictionary values, passing the current key name
        return {key: process_json_recursively(value, key_name=key) for key, value in data.items()}
    elif isinstance(data, list):
        # Recursively process list elements, passing the key name from the parent if available
        return [process_json_recursively(element, key_name=key_name) for element in data]
    elif isinstance(data, str):
        # Attempt to clean and convert the string value
        processed_value = clean_currency_string(data)
        
        if isinstance(processed_value, float):
            # If the string was successfully converted to a float
            if key_name == "P_invoice_typecode":
                # Special handling for "P_invoice_typecode": should be an integer if numerical
                # and "without any decimals".
                if processed_value.is_integer():
                    return int(processed_value)
                else:
                    # If it's a float with decimals (e.g., 380.5) for this key,
                    # return the original string to avoid silent data loss/rounding.
                    # This implies that if "P_invoice_typecode" is not a whole number, it's considered invalid for this field type.
                    return data 
            else: 
                # For all other keys where a string converted to a float,
                # round the float to 2 decimal places.
                # Note: A float like 2600.0 or 2600.00 is internally represented just as 2600.0.
                # The 'round(value, 2)' ensures calculations are to 2 decimal places,
                # and for display, you would format it: f"{value:.2f}".
                return round(processed_value, 2)
        
        # If cleaned_currency_string did not return a float (e.g., it returned the original string
        # because it couldn't be parsed as a number, or it was an empty string), return it as is.
        return processed_value
    else:
        # For other types (int, float, bool, None) that are not strings, lists, or dicts,
        # return them as-is. This function primarily targets string conversion/formatting.
        return data

#*****************************************************
def extract_vat_percentage(vat_string):
    try:
        return int(float(vat_string.strip().replace("%", "")))
    except Exception:
        return None  # or fallback value like 0
#*****************************************************    
def clean_vat_in_json(data):
    if isinstance(data, dict):
        return {k: clean_vat_in_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_vat_in_json(item) for item in data]
    elif isinstance(data, str):
        match = re.match(r"^\d+(\.\d+)?%$", data.strip())
        if match:
            return int(float(data.strip().replace("%", "")))
        return data
    else:
        return data
#*****************************************************
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
            "P_supplier_address_country": country
        }


    except Exception as e:
        return {
            "P_supplier_address_streetname": "",
            "P_supplier_address_postalzone": "",
            "P_supplier_address_city": "",
            "P_supplier_address_country": "",
            "error": f"Could not parse address: {str(e)}"
        }
#*****************************************************
def split_customer_address_for_template(address):
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
            "P_customer_address_streetname": street_and_nr,
            "P_customer_address_postalzone": postalcode,
            "P_customer_address_city": city,
            "P_customer_address_country": country
        }

    except Exception as e:
        return {
            "P_customer_address_streetname": "",
            "P_customer_address_postalzone": "",
            "P_customer_address_city": "",
            "P_customer_address_country": "",
            "error": f"Could not parse address: {str(e)}"
        }
#*****************************************************
def normalize_keys(data):
    if isinstance(data, dict):
        return {
            key.replace(" ", "_"): normalize_keys(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [normalize_keys(item) for item in data]
    else:
        return data
#*****************************************************
#** FUNCTION to make the dates in the JSON normalized **
def reformat_dates_in_json(data, input_format="%m/%d/%Y", output_format="%d/%m/%Y"):
    """
    Recursively reformats date strings in a nested JSON-like structure.
    
    :param data: The JSON-like structure (dict/list)
    :param input_format: The expected format of the input date strings
    :param output_format: The desired format of the output date strings
    :return: A new structure with reformatted date strings
    """
    if isinstance(data, dict):
        return {
            key: reformat_dates_in_json(value, input_format, output_format)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [
            reformat_dates_in_json(item, input_format, output_format)
            for item in data
        ]
    elif isinstance(data, str):
        try:
            dt = datetime.strptime(data, input_format)
            return dt.strftime(output_format)
        except ValueError:
            return data  # Not a date string, return as-is
    else:
        return data  # Return all non-string values unchanged
#*****************************************************
def clean_json_data_for_carbone(data):
    """
    Cleans the JSON data by capitalizing keys, replacing empty values, and normalizing keys and reformatting the dates to Peppol requirements.
    
    :param data: The JSON data to clean
    :return: The cleaned JSON data
    """
    data = capitalize_keys(data)
    #print("data after capitalize_keys",data)
    data = replace_empty_values(data)
    #print("data after replace_empty_values",data)
    data = process_json_recursively(data)
    #print("data after make prices float : ", json.dumps(data, indent=2))
    data = clean_vat_in_json(data)
    #print("data after clean_vat_in_json",data)
    #data = split_supplier_address_for_template(data.get("supplier_address", ""))
    #print("data after split_supplier_address_for_template",data)
    data = normalize_keys(data)
    #print("data after normalize_keys",data)
    data = reformat_dates_in_json(data, "%m/%d/%Y", "%Y-%m-%d")
    #print("data after reformat_dates_in_json",data)
    return data
#*****************************************************
def format_number_eu(value):
    """Convert float to EU formatted string: 11560.00 → '11.560,00'"""
    s = f"{value:,.2f}"              # '11,560.00'
    s = s.replace(",", "X").replace(".", ",").replace("X", " ")
    return s

def try_convert_string_number(value):
    """Try to convert a string to a number, format if successful."""
    try:
        # Try to parse as float
        num = float(value)
        return format_number_eu(num)
    except (ValueError, TypeError):
        return value  # Leave non-numeric strings untouched

def convert_string_numbers_in_json(data):
    """Recursively convert numeric strings in JSON-like structure to EU format."""
    if isinstance(data, dict):
        return {k: convert_string_numbers_in_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_string_numbers_in_json(item) for item in data]
    elif isinstance(data, str):
        return try_convert_string_number(value=data)
    else:
        return data  # Leave other types untouched (e.g., bool, None)
#*****************************************************
