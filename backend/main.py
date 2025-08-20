from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from io import StringIO
from pyisemail import is_email
from dotenv import load_dotenv
from hubspot import HubSpot
from hubspot.crm.contacts import (
    BatchInputSimplePublicObjectBatchInputForCreate as Batch,
)
from hubspot.crm.contacts.exceptions import ApiException
import faker
import csv
import phonenumbers
import random as r
import requests
import os
import json
import time

f = faker.Faker()
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv()
api_client = HubSpot(access_token=os.getenv("API_KEY"))
url = "https://api.hubapi.com/crm/v3/objects/leads/batch/create"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f'Bearer {os.getenv("API_KEY")}',
}


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    start_time = time.perf_counter()
    file_bytes = file.file.read()
    buffer = StringIO(file_bytes.decode("utf-8"))

    reader = csv.DictReader(buffer)

    contacts_to_import = []
    contacts = []
    column_names = reader.fieldnames
    error_count = 0
    duplicate_count = 0
    for index, row in enumerate(reader):
        print(f"Importing contact {index + 1}...")
        new_contact = {}
        for column_name in column_names:
            new_contact[column_name] = row[column_name]

        # validate data
        if not is_email(new_contact["email"]):
            print(f"Found an invalid email: {new_contact['email']}")
            continue
        # TODO: change to is_valid?
        if not phonenumbers.is_possible_number(
            phonenumbers.parse(new_contact["phone"], None)
        ):
            print(f"Found an invalid phone number: {new_contact['phone']}")
            error_count += 1
            continue
        if not new_contact["company"]:
            print("Missing required field: company")
            error_count += 1
            continue
        if not new_contact["name"]:
            print("Missing required field: name")
            error_count += 1
            continue
        # if not new_contact["lead_type"]:
        #     # add default lead_type
        #     new_contact["lead_type"] = "NEW_BUSINESS"
        # if not new_contact["lead_label"]:
        #     # add default lead_label
        #     new_contact["lead_label"] = "HOT"

        # check if email already exists as a contact in Hubspot
        try:
            email_response = api_client.crm.contacts.basic_api.get_by_id(
                contact_id=new_contact["email"], id_property="email", archived=False
            )
            if email_response:
                print(f"Email already exists: {new_contact['email']} as a contact")
                duplicate_count += 1
                error_count += 1
            continue
        except ApiException as e:
            # email not found, do nothing
            pass

        # check if email already exists in contacts list
        if [
            contact for contact in contacts if contact["email"] == new_contact["email"]
        ]:
            print(f"Email already exists: {new_contact['email']} in contacts list")
            duplicate_count += 1
            error_count += 1
            continue

        # split name into first_name, last_name
        name = new_contact["name"].split(" ")
        if len(name) > 2:
            # check if first name is a title/has a period
            if "." in name[0]:
                new_contact["firstname"] = name[1]
                new_contact["lastname"] = name[2]
            else:
                # name possibly has middle name, join first and middle
                new_contact["firstname"] = name[0] + " " + name[1]
                new_contact["lastname"] = name[2]
        else:
            new_contact["firstname"] = name[0]
            new_contact["lastname"] = name[1]

        # create contact first
        contact = {
            "associations": None,
            "properties": {
                "firstname": new_contact["firstname"],
                "lastname": new_contact["lastname"],
                "email": new_contact["email"],
                "company": new_contact["company"],
                "phone": new_contact["phone"],
            },
        }

        contacts.append(new_contact)
        contacts_to_import.append(contact)

    # batch create of contacts
    batch_input = Batch(inputs=contacts_to_import)
    try:

        response = api_client.crm.contacts.batch_api.create(batch_input)

        print(f"Successfully created {len(response.results)} contacts")
    except ApiException as e:
        print("An error occurred during contact batch creation: %s\n" % e)
        return {"message": "Error creating contacts", "status": "fail"}

    # build dictionary of all contacts by email
    # the assumption is that all emails are unique
    print("Building contact dictionary...")
    #contact_dict = build_dict(contacts, key_func=lambda d: d["email"])
    contact_dict = { contact["email"]: contact for contact in contacts }
    leads = []
    print("Creating batch of leads...")

    # convert hubspot object to dict
    hub_contact_dict = []
    for contact in response.results:
        hub_contact_dict.append(contact.to_dict())

    # create leads
    for result in hub_contact_dict:
        contact_info = contact_dict.get(result["properties"]["email"])

        if contact_info:
            leads.append(
                {
                    "associations": [
                        {
                            "types": [
                                {
                                    "associationCategory": "HUBSPOT_DEFINED",
                                    "associationTypeId": 578,
                                }
                            ],
                            "to": {
                                "id": result["id"],
                            },
                        }
                    ],
                    "properties": {
                        "hs_lead_name": contact_info["firstname"]
                        + " "
                        + contact_info["lastname"],
                        # "hs_lead_type": contact_info["lead_type"],
                        # "hs_lead_label": contact_info["lead_label"],
                    },
                }
            )
        else:
            print(f"No contact found for email: {result.properties.email}")

    try:
        lead_response = requests.request(
            "POST", url, data=json.dumps({"inputs": leads}), headers=headers
        )
        print(f"Successfully created {len(lead_response.json()['results'])} leads")
    except Exception as e:
        print("An error occurred during lead batch creation: %s\n" % e)
        return {"message": "Error creating leads", "status": "fail"}

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Contact and lead creation took {(end_time - start_time):.4f} seconds")
    return {
        "message": "Contact and leads created successfully on Hubspot",
        "runtime": elapsed_time,
        "totalContacts": len(contacts),
        "totalErrors": error_count,
        "duplicatesSkipped": duplicate_count,
        "status": "success",
    }


def generate_random_phone_number():
    phone_number = "+44"
    for _ in range(10):
        phone_number += str(r.randint(0, 9))
    return phone_number

@app.post("/generate")
async def generate():
    file_name = "generated.csv"
    with open(file_name, "w", newline=""):
        writer = csv.writer(open(file_name, "w", newline=""))
        writer.writerow(
            ["name", "email", "company", "phone"]
        )
        for _ in range(100):
            name = f.name()
            email = f.email()
            company = f.company()
            phone = generate_random_phone_number()
            # lead_type = r.choice(["NEW_BUSINESS", "UPSELL", "RE_ATTEMPTING"])
            # lead_label = r.choice(["HOT", "WARM", "COLD"])
            writer.writerow([name, email, company, phone])
    return {"message": "Successfully generated file"}
