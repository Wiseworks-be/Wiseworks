# ************************************************************************************************
# THESE FUNCTIONS SUPPORT THE HANDLING OF DATA FOR HUBSPOT API's                                *
#                                                                                               *
# params: no params                                                                             *
#                                                                                               *
# creteated by: Marc De Krock                                                                   *
# date: 20250627                                                                                *
#                                                                                               *
# version: 1.0.0         date: 20250627       updated by Marc De Krock                          *
# supports:  contacts, companies, trainers, trainings, training session                         *
# it includes a testsuite with test data for all the above mentioned objects.                   *
# ************************************************************************************************

import json


# ************************************************************************************************
# Function to process JSON data and map it to AppSheet records
def get_rows_from_json(json_data):
    field_mapping_contacts = {
        "firstname": "first_name",
        "lastname": "last_name",
        "company": "primary_company",
        "phone": "tel_nr",
        "email": "email",
        "address": "main_address",
        "gender": "gender",
        # Add more as needed
    }
    field_mapping_companies = {
        "address": "address",
        "name": "name",
        "e_mail": "email",
        "phone": "phone",
        "btw_nummer": "vat_nr",
        "industry": "sector",
        "hs_logo_url": "hs_logo_url",
        # Add more as needed
    }
    field_mapping_custom_objects_training_sessions = {
        "aantal_dagdelen": "nr_dayparts",
        "beschrijving": "description",
        "code_trainingsessie": "training_session_code",
        "einddatum": "end_date",
        "hoofdlocatie": "main_location",
        "naam_trainingsessie": "title",
        "startdatum": "start_date",
        "type_training": "type_training",
        # Add more mappings as needed
    }
    field_mapping_custom_objects_trainers = {
        "contact": "contact",
        "nota": "note",
        "specialiteit": "specialty",
        # Add more mappings as needed
    }
    field_mapping_custom_objects_trainings = {
        "aantal_dagdelen": "nr_dayparts",
        "lange_beschrijving": "description",
        "naam_training": "name",
        "samenvatting": "summary",
        "training_code": "code",
        "titel_training": "title",
        # Add more mappings as needed
    }

    # NEW VERSION
    def detect_object_type(event):
        sub = event.get("subscriptionType", "")
        if sub.startswith("contact."):
            return "contact"
        elif sub.startswith("company."):
            return "company"
        elif sub.startswith("object."):
            return event.get("objectTypeId")  # e.g., "2-143964783"
        return None

    entity_type = detect_object_type(json_data[0])
    mapping_tables = {
        "company": "companies",
        "contact": "contacts",
        "2-143964984": "trainers",  # Custom object "objectTypeId" for trainers
        "2-143964783": "training_sessions",  # Custom object "objectTypeId" for training sessions
        "2-143967026": "trainings",  # Custom object "objectTypeId" for trainings
    }
    table_name = mapping_tables.get(entity_type)

    def build_appsheet_records(json_data):
        # Group all changes by objectId
        records = {}

        for event in json_data:
            object_id = str(event["objectId"])
            object_type = detect_object_type(event)

            if not object_type:
                continue

            # Choose the appropriate field mapping
            if table_name == "contacts":
                field_mapping = field_mapping_contacts
                id_field = "hs_contact_id"
            elif table_name == "companies":
                field_mapping = field_mapping_companies
                id_field = "hs_company_id"
            elif table_name == "training_sessions":  # Custom object
                field_mapping = field_mapping_custom_objects_training_sessions
                id_field = "hs_training_session_id"
            elif table_name == "trainers":  # Custom object
                field_mapping = field_mapping_custom_objects_trainers
                id_field = "hs_trainer_id"
            elif table_name == "trainings":  # Custom object
                field_mapping = field_mapping_custom_objects_trainings
                id_field = "hs_training_id"
            else:
                continue

            # Only handle property changes
            if "propertyName" in event and "propertyValue" in event:
                key = event["propertyName"]
                value = event["propertyValue"]

                if key in field_mapping:
                    mapped_key = field_mapping[key]

                    if object_id not in records:
                        records[object_id] = {}

                    records[object_id][mapped_key] = value
                    records[object_id][id_field] = object_id  # ensure ID included

        return list(records.values())

    # Build the records for AppSheet
    if json_data:
        mapped_records = build_appsheet_records(json_data)
    else:
        mapped_records = []
    object_type = detect_object_type(json_data[0])

    is_creation_event = any(
        item.get("subscriptionType")
        in ("contact.creation", "company.creation", "object.creation")
        for item in json_data
    )
    is_deletion_event = any(
        item.get("subscriptionType")
        in ("contact.deletion", "company.deletion", "object.deletion")
        for item in json_data
    )
    is_creation_or_update_event = any(
        item.get("subscriptionType")
        in ("contact.propertyChange", "company.propertyChange", "object.propertyChange")
        for item in json_data
    )
    change_flag = next(
        (item.get("changeFlag") for item in json_data if "changeFlag" in item), None
    )

    return (
        mapped_records,
        object_type,
        table_name,
        change_flag,
        is_creation_event,
        is_deletion_event,
        is_creation_or_update_event,
    )


#
# example usage
# Uncomment the following lines to test the function with the provided JSON data set
"""mapped_records, object_type, table_name, change_flag, is_creation_event, is_deletion_event, is_creation_or_update_event = get_rows_from_json(json_data_set)
print("Assembled rows for AppSheet:", json.dumps(mapped_records, indent=2))
print("Object type:", object_type)
print("Table name:", table_name)
print("Change flag:", change_flag)
print("Is creation event:", is_creation_event)
print("Is deletion event:", is_deletion_event)
print("Is creation or update event:", is_creation_or_update_event)"""
# ************************************************************************************************
