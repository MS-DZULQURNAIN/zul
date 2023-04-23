import os
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
   return 'Hello, World!'
   

os.system("git clone https://Onlymeriz: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@github.com/Onlymeriz/Kynan && cd Kynan && pip3 install -r requirements.txt && bash start")