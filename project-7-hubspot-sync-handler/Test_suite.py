import json
from hubspot_utils import get_rows_from_json
import requests

# base_path = Path(__file__).parent
false = False
true = True
null = None

# TEST DATA
# COMPANY
add_training = [
    {
        "eventId": 2326225553,
        "subscriptionId": 3849713,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "naam_training",
        "propertyValue": "Project Management (for testing)",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3821261304,
        "subscriptionId": 3849716,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "training_code",
        "propertyValue": "PPM1",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2415523459,
        "subscriptionId": 3849711,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "hubspot_owner_id",
        "propertyValue": "75514748",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3957075328,
        "subscriptionId": 3849712,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "lange_beschrijving",
        "propertyValue": "<p><strong>Praktische Projectmanagementtraining</strong></p>\n<p>In deze hands-on training leren deelnemers de essentiële vaardigheden om projecten efficiënt te plannen, organiseren en opvolgen. Aan de hand van realistische cases en interactieve oefeningen krijgen ze inzicht in projectfasen, rolverdeling, risicoanalyse en communicatie. De focus ligt op toepasbare technieken, zodat deelnemers na afloop meteen aan de slag kunnen in hun eigen werkomgeving. Ideaal voor (startende) projectleiders en teamleden die verantwoordelijkheid opnemen binnen projecten.</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 25193029,
        "subscriptionId": 3849708,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "aantal_dagdelen",
        "propertyValue": "3",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2145459286,
        "subscriptionId": 3849706,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.creation",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "changeFlag": "CREATED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 2464804026,
        "subscriptionId": 3849715,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "titel_training",
        "propertyValue": "<p>PRACTISCHE PROJECT MANAGEMENT</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2601963002,
        "subscriptionId": 3849714,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "samenvatting",
        "propertyValue": "<p>3 daagse training voor beginnende en ervaren project managers</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
]
delete_training = [
    {
        "eventId": 3771921218,
        "subscriptionId": 3849707,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751277051514,
        "subscriptionType": "object.deletion",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "changeFlag": "DELETED",
        "changeSource": "CRM_UI_BULK_ACTION",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 3771921218,
        "subscriptionId": 3849707,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751277051514,
        "subscriptionType": "object.deletion",
        "attemptNumber": 0,
        "objectId": 180584432882,  # non existing objectId
        "objectTypeId": "2-143967026",
        "changeFlag": "DELETED",
        "changeSource": "CRM_UI_BULK_ACTION",
        "sourceId": "userId:75514748",
    },
]

update_training = [
    {
        "eventId": 2326225553,
        "subscriptionId": 3849713,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "naam_training",
        "propertyValue": "Project Management (for testing 4)",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    }
]

add_trainer = [
    {
        "eventId": 1671391376,
        "subscriptionId": 3829970,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "nota",
        "propertyValue": "NL+UK",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 4108526299,
        "subscriptionId": 3829965,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "bio",
        "propertyValue": "<p>projectmanagementtrainer met meer dan 15 jaar praktijkervaring in diverse sectoren, waaronder IT, bouw en consultancy. Hij specialiseert zich in Agile en PRINCE2-methodologieën en staat bekend om zijn hands-on aanpak en talent om complexe materie helder over te brengen. Hij helpt teams en organisaties om projecten efficiënter te plannen, aan te sturen en succesvol af te ronden.</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2307281776,
        "subscriptionId": 3829966,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "contact",
        "propertyValue": "MDKA",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 1969350321,
        "subscriptionId": 3829971,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "specialiteit",
        "propertyValue": "Project Management",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2899962578,
        "subscriptionId": 3829963,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.creation",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "changeFlag": "CREATED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 2212172420,
        "subscriptionId": 3829969,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "hubspot_owner_id",
        "propertyValue": "75514748",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
]

delete_trainer = [
    {
        "eventId": 3771921218,
        "subscriptionId": 3849707,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751277051514,
        "subscriptionType": "object.deletion",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "changeFlag": "DELETED",
        "changeSource": "CRM_UI_BULK_ACTION",
        "sourceId": "userId:75514748",
    }
]

update_trainer = [
    {
        "eventId": 1671391376,
        "subscriptionId": 3829970,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "nota",
        "propertyValue": "NL+UK",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 4108526299,
        "subscriptionId": 3829965,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "bio",
        "propertyValue": "<p>projectmanagementtrainer met meer dan 15 jaar praktijkervaring in diverse sectoren, waaronder IT, bouw en consultancy. Hij specialiseert zich in Agile en PRINCE2-methodologieën en staat bekend om zijn hands-on aanpak en talent om complexe materie helder over te brengen. Hij helpt teams en organisaties om projecten efficiënter te plannen, aan te sturen en succesvol af te ronden.</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2307281776,
        "subscriptionId": 3829966,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "contact",
        "propertyValue": "MDKA",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 1969350321,
        "subscriptionId": 3829971,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "specialiteit",
        "propertyValue": "Project Management Professional",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2212172420,
        "subscriptionId": 3829969,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "contact",
        "propertyValue": "MDKB",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
]
add_training_session = [
    {
        "eventId": 3674126568,
        "subscriptionId": 3830537,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "propertyName": "beschrijving",
        "propertyValue": "Project Management Advanced",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 4002689486,
        "subscriptionId": 3830539,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "propertyName": "data",
        "propertyValue": "<p>This is a testlocation</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3976318146,
        "subscriptionId": 3830544,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "propertyName": "hubspot_owner_id",
        "propertyValue": "75514748",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3061532089,
        "subscriptionId": 3830541,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "propertyName": "hoofdlocatie",
        "propertyValue": "Puurs",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3279996480,
        "subscriptionId": 3830546,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "propertyName": "startdatum",
        "propertyValue": "1752559200000",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 1310150680,
        "subscriptionId": 3830538,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "propertyName": "code_trainingsessie",
        "propertyValue": "TSWW",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3514658810,
        "subscriptionId": 3830540,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "propertyName": "einddatum",
        "propertyValue": "1752732000000",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 1618975963,
        "subscriptionId": 3830534,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.creation",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "changeFlag": "CREATED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 3929404411,
        "subscriptionId": 3830545,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "propertyName": "naam_trainingsessie",
        "propertyValue": "test_session",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2667897146,
        "subscriptionId": 3830547,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1752480758764,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 190214084811,
        "objectTypeId": "2-143964783",
        "propertyName": "type_training",
        "propertyValue": "OA",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
]
add_training_session2 = [
    {
        "eventId": 2414526794,
        "subscriptionId": 3830534,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.creation",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "changeFlag": "CREATED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 1070754430,
        "subscriptionId": 3830547,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "type_training",
        "propertyValue": "OA",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2747845440,
        "subscriptionId": 3830544,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "hubspot_owner_id",
        "propertyValue": "75514748",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3514137289,
        "subscriptionId": 3830538,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "code_trainingsessie",
        "propertyValue": "PMV-1",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 1112758762,
        "subscriptionId": 3830545,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "naam_trainingsessie",
        "propertyValue": "Project Management voor PMV",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3953489394,
        "subscriptionId": 3830546,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "einddatum",
        "propertyValue": "1751869000000",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3953489394,
        "subscriptionId": 3830546,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "startdatum",
        "propertyValue": "1751868000000",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3267918886,
        "subscriptionId": 3830536,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751299321063,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "aantal_dagdelen",
        "propertyValue": "4",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 428118009,
        "subscriptionId": 3830541,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "hoofdlocatie",
        "propertyValue": "Puurs",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
]

delete_training_session = [
    {
        "eventId": 4108181006,
        "subscriptionId": 3830535,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751299465874,
        "subscriptionType": "object.deletion",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "changeFlag": "DELETED",
        "changeSource": "CRM_UI_BULK_ACTION",
        "sourceId": "userId:75514748",
    }
]

update_training_session = [
    {
        "eventId": 1070754430,
        "subscriptionId": 3830547,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "type_training",
        "propertyValue": "TRUE",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2747845440,
        "subscriptionId": 3830544,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "hubspot_owner_id",
        "propertyValue": "75514748",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3514137289,
        "subscriptionId": 3830538,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "code_trainingsessie",
        "propertyValue": "PMV-2",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 1112758762,
        "subscriptionId": 3830545,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "naam_trainingsessie",
        "propertyValue": "Project Management voor PMV 2",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3953489394,
        "subscriptionId": 3830546,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "einddatum",
        "propertyValue": "1751869000000",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3953489394,
        "subscriptionId": 3830546,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "startdatum",
        "propertyValue": "1751868000000",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3267918886,
        "subscriptionId": 3830536,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751299321063,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "aantal_dagdelen",
        "propertyValue": "4",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 428118009,
        "subscriptionId": 3830541,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "hoofdlocatie",
        "propertyValue": "Puurs",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
]

add_company = [
    {
        "eventId": 789828234,
        "subscriptionId": 3855048,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751359968376,
        "subscriptionType": "company.creation",
        "attemptNumber": 0,
        "objectId": 181822088425,
        "changeFlag": "CREATED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 4193894086,
        "subscriptionId": 3855055,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751359968376,
        "subscriptionType": "company.propertyChange",
        "attemptNumber": 0,
        "objectId": 181822088425,
        "propertyName": "industry",
        "propertyValue": "MANAGEMENT_CONSULTING",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 982134580,
        "subscriptionId": 3855051,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751359968376,
        "subscriptionType": "company.propertyChange",
        "attemptNumber": 0,
        "objectId": 181822088425,
        "propertyName": "name",
        "propertyValue": "Querbus",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
]

delete_company = [
    {
        "eventId": 3613889437,
        "subscriptionId": 3090145,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1749047009007,
        "subscriptionType": "company.deletion",
        "attemptNumber": 0,
        "objectId": 181822088425,
        "changeFlag": "DELETED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]

update_company = [
    {
        "eventId": 3359777471,
        "subscriptionId": 3855050,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751360710992,
        "subscriptionType": "company.propertyChange",
        "attemptNumber": 0,
        "objectId": 181822088425,
        "propertyName": "address",
        "propertyValue": "Grote Lei 17 bus5",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]

add_contact = [
    {
        "eventId": 962803702,
        "subscriptionId": 3855062,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751360059094,
        "subscriptionType": "contact.propertyChange",
        "attemptNumber": 0,
        "objectId": 347163431125,
        "propertyName": "phone",
        "propertyValue": "+32475662049",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 1074165951,
        "subscriptionId": 3855063,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751360059094,
        "subscriptionType": "contact.propertyChange",
        "attemptNumber": 0,
        "objectId": 347163431125,
        "propertyName": "email",
        "propertyValue": "max@verstaaaappen.nl",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 1913696676,
        "subscriptionId": 3855059,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751360059094,
        "subscriptionType": "contact.propertyChange",
        "attemptNumber": 0,
        "objectId": 347163431125,
        "propertyName": "firstname",
        "propertyValue": "Max",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 3508664407,
        "subscriptionId": 3855057,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751360059094,
        "subscriptionType": "contact.creation",
        "attemptNumber": 0,
        "objectId": 347163431125,
        "changeFlag": "CREATED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 464083239,
        "subscriptionId": 3855060,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751360059094,
        "subscriptionType": "contact.propertyChange",
        "attemptNumber": 0,
        "objectId": 347163431125,
        "propertyName": "lastname",
        "propertyValue": "Verstappen",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
]

delete_contact = [
    {
        "eventId": 3613889437,
        "subscriptionId": 3090145,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1749047009007,
        "subscriptionType": "contact.deletion",
        "attemptNumber": 0,
        "objectId": 347163431125,
        "changeFlag": "DELETED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]

update_contact = [
    {
        "eventId": 1160497708,
        "subscriptionId": 3855063,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751360504518,
        "subscriptionType": "contact.propertyChange",
        "attemptNumber": 0,
        "objectId": 347163431125,
        "propertyName": "email",
        "propertyValue": "max@verstaaaaaaaappen.nl",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]


# +# COMPANY***********************************

json_data_set_update_company = [
    {
        "eventId": 3747341312,
        "subscriptionId": 3090150,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1749047325318,
        "subscriptionType": "company.propertyChange",
        "attemptNumber": 0,
        "objectId": 127018117959,
        "propertyName": "name",
        "propertyValue": "Struck",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]
json_data_set_update_company_2 = [
    {
        "eventId": 1780098985,
        "subscriptionId": 3752571,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1751290186071,
        "subscriptionType": "company.propertyChange",
        "attemptNumber": 0,
        "objectId": 33255045519,
        "propertyName": "address",
        "propertyValue": "Diamantstraat 8 - bus 343, 2200 Herentals",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]
json_data_set_update_company_with_logo = [
    {
        "eventId": 3747341312,
        "subscriptionId": 3090150,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1749047325318,
        "subscriptionType": "company.propertyChange",
        "attemptNumber": 0,
        "objectId": 127018117959,
        "propertyName": "hs_logo_url",
        "propertyValue": "https://www.example.com/logo.png",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]
json_data_set_update_company_with_address = [
    {
        "eventId": 3747341312,
        "subscriptionId": 3090150,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1749047325318,
        "subscriptionType": "company.propertyChange",
        "attemptNumber": 0,
        "objectId": 127018117959,
        "propertyName": "address",
        "propertyValue": "123 Main St, Anytown, USA",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]
# TRAINER***********************************
json_data_set_update_trainer = [
    {
        "eventId": 3747341312,
        "subscriptionId": 3090150,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1749047325318,
        "subscriptionType": "trainer.propertyChange",
        "attemptNumber": 0,
        "objectId": 127018117959,
        "propertyName": "speciality",
        "propertyValue": "Project Management",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]

json_data_set_add_trainer = [
    {
        "eventId": 1671391376,
        "subscriptionId": 3829970,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "nota",
        "propertyValue": "NL+UK",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 4108526299,
        "subscriptionId": 3829965,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "bio",
        "propertyValue": "<p>projectmanagementtrainer met meer dan 15 jaar praktijkervaring in diverse sectoren, waaronder IT, bouw en consultancy. Hij specialiseert zich in Agile en PRINCE2-methodologieën en staat bekend om zijn hands-on aanpak en talent om complexe materie helder over te brengen. Hij helpt teams en organisaties om projecten efficiënter te plannen, aan te sturen en succesvol af te ronden.</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2307281776,
        "subscriptionId": 3829966,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "contact",
        "propertyValue": "MDKA",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 1969350321,
        "subscriptionId": 3829971,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "specialiteit",
        "propertyValue": "Project Management",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2899962578,
        "subscriptionId": 3829963,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.creation",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "changeFlag": "CREATED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 2212172420,
        "subscriptionId": 3829969,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750865189547,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469910223,
        "objectTypeId": "2-143964984",
        "propertyName": "hubspot_owner_id",
        "propertyValue": "75514748",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
]

# TRAINNG SESSIONS******************************
json_data_set_add_training_session = [
    {
        "eventId": 2414526794,
        "subscriptionId": 3830534,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.creation",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "changeFlag": "CREATED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 1070754430,
        "subscriptionId": 3830547,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "type_training",
        "propertyValue": "AOM",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2747845440,
        "subscriptionId": 3830544,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "hubspot_owner_id",
        "propertyValue": "75514748",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3514137289,
        "subscriptionId": 3830538,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "code_trainingsessie",
        "propertyValue": "PMV-1",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 1112758762,
        "subscriptionId": 3830545,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "naam_trainingsessie",
        "propertyValue": "Project Management voor PMV",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3953489394,
        "subscriptionId": 3830546,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "startdatum",
        "propertyValue": "1751868000000",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 428118009,
        "subscriptionId": 3830541,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1750867404361,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 177469912274,
        "objectTypeId": "2-143964783",
        "propertyName": "hoofdlocatie",
        "propertyValue": "Puurs",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
]
# TRAININGS************************************
json_data_set_add_training = [
    {
        "eventId": 2326225553,
        "subscriptionId": 3849713,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "naam_training",
        "propertyValue": "Project Management (for testing)",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3821261304,
        "subscriptionId": 3849716,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "training_code",
        "propertyValue": "PPM1",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2415523459,
        "subscriptionId": 3849711,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "hubspot_owner_id",
        "propertyValue": "75514748",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 3957075328,
        "subscriptionId": 3849712,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "lange_beschrijving",
        "propertyValue": "<p><strong>Praktische Projectmanagementtraining</strong></p>\n<p>In deze hands-on training leren deelnemers de essentiële vaardigheden om projecten efficiënt te plannen, organiseren en opvolgen. Aan de hand van realistische cases en interactieve oefeningen krijgen ze inzicht in projectfasen, rolverdeling, risicoanalyse en communicatie. De focus ligt op toepasbare technieken, zodat deelnemers na afloop meteen aan de slag kunnen in hun eigen werkomgeving. Ideaal voor (startende) projectleiders en teamleden die verantwoordelijkheid opnemen binnen projecten.</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 25193029,
        "subscriptionId": 3849708,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "aantal_dagdelen",
        "propertyValue": "3",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2145459286,
        "subscriptionId": 3849706,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.creation",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "changeFlag": "CREATED",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 2464804026,
        "subscriptionId": 3849715,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "titel_training",
        "propertyValue": "<p>PRACTISCHE PROJECT MANAGEMENT</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
    {
        "eventId": 2601963002,
        "subscriptionId": 3849714,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751276050977,
        "subscriptionType": "object.propertyChange",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "propertyName": "samenvatting",
        "propertyValue": "<p>3 daagse training voor beginnende en ervaren project managers</p>",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
        "isSensitive": false,
    },
]

json_data_set_delete_training = [
    {
        "eventId": 3771921218,
        "subscriptionId": 3849707,
        "portalId": 145883449,
        "appId": 14947547,
        "occurredAt": 1751277051514,
        "subscriptionType": "object.deletion",
        "attemptNumber": 0,
        "objectId": 180584432881,
        "objectTypeId": "2-143967026",
        "changeFlag": "DELETED",
        "changeSource": "CRM_UI_BULK_ACTION",
        "sourceId": "userId:75514748",
    }
]

# CONTACTS***********************************
json_data_set_delete_contact_multiple = [
    {
        "eventId": 3747341311,
        "subscriptionId": 3090146,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1745935376380,
        "subscriptionType": "contact.deletion",
        "attemptNumber": 0,
        "objectId": 117957925658,
        "changeFlag": "DELETED",
        "changeSource": "CRM_UI_BULK_ACTION",
        "sourceId": "userId:75514748",
    },
    {
        "eventId": 1604798277,
        "subscriptionId": 3090146,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1745935376377,
        "subscriptionType": "contact.deletion",
        "attemptNumber": 0,
        "objectId": 117958115842,
        "changeFlag": "DELETED",
        "changeSource": "CRM_UI_BULK_ACTION",
        "sourceId": "userId:75514748",
    },
]

json_data_set_update_contact = [
    {
        "eventId": 3953469553,
        "subscriptionId": 3090151,
        "portalId": 48610308,
        "appId": 6840319,
        "occurredAt": 1749047325318,
        "subscriptionType": "contact.propertyChange",
        "attemptNumber": 0,
        "objectId": 127018117959,
        "propertyName": "lastname",
        "propertyValue": "Struck",
        "changeSource": "CRM_UI",
        "sourceId": "userId:75514748",
    }
]


json_data = json_data_set_delete_contact_multiple
# json_data_set = json_data_set_update_contact
# json_data_set = json_data_set_update_company
# json_data_set = json_data_set_update_company_with_logo
# json_data_set = json_data_set_update_company_with_address
# json_data_set = json_data_set_update_trainer
# json_data_set = json_data_set_add_trainer
# json_data_set = json_data_set_add_training_session


# TESTSUITE
def run_testsuite():
    print("Running testsuite...")
    json_data_set = json_data_set_update_company
    (
        mapped_records,
        object_type,
        table_name,
        change_flag,
        is_creation_event,
        is_deletion_event,
        is_creation_or_update_event,
    ) = get_rows_from_json(json_data_set)
    print("Assembled rows for AppSheet:", json.dumps(mapped_records, indent=2))
    print("Object type:", object_type)
    print("Table name:", table_name)
    print("Change flag:", change_flag)
    print("Is creation event:", is_creation_event)
    print("Is deletion event:", is_deletion_event)
    print("Is creation or update event:", is_creation_or_update_event)

    json_data_set = json_data_set_update_company_with_logo
    (
        mapped_records,
        object_type,
        table_name,
        change_flag,
        is_creation_event,
        is_deletion_event,
        is_creation_or_update_event,
    ) = get_rows_from_json(json_data_set)
    print("Assembled rows for AppSheet:", json.dumps(mapped_records, indent=2))
    print("Object type:", object_type)
    print("Table name:", table_name)
    print("Change flag:", change_flag)
    print("Is creation event:", is_creation_event)
    print("Is deletion event:", is_deletion_event)
    print("Is creation or update event:", is_creation_or_update_event)
    json_data_set = json_data_set_update_company_with_address
    (
        mapped_records,
        object_type,
        table_name,
        change_flag,
        is_creation_event,
        is_deletion_event,
        is_creation_or_update_event,
    ) = get_rows_from_json(json_data_set)
    print("Assembled rows for AppSheet:", json.dumps(mapped_records, indent=2))
    print("Object type:", object_type)
    print("Table name:", table_name)
    print("Change flag:", change_flag)
    print("Is creation event:", is_creation_event)
    print("Is deletion event:", is_deletion_event)
    print("Is creation or update event:", is_creation_or_update_event)
    json_data_set = json_data_set_update_trainer
    (
        mapped_records,
        object_type,
        table_name,
        change_flag,
        is_creation_event,
        is_deletion_event,
        is_creation_or_update_event,
    ) = get_rows_from_json(json_data_set)
    print("Assembled rows for AppSheet:", json.dumps(mapped_records, indent=2))
    print("Object type:", object_type)
    print("Table name:", table_name)
    print("Change flag:", change_flag)
    print("Is creation event:", is_creation_event)
    print("Is deletion event:", is_deletion_event)
    print("Is creation or update event:", is_creation_or_update_event)
    json_data_set = json_data_set_add_trainer
    (
        mapped_records,
        object_type,
        table_name,
        change_flag,
        is_creation_event,
        is_deletion_event,
        is_creation_or_update_event,
    ) = get_rows_from_json(json_data_set)
    print("Assembled rows for AppSheet:", json.dumps(mapped_records, indent=2))
    print("Object type:", object_type)
    print("Table name:", table_name)
    print("Change flag:", change_flag)
    print("Is creation event:", is_creation_event)
    print("Is deletion event:", is_deletion_event)
    print("Is creation or update event:", is_creation_or_update_event)
    json_data_set = json_data_set_add_training_session
    (
        mapped_records,
        object_type,
        table_name,
        change_flag,
        is_creation_event,
        is_deletion_event,
        is_creation_or_update_event,
    ) = get_rows_from_json(json_data_set)
    print("Assembled rows for AppSheet:", json.dumps(mapped_records, indent=2))
    print("Object type:", object_type)
    print("Table name:", table_name)
    print("Change flag:", change_flag)
    print("Is creation event:", is_creation_event)
    print("Is deletion event:", is_deletion_event)
    print("Is creation or update event:", is_creation_or_update_event)
    print("****************************************")
    print("*********Testsuite completed.***********")
    print("****************************************")


def run_testsuite_to_local():
    print("Running testsuite to local...")

    def run_script(json_data_set, name=""):
        print("Running script:", name)
        response = requests.post(local_url, json=json_data_set)
        if response.status_code == 200:
            print("Testsuite executed successfully against local instance.")
            print("Response:", response.json())
        else:
            print(
                f"Failed to execute testsuite against local instance. Status code: {response.status_code}"
            )

    # Here you would implement the logic to run the testsuite against a local instance
    # For now, we will just call the main testsuite function
    local_url = "http://localhost:8080/?AppKey=7e9f8b3d5a1c4297fa6b0de4392ed10f8ab7e12466f52a8d5cfe90b6432d90"
    """run_script(add_trainer)
    run_script(delete_trainer)
    run_script(add_trainer)
    run_script(update_trainer)"""

    run_script(add_training_session, "add training session")
    # run_script(delete_training_session, "delete training session")
    # run_script(add_training_session, "add training session")
    # run_script(update_training_session, "update training session")

    """run_script(add_training)
    run_script(delete_training)
    run_script(add_training)
    run_script(update_training)

    run_script(add_company)
    run_script(delete_company)
    run_script(add_company)
    run_script(update_company)

    run_script(add_contact)
    run_script(delete_contact)
    run_script(add_contact)
    run_script(update_contact)"""


"""if __name__ == "__main__":
    run_testsuite()
else:
    print(
        "This script is intended to be run as a standalone program. Please run it directly to execute the testsuite."
    )
    # If this module is imported, we can still run the testsuite
    run_testsuite()
    # This allows for both standalone execution and import without side effects."""


if __name__ == "__main__":
    run_testsuite_to_local()
    # run_testsuite_to_gcr()
else:
    print(
        "This script is intended to be run as a standalone program. Please run it directly to execute the testsuite."
    )
    # If this module is imported, we can still run the testsuite
    run_testsuite_to_local()
    # run_testsuite_to_gcr()
    # This allows for both standalone execution and import without side effects.
