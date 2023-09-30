from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"*": {"origins": "*"}})

database = os.getenv("DATABASE")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")

@app.route('/')
def index():
    return jsonify({"Choo Choo": "Welcome to your Flask app 🚅"})

@app.route('/search/<string:q>', methods=['GET'])
def search():
    # conn = psycopg2.connect(database=database,
    #                         user=user,
    #                         password=password,
    #                         host=host,
    #                         port=port)
    
    q = request.args.get('q')
    
    # cur = conn.cursor()

    return jsonify({"q": q})

@app.route('/schools', methods=['GET'])
def schools():
    conn = psycopg2.connect(database=database, 
                            user=user,
                            password=password, 
                            host=host, 
                            port=port)
    
    cur = conn.cursor()

    cur.execute('SELECT name FROM schools')
  
    data = cur.fetchall()
  
    cur.close()
    conn.close()
    
    return data

@app.route('/school/<string:school_id>', methods=['GET'])
def get_school(school_id):
    conn = psycopg2.connect(database=database, 
                            user=user,
                            password=password, 
                            host=host, 
                            port=port)
    
    cur = conn.cursor()

    cur.execute(f"SELECT name, address, city, www, email, facebook, phone, school_description, recrutation_description FROM schools WHERE school_id = {school_id}")
  
    data = cur.fetchall()
  
    cur.close()
    conn.close()
    
    return data


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
