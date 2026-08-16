from flask import Flask, render_template,request
import gspread, json, base64
from datetime import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv



load_dotenv()


CREDS = json.loads(base64.b64decode(os.environ["CREDS"]))
DOCUMENT_ID = os.environ["DOCUMENT_ID"]
SOURCE_DOC_ID = os.environ["SOURCE_DOC_ID"]


sheet = gspread.service_account_from_dict(info=CREDS).open("DSA Accuracy Tracker").sheet1
docs = build('docs', 'v1', credentials=service_account.Credentials.from_service_account_info(info=CREDS)).documents()
source_doc = build('docs', 'v1', credentials=service_account.Credentials.from_service_account_info(info=CREDS)).documents().get(documentId=SOURCE_DOC_ID).execute()

body_content = source_doc.get('body', {}).get('content', [])


with open("questions.json") as file:
        data = json.load(file)
        file.close()

questions_by_phases = [phase["questions"] for phase in data["phases"]]

questions = {}

for question in questions_by_phases:
     for q in question:
          questions[q["id"]] = q["marks"]



app = Flask(__name__)



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
    inputTime = data["inputTime"]

    marks = [questions[id] if id in checked else 0 for id in range(1,13)]

    if url=="" or name=="" or inputTime=="":
        return {"status":400}
    
    rows = sheet.get_all_values()

    date = datetime.now().strftime("%d %b %Y, %a")

    row = [date,name,url,difficulty,inputTime,percent,*marks]

    if row in rows:
        return {"status":400}
    
    sheet.append_row(row)

    requests = []

    requests.append({
        'insertPageBreak': {
            'location': {
                'index': 1
            }
        }
    })

    current_index = 1 

    for element in body_content:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            paragraph_style = paragraph.get('paragraphStyle', {})
            elements = paragraph.get('elements', [])
            bullet_info = paragraph.get('bullet', None)
            
            paragraph_start_index = current_index
            paragraph_length = 0
            
            for el in elements:
                if 'textRun' in el:
                    text_run = el['textRun']
                    text_content = text_run.get('content', '')
                    text_style = text_run.get('textStyle', {})
                    
                    if not text_content:
                        continue
                    
                    requests.append({
                        'insertText': {
                            'location': {'index': current_index},
                            'text': text_content
                        }
                    })
                    
                    end_idx = current_index + len(text_content)
                    if 'link' in text_style and 'url' in text_style['link']:
                        link_url = text_style['link']['url']
                        text_style['link'] = {'url': link_url}

                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': current_index,
                                'endIndex': end_idx
                            },
                            'textStyle': text_style,
                            'fields': '*'
                        }
                    })
                    
                    current_index += len(text_content)
                    paragraph_length += len(text_content)
            
            if paragraph_length > 0:
                if paragraph_style:
                    paragraph_style.pop('headingId', None)
                    requests.append({
                        'updateParagraphStyle': {
                            'range': {
                                'startIndex': paragraph_start_index,
                                'endIndex': paragraph_start_index + paragraph_length
                            },
                            'paragraphStyle': paragraph_style,
                            'fields': '*'
                        }
                    })
                    
                if bullet_info:
                    requests.append({
                        'createParagraphBullets': {
                            'range': {
                                'startIndex': paragraph_start_index,
                                'endIndex': paragraph_start_index + paragraph_length
                            },
                            'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                        }
                    })


    requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': name + "\n"
            }
        })

    
    requests.append({
            'insertText': {
                'location': {'index': len(name) + 10},
                'text': date
            }
        })


    requests.append({
        'updateTextStyle': {
            'range': {
                'startIndex': len(name) + 10,
                'endIndex': len(name) + 10 + len(date)
            },
            'textStyle': {
                'bold': False,
                'italic': False,
                'underline': False,
                'strikethrough': False,
            },
            'fields': 'bold,italic,underline,strikethrough'
        }
    })


    requests.append({
        'updateTextStyle': {
            'range': {
                'startIndex': 1,
                'endIndex': len(name) + 1   
            },
            'textStyle': {
                'link': {
                    'url': url  
                },
                'underline': False,
                'foregroundColor': {
                    'color': {
                        'rgbColor': {
                            'blue': 0.8, 
                            'green': 0.3,
                            'red': 0.1
                        }
                    }
                }
            },
            'fields': 'link,underline,foregroundColor'
        }
    })


    docs.batchUpdate(documentId=DOCUMENT_ID, body={'requests': requests}).execute()

    return {"status":200}