import os
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
   return 'Hello, World!'
   

os.system("git clone https://github.com/DjeFaris/ritoprivat Kynan && cd Kynan && pip3 install -r requirements.txt && bash start")
