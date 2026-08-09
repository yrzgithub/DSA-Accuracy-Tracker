from flask import Flask, render_template,request
import gspread, json
from datetime import datetime
import os



app = Flask(__name__)
sheet = gspread.service_account(filename='credentials.json').open("DSA Accuracy Tracker").sheet1



@app.route("/")
def index():
    #with open("questions.json") as file:
    #    data = json.load(file)
    #    file.close()

    return render_template("index.html", rubric=os.environ.get("CREDS"))



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



if __name__ == "__main__":
    app.run(debug=True)