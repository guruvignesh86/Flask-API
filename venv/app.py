from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})    # Automatically adds CORS headers to all responses
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_login_signup'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/login', methods=['OPTIONS', 'POST'])
def login():
    if request.method == 'OPTIONS':    #request is  a attribute
        # Preflight request
        return _build_cors_prelight_response()
    elif request.method == 'POST':
        data = request.get_json()
       
        user = User.query.filter_by(username=data['username']).first()       # Searches the database for a user with the given username.
        if user and user.password == data['password']:      #If the user exists and the password matches, login is successful.
            return _corsify_actual_response(jsonify({"message": "Login successful"})), 200
        return _corsify_actual_response(jsonify({"message": "Invalid username or password"})), 200


#  response is a Flask Response object created by jsonify().
#  response.headers header is  a CORS  attribute interlinking with jsonify().
def _build_cors_prelight_response():
    response = jsonify({'message': 'CORS preflight'})
    response.headers.add('Access-Control-Allow-Origin', '*')    #* → Allows requests from any frontend vite,vue,vanilla.
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')   #→ Specifies which request methods are allowed.
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')  #Specifies which headers the frontend can use
    return response   #Send the response back to the browser

def _corsify_actual_response(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
# using jsonify is majorly because Sent to frontend/API clients 
@app.route('/signup', methods=['POST'])   #POST is a header
def signup():
    data = request.get_json()   #Retrieves JSON data sent in the request body. json to python dictionary
    new_user = User(username=data['username'], email=data['email'], password=data['password']) #Creates a new User object with the extracted username, email, and password.
    db.session.add(new_user)    # Adds the new user object to the database session
    db.session.commit()  #Saves the new user in the database
    return jsonify({"message": "User created"}), 201    #Converts Python dictionary → JSON response

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()  #retrieves all users from the database.

    users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]  #python dictionary
    return jsonify(users_list), 200 # Converts the list of users(users_list) into a JSON response.

@app.route('/add-user', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No data provided")  #ValueError is build in exception class
        
        print(f"Received data: {data}")  # Debug print
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')  #.get()?	✅ Prevents errors when a key is missing

        if not all([username, email, password]):
            raise ValueError("Missing data fields")
        
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({"message": "User added", "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}}), 201
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"message": "Failed to add user", "error": str(e)}), 400
    
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = User.query.get(id)
    if user:
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        db.session.commit()
        return jsonify({'message': 'User updated successfully!', 'user': {'id': user.id, 'username': user.username, 'email': user.email}})
    return jsonify({'message': 'User not found'}), 404

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully!'})




# @app.route('/users/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     print(f"Received request to delete user with ID: {user_id}")
#     user = User.query.get(user_id)
#     if user is None:
#         print("User not found")
#         return jsonify({"error": "User not found"}), 404

#     db.session.delete(user)
#     db.session.commit()

#     # Renumber IDs
#     users = User.query.order_by(User.id).all()
#     for index, user in enumerate(users):
#         user.id = index + 1
#     db.session.commit()

#     print("User deleted and IDs renumbered")
#     return jsonify({"message": "User deleted and IDs renumbered"}), 200




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)




















# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
# app.config['CORS_HEADERS'] = 'Content-Type'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_login_signup'

# db = SQLAlchemy(app)


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(80), unique=True, nullable=False)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

# @app.route('/login', methods=['OPTIONS', 'POST'])
# def login():
#     if request.method == 'OPTIONS':
#         # Preflight request
#         return _build_cors_prelight_response()
#     elif request.method == 'POST':
#         data = request.get_json()
#         user = User.query.filter_by(username=data['username']).first()
#         if user and user.password == data['password']:
#             return _corsify_actual_response(jsonify({"message": "Login successful"})), 200
#         return _corsify_actual_response(jsonify({"message": "Invalid username or password"})), 200

# def _build_cors_prelight_response():
#     response = jsonify({'message': 'CORS preflight'})
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
#     return response

# def _corsify_actual_response(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response

# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     new_user = User(username=data['username'], email=data['email'], password=data['password'])
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({"message": "User created"}), 201

# @app.route('/users', methods=['GET'])
# def get_users():
#     users = User.query.all()
#     users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
#     return jsonify(users_list), 200


# # @app.route('/users/<int:user_id>', methods=['DELETE'])
# # def delete_user(user_id):
# #     user = User.query.get(user_id)
# #     if user is None:
# #         return jsonify({"error": "User not found"}), 404

# #     db.session.delete(user)
# #     db.session.commit()

# #     # Renumber IDs
# #     users = User.query.order_by(User.id).all()
# #     for index, user in enumerate(users):
# #         user.id = index + 1
# #     db.session.commit()

# #     return jsonify({"message": "User deleted and IDs renumbered"}), 200

# @app.route('/users/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     print(f"Received request to delete user with ID: {user_id}")
#     user = User.query.get(user_id)
#     if user is None:
#         print("User not found")
#         return jsonify({"error": "User not found"}), 404

#     try:
#         db.session.delete(user)
#         db.session.commit()
#         print("User deleted successfully")

#         # Renumber IDs
#         users = User.query.order_by(User.id).all()
#         for index, user in enumerate(users):
#             user.id = index + 1
#         db.session.commit()
#         print("IDs renumbered")

#         return jsonify({"message": "User deleted and IDs renumbered"}), 200
#     except Exception as e:
#         print(f"Error deleting user: {e}")
#         return jsonify({"error": "Internal server error"}), 500




# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)










# @app.route('/users/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     user = User.query.get(user_id)
#     if user is None:
#         return jsonify({"error": "User not found"}), 404

#     db.session.delete(user)
#     db.session.commit()
#     return jsonify({"message": "User deleted"}), 200

 
    




# @app.route('/users', methods=['GET'])
# def get_users():
#     users = User.query.all()
#     users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
#     return jsonify(users_list), 200
























# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS

# app = Flask(__name__)
# # CORS(app)
# CORS(app, resources={r"/*": {"origins": "*"}})

# app.config['CORS_HEADERS'] = 'Content-Type'

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/flask_login_signup'
# db = SQLAlchemy(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(80), unique=True, nullable=False)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

# # CURRENTLY USING
# # @app.route('/login', methods=['POST'])
# # def login():
# #     data = request.get_json()
# #     user = User.query.filter_by(username=data['username']).first()
# #     if user:
# #         return jsonify({"message": "Login successful"}), 200
# #     return jsonify({"message": "User not found"}), 404

# @app.route('/login', methods=['OPTIONS', 'POST'])
# def login():
#     if request.method == 'OPTIONS':
#         # Preflight request
#         return _build_cors_prelight_response()
#     elif request.method == 'POST':
#         data = request.get_json()
#         user = User.query.filter_by(username=data['username']).first()
#         if user and user.password == data['password']:
#             return _corsify_actual_response(jsonify({"message": "Login successful"})), 200
#         return _corsify_actual_response(jsonify({"message": "Invalid username or password"})),200 

# def _build_cors_prelight_response():
#     response = jsonify({'message': 'CORS preflight'})
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
#     return response

# def _corsify_actual_response(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     return response











# # @app.route('/login', methods=['POST'])
# # def login():
# #     data = request.get_json()
# #     user = User.query.filter_by(username=data['username']).first()
# #     if user and user.password == data['password']:
# #         return jsonify({"message": "Login successful"}), 200
# #     return jsonify({"message": "Invalid username or password"}), 401



# @app.route('/signup', methods=['POST'])
# def signup():
#     data = request.get_json()
#     new_user = User(username=data['username'], email=data['email'], password=data['password'])
#     db.session.add(new_user)
#     db.session.commit()
#     return jsonify({"message": "User created"}), 201

# from flask import Flask, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# @app.route('/users/<int:user_id>', methods=['DELETE'])
# def delete_user(user_id):
#     user = User.query.get(user_id)
#     if user is None:
#         return jsonify({"error": "User not found"}), 404

#     db.session.delete(user)
#     db.session.commit()

#     return jsonify({"message": "User deleted"}), 200

# @app.route('/users', methods=['GET'])
# def get_users():
#     users = User.query.all()
#     users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
#     return jsonify(users_list), 200







# # @app.route('/users', methods=['GET'])
# # def get_users():
# #     users = User.query.all()
# #     user_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
# #     return jsonify(user_list), 200

# # @app.route('/users/<int:user_id>', methods=['DELETE'])
# # def delete_user(user_id):
# #     user = User.query.get(user_id)
# #     if user is None:
# #         return jsonify({"error": "User not found"}), 404

# #     db.session.delete(user)
# #     db.session.commit()

# #     # Renumber IDs
# #     users = User.query.order_by(User.id).all()
# #     for index, user in enumerate(users):
# #         user.id = index + 1
# #     db.session.commit()

# #     return jsonify({"message": "User deleted"}), 200


# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
