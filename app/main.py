from flask import Flask, render_template,request
import gspread, json, base64
from datetime import datetime
import os
from dotenv import load_dotenv



load_dotenv()


app = Flask(__name__)
sheet = gspread.service_account_from_dict(info=json.loads(base64.b64decode(os.environ["CREDS"]))).open("DSA Accuracy Tracker").sheet1



@app.route("/")
def index():
    with open("questions.json") as file:
        data = json.load(file)
        file.close()

    return render_template("index.html", rubric=data)



@app.route("/updatekeep",methods=["POST"])
def updateKeep():
    data = json.loads(request.get_data(as_text=True))

    url = data["url"]
    name = data["name"]
    difficulty = data["difficulty"]
    percent = data["percent"]

    if url=="" or name=="":
        return {}
    
    rows = sheet.get_all_values()

    row = [datetime.now().strftime("%d %b %Y, %a"),name,url,difficulty,percent]

    if row in rows:
        return {"status":400}
    
    sheet.append_row(row)

    return {"status":200}