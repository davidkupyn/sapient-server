from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS
from dotenv import load_dotenv
import openai
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

@app.route('/schools', methods=['GET'])
def schools():
    conn = psycopg2.connect(database=database, 
                            user=user,
                            password=password, 
                            host=host, 
                            port=port)
    
    cur = conn.cursor()

    cur.execute('SELECT id, name, LEFT(school_description, 100) AS school_description, city, phone FROM schools')
  
    data = cur.fetchall()
  
    cur.close()
    conn.close()
    
    return jsonify(data)

@app.route('/school/<string:school_id>', methods=['GET'])
def get_school(school_id):
    conn = psycopg2.connect(database=database, 
                            user=user,
                            password=password, 
                            host=host, 
                            port=port)
    
    cur = conn.cursor()

    cur.execute(f"SELECT name, address, city, www, email, facebook, phone, school_description, recrutation_description, subjects FROM schools WHERE id = {school_id}")
  
    data = cur.fetchall()
  
    cur.close()
    conn.close()
    
    return data

@app.route('/search', methods=['GET'])
def ai_api():

    q = request.args.get('q')

    if q == None:
        return jsonify({"error": "No query provided"})
    
    if "biol-chem" in q:

        prompt = "Biologia & Lublin & Chemia"
        conn = psycopg2.connect(database=database, 
                            user=user,
                            password=password, 
                            host=host, 
                            port=port)
    
        cur = conn.cursor()

        cur.execute(f"SELECT id, name, city, LEFT(school_description, 100) AS school_description, voivodeship FROM schools WHERE ts_vector @@ to_tsquery('{prompt}')")
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data)
    
    elif "technik informatyk" in q:


        prompt = "Informatyka & Warszawa"
        conn = psycopg2.connect(database=database, 
                            user=user,
                            password=password, 
                            host=host, 
                            port=port)
    
        cur = conn.cursor()

        cur.execute(f"SELECT id, name, city, LEFT(school_description, 100) AS school_description, voivodeship FROM schools WHERE ts_vector @@ to_tsquery('{prompt}')")
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data)
    
    elif "architektura" in q or "firmę budowlaną" in q:

        prompt = "architektura"
        conn = psycopg2.connect(database=database,
                            user=user,
                            password=password,
                            host=host,
                            port=port)
        cur = conn.cursor()

        cur.execute(f"SELECT id, name, city, LEFT(school_description, 100) AS school_description, voivodeship FROM schools WHERE ts_vector @@ to_tsquery('{prompt}')")
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data)

    if q.__len__() < 50:
        conn = psycopg2.connect(database=database, 
                            user=user,
                            password=password, 
                            host=host, 
                            port=port)
    
        cur = conn.cursor()

        transformed_response = q.replace(" ", " & ")
        cur.execute(f"SELECT id, name, city, LEFT(school_description, 100) AS school_description, voivodeship FROM schools WHERE ts_vector @@ to_tsquery('{transformed_response}')")
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data)
    
    else:
        gpt_prompt_schema = "NA SAMYM POCZĄTKU PRZETŁUMACZ PODANY TEKST NA JĘZYK POLSKI następnie Przetransformuj odpowiedź użytkownika, tak aby była zdatna do użycia w wyszukiwarce. Musisz ocenić zdolności użytkownika, jego mocne i słabe strony oraz to, co opowie o sobie, aby znaleźć dla niego idealny kierunek studiów. Jeżeli wspomni coś o lokalizacji, uwzględnij to. Prompt do wyszukiwarki, który masz za zadanie napisać, musi być krótki i zawierać kluczowe słowa. Przykład: Użytkownik napisał: 'Uwielbiam informatykę! Od urodzenia jestem umysłem ścisłym, jednak nie mogę się zdecydować nad studiami. Chciałbym zostać w moim rodzinnym mieście - Warszawie.' Twoja odpowiedź powinna brzmieć: 'Informatyka Warszawa.' PAMIĘTAJ, ABY OGRANICZYĆ SIĘ DO KILKU (max 3) KLUCZOWYCH SŁÓW KTÓRE POMOGĄ OSOBIE OPISUJĄCEJ ZNALEŹĆ IDEALNY PROFIL STUDENCKI!!! Twój opis do analizy to: "
        gpt_prompt_end = "MAKSYMALNA ILOŚĆ SŁÓW KLUCZOWYCH DO UŻYCIA TO 3. ODWOŁUJ SIĘ JEDYNIE DO PRZYSZYŁYCH STUDIÓW A NIE PRACY, unikaj przecinków i kropek, pamiętaj o podaniu lokalizacji jeśli użytkownik ją uwzględnił."

        gpt_prompt = gpt_prompt_schema + q + gpt_prompt_end

        openai.api_key = os.getenv("OPENAI_API_KEY")
        messages = [{"role": "user", "content": gpt_prompt}] 
        chat = openai.ChatCompletion.create( 
            model="gpt-3.5-turbo", 
            messages=messages, 
            temperature=0.1, 
        )

        response = chat["choices"][0]["message"]["content"]

        print(response)

        conn = psycopg2.connect(database=database, 
                                user=user,
                                password=password, 
                                host=host, 
                                port=port)
        
        cur = conn.cursor()
    
        transformed_response = response.replace(" ", " & ").replace(".", "")

        print(transformed_response)

        cur.execute(f"SELECT id, name, city, LEFT(school_description, 100) AS school_description, voivodeship FROM schools WHERE ts_vector @@ to_tsquery('{transformed_response}')")
        data = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
