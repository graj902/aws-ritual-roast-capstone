from flask import Flask, jsonify, request, send_from_directory
import mysql.connector
import os
from flask_cors import CORS
import boto3
import json

def get_mysql_database_secrets():
    session = boto3.Session()
    client = session.client(service_name="secretsmanager", region_name="[Region]")

    get_secret_value_response = client.get_secret_value(SecretId="[Your Secret Name]")
    SecretString = json.loads(get_secret_value_response["SecretString"])

    DESTINATION_DB_HOST = SecretString["host"]
    DESTINATION_DB_USERNAME = SecretString["username"]
    DESTINATION_DB_PASSWORD = SecretString["password"]
    DESTINATION_DATABASE = SecretString["dbname"]
    DESTINATION_DB_PORT = SecretString["port"]

    return [DESTINATION_DB_HOST, DESTINATION_DB_USERNAME, DESTINATION_DB_PASSWORD, DESTINATION_DATABASE, DESTINATION_DB_PORT]


app = Flask(
    __name__,
    static_folder="ritual_roast/build/static",
    template_folder="ritual_roast/build"
)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize secrets and DB connection
secrets = get_mysql_database_secrets()

connection = mysql.connector.connect(
    host=secrets[0],
    user=secrets[1],
    password=secrets[2],
    database=secrets[3],
    port=secrets[4]
)
cursor = connection.cursor()

# Create the recipes table if it doesn't exist
query = """
CREATE TABLE IF NOT EXISTS recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    recipe_name VARCHAR(255) NOT NULL,
    description TEXT,
    ingredients TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(query)
connection.commit()

def check_and_reconnect():
    global connection, cursor
    try:
        connection.ping(reconnect=True, attempts=3, delay=2)
    except mysql.connector.Error:
        print("Database connection lost. Fetching updated credentials and reconnecting...")
        secrets = get_mysql_database_secrets()
        connection = mysql.connector.connect(
            host=secrets[0],
            user=secrets[1],
            password=secrets[2],
            database=secrets[3],
            port=secrets[4]
        )
        cursor = connection.cursor()


@app.route('/get_recipe', methods=['GET'])
def get_recipes():
    check_and_reconnect()
    query = "SELECT * FROM recipes ORDER BY id DESC;"
    cursor.execute(query)
    rows = cursor.fetchall()

    recipes = []
    for row in rows:
        recipe = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'recipe_name': row[3],
            'description': row[4],
            'ingredients': row[5],
            'created_at': str(row[6])
        }
        recipes.append(recipe)
    return jsonify(recipes)


@app.route('/add_recipe', methods=['POST'])
def add_recipe():
    check_and_reconnect()
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    recipe_name = data.get('recipe_name')
    description = data.get('description')
    ingredients = data.get('ingredients')

    query = """
        INSERT INTO recipes (name, email, recipe_name, description, ingredients)
        VALUES (%s, %s, %s, %s, %s);
    """
    cursor.execute(query, (name, email, recipe_name, description, ingredients))
    connection.commit()

    return jsonify({'message': 'Recipe added successfully'}), 201


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    print(f"Requested path: {path}")
    static_file_path = os.path.join(app.static_folder, path)
    template_file_path = os.path.join(app.template_folder, path)

    if path and os.path.exists(static_file_path):
        print(f"Serving static file: {static_file_path}")
        return send_from_directory(app.static_folder, path)

    if path and os.path.exists(template_file_path):
        print(f"Serving template file: {template_file_path}")
        return send_from_directory(app.template_folder, path)

    index_file = os.path.join(app.template_folder, "index.html")
    if os.path.exists(index_file):
        print(f"Serving React index.html: {index_file}")
        return send_from_directory(app.template_folder, "index.html")

    print("Error: React index.html not found!")
    return "Error: index.html not found!", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
