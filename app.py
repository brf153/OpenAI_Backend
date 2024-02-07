import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from langchain_community.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain_openai import ChatOpenAI
from openai import OpenAI

app = Flask(__name__)
CORS(app)

# Retrieve environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Use the environment variable
print(f"OpenAI API Key: {OPENAI_API_KEY}")

clientAI = OpenAI(api_key=OPENAI_API_KEY)

# Decorator to check if the authentication token is provided in the header
def authenticate(func):
    def wrapper(*args, **kwargs):
        authorization_header = request.headers.get("Authorization")
        print(f"Authorization Header: {authorization_header}")
        if request.headers.get("Authorization") == "Bearer secret_token":
            return func(*args, **kwargs)
        else:
            abort(401, description="Unauthorized")
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello, World!'

@app.route('/api/product', methods=['POST'])
@authenticate
def store_product():
    try:
        product_data = request.json.get('product')
        product_id = request.json.get('id')

        if not product_data:
            abort(400, description="Missing 'product' key in the JSON payload")


        if os.path.exists(f'{product_id}.txt'):
            return jsonify({"message": "Product already exists!"}), 200

        print("Received a request to store the content in a temporary file.", product_data)

        with open(f'{product_id}.txt', 'w', encoding='utf-8') as file:
            file.write(product_data)

        return jsonify({"message": "Received the product data successfully"})

    except Exception as e:
        print(f"Error processing the product data: {e}")
        return jsonify({"error": str(e)}), 500

# POST endpoint
@app.route('/api/chat', methods=['POST'])
@authenticate
def add_item():
    try:
        if 'message' not in request.json:
            return jsonify({"error": "Missing 'message' key in the JSON payload"}), 400

        item = request.json['message']
        product_id = request.json.get('id')

        loader = TextLoader(f'{product_id}.txt')
        index = VectorstoreIndexCreator().from_loaders([loader])

        return jsonify({"message": index.query(item, llm=ChatOpenAI())})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Remove endpoint
@app.route('/api/product/remove', methods=['GET'])
@authenticate
def remove_item():
    try:
        if os.path.exists('data.txt'):
            os.remove('data.txt')

        return jsonify({"message": "Removed the data!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
