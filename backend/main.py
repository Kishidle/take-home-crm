from fastapi import FastAPI, File, UploadFile
from io import StringIO
from pyisemail import is_email
import faker
import csv
import phonenumbers
import random as r
f = faker.Faker()
app = FastAPI()

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
    for index, row in enumerate(csv_reader):
      print(f"Importing lead {index}")
      data = {}
      for column_name in column_names:
        data[column_name] = row[column_name]

      #validate data
      if not is_email(data["email"]):
        print(f"Found an invalid email: {data['email']}")
        continue
      #TODO: change to is_valid?
      if not phonenumbers.is_possible_number(phonenumbers.parse(data["phone"], None)):
        print(f"Found an invalid phone number: {data['phone']}")
        continue
      if not data["company"]:
        print("Missing required field: company")
        continue
      if not data["name"]:
        print("Missing required field: name")
        continue
      
      #print(data)

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