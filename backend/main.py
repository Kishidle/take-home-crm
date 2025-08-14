from fastapi import FastAPI, File, UploadFile
from io import StringIO
from pyisemail import is_email
from dotenv import load_dotenv
from hubspot import HubSpot
from hubspot.crm.contacts import SimplePublicObjectInputForCreate
from hubspot.crm.contacts.exceptions import ApiException
import faker
import csv
import phonenumbers
import random as r

import os
f = faker.Faker()
app = FastAPI()
api_client = HubSpot(access_token=os.getenv("API_KEY"))
load_dotenv()
url = "https://api.hubapi.com/crm/v3/objects/leads/batch/create"
headers = {
  'accept': 'application/json',
  'content-type': 'application/json',
  'authorization': f'Bearer {os.getenv("API_KEY")}'
}
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
  data = {}
  file_bytes = file.file.read()
  buffer = StringIO(file_bytes.decode("utf-8"))

  reader = csv.DictReader(buffer)
  
  for row in reader: 
    data[row["name"]] = row["name"]
    data[row["email"]] = row["email"]
    data[row["company"]] = row["company"]
    data[row["phone"]] = row["phone"]
  
  return data

def generate_random_phone_number():
  phone_number = "+44"
  for _ in range(10):
    phone_number += str(r.randint(0, 9))
  return phone_number

@app.get("/test")
async def test():
  file_name="generated.csv"
  with open(file_name) as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=",")
    column_names = csv_reader.fieldnames
    print(f"Starting import of leads from {file_name}")
    leads = []
    for index, row in enumerate(csv_reader):
      print(f"Importing lead {index}")
      new_lead = {}
      for column_name in column_names:
        new_lead[column_name] = row[column_name]

      #validate data
      if not is_email(new_lead["email"]):
        print(f"Found an invalid email: {new_lead['email']}")
        continue
      #TODO: change to is_valid?
      if not phonenumbers.is_possible_number(phonenumbers.parse(new_lead["phone"], None)):
        print(f"Found an invalid phone number: {new_lead['phone']}")
        continue
      if not new_lead["company"]:
        print("Missing required field: company")
        continue
      if not new_lead["name"]:
        print("Missing required field: name")
        continue

      #split name into first_name, last_name
      name = new_lead["name"].split(" ")
      if len(name) > 2:
        # check if first name is a title/has a period
        if "." in name[0]:
          new_lead["firstname"] = name[1]
          new_lead["lastname"] = name[2]
        else:
          # name possibly has middle name, join first and middle
          new_lead["firstname"] = name[0] + " " + name[1]
          new_lead["lastname"] = name[2]
      else :
        new_lead["firstname"] = name[0]
        new_lead["lastname"] = name[1]
      #create lead on hubspot
      try:
        simple_object = SimplePublicObjectInputForCreate(
          properties={
            "firstname": new_lead["firstname"],
            "lastname": new_lead["lastname"],
            "email": new_lead["email"],
            "company": new_lead["company"],
            "phone": new_lead["phone"]
          }
        )
        response = api_client.crm.contacts.basic_api.create(simple_public_object_input_for_create=simple_object)
      except ApiException as e:
        print("Exception when creating contact: %s\n" % e)
      #push to data array
      # leads.append({
      #   "properties": [
      #     {
      #       "property": "name",
      #       "value": new_lead["name"]
      #     },
      #     {
      #       "property": "email",
      #       "value": new_lead["email"]
      #     },
      #     {
      #       "property": "company",
      #       "value": new_lead["company"]
      #     },
      #     {
      #       "property": "phone",
      #       "value": new_lead["phone"]
      #     }
      #   ]
      # })
      
      #print(data) 

    # response = requests.post(url, headers=headers, json={"inputs": leads})

  return {"message": "Hello World"}

@app.post("/generate")
async def generate():
  file_name="generated.csv"
  with open(file_name, "w", newline=""):
    writer = csv.writer(open(file_name, "w", newline=""))
    writer.writerow(["name", "email", "company", "phone"])
    for _ in range(100):
      name = f.name()
      email = f.email()
      company = f.company()
      phone = generate_random_phone_number()
      writer.writerow([name, email, company, phone])
  return {"message": "Successfully generated file"}