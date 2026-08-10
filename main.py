from flask import Flask, render_template,request
import gspread, json, base64
from datetime import datetime
import os
from dotenv import load_dotenv



load_dotenv()


app = Flask(__name__)
sheet = gspread.service_account_from_dict(info=json.loads(base64.b64decode(os.environ["CREDS"]))).open("DSA Accuracy Tracker").sheet1


with open("questions.json") as file:
        data = json.load(file)
        file.close()


questions_by_phases = [phase["questions"] for phase in data["phases"]]

questions = {}

for question in questions_by_phases:
     for q in question:
          questions[q["id"]] = q["marks"]



@app.route("/")
def index():
    return render_template("index.html", rubric=data)



@app.route("/updatekeep",methods=["POST"])
def updateKeep():
    data = json.loads(request.get_data(as_text=True))

    url = data["url"]
    name = data["name"]
    difficulty = data["difficulty"]
    percent = data["percent"]
    checked = set(map(lambda e : int(e),data["checked"]))

    marks = [questions[id] if id in checked else 0 for id in range(1,13)]

    if url=="" or name=="":
        return {}
    
    rows = sheet.get_all_values()

    row = [datetime.now().strftime("%d %b %Y, %a"),name,url,difficulty,percent,*marks]

    if row in rows:
        return {"status":400}
    
    sheet.append_row(row)

    return {"status":200}