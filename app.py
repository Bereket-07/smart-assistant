import os
from flask import Flask,request,jsonify
from dotenv import load_dotenv
from models import db
from ai import chat_with_groq


# Load environment variables
load_dotenv()
# initialize flask app
app = Flask(__name__)


# set a secret key for session management
app.secret_key = os.getenv("FLASK_SECRET_KEY","default_secret_key")

# database configuration

db_config = {
    'host':os.getenv('DB_HOST','localhost'),
    'user':os.getenv('DB_USER','root'),
    'password':os.getenv('DB_PASSWORD'),
    'database':os.getenv('DB_NAME','analytics')
}

# database connection 
app.config['SQLALCHEMY_DATABASE_URI']=f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

#  Initialize SQLAlchemy

db.init_app(app)

@app.route('/chat', methods=['POST'])
def chat():
    quetioner_id = request.json.get('id')
    language = request.json.get('language')
    user_message = request.json.get('message')
    chat_response = chat_with_groq(user_message,quetioner_id,language)
    return jsonify({"response": chat_response})

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug_mode)