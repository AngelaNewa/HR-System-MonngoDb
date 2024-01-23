import hashlib
import datetime
import json
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson import json_util
app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1) # login auth token expires

client = MongoClient("mongodb+srv://kuljeet:Stkh%401895@cluster0.br7v5ml.mongodb.net/") # Data Connection
db = client["hr_system"]
users_collection = db["users"]
staff_data = db["staff"]
student_data = db["student"]
# register api but will not be needed in main project

@app.route("/register", methods=["POST"])
def register():
	new_user = request.get_json() # store the json body request
	new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest() # encrpt password
	doc = users_collection.find_one({"username": new_user["username"]}) # check if user exist
	if not doc:
		users_collection.insert_one(new_user)
		return jsonify({'msg': 'User created successfully'}), 201
	else:
		return jsonify({'msg': 'Username already exists'}), 409
	

#login api

@app.route("/login", methods=["POST"])
def login():
	login_details = request.get_json() # store the json body request
	user_from_db = users_collection.find_one({'username': login_details['username']})  # search for user in database

	if user_from_db:
		encrpted_password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()
		if encrpted_password == user_from_db['password']:
			access_token = create_access_token(identity=user_from_db['username']) # creating jwt token
			return jsonify(access_token=access_token), 200

	return jsonify({'msg': 'The username or password is incorrect'}), 401


# @app.route("/staff/", methods=["GET"])
# @jwt_required
# def staff():
# 	current_user = get_jwt_identity() # Get the identity of the current user
# 	user_from_db = users_collection.find_one({'username' : current_user})
# 	if user_from_db:
# 		del user_from_db['_id'], user_from_db['password'] # delete data we don't want to return
# 		return jsonify({'staff' : user_from_db }), 200
# 	else:
# 		return jsonify({'msg': 'Profile not found'}), 404
	

def validate_staff_data(data):
    required_fields = [
        "first_name", "last_name", "date_of_birth", "email", "phone", "street",
        "city", "state", "postal_code", "department", "position", "start_date",
        "salary", "employment_status", "dbs_id"
    ]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Additional validation checks can be added here
    # For example, you can check if email is a valid email address, if phone is a valid phone number, etc.

    return True, None


@app.route('/get_staff', methods=['GET'])
def get_all_staff():
    try:
        staff = list(staff_data.find())

        if staff:
            # Return staff data as a response
            response = {
                "status": "success",
                "data": staff
            }
            return json.loads(json_util.dumps(response)), 200
        else:
            response = {
                "status": "error",
                "message": "No Data found"
            }
            return jsonify(response), 404

    except Exception as e:
        # Handle any exceptions that may occur
        response = {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }
        return jsonify(response), 500
    
@app.route('/add_staff', methods=['POST'])
def add_staff():
    
	
    try:
		
        # Extract data from the request JSON
        request_data = request.json

        # Validate the request data
        is_valid, validation_error = validate_staff_data(request_data)
        if not is_valid:
            response = {
                "status": "error",
                "message": validation_error
            }
            return jsonify(response), 400

        # Construct the new_staff document
        new_staff = {
            "first_name": request_data['first_name'],
            "last_name": request_data['last_name'],
            "date_of_birth": request_data['date_of_birth'],
            "email": request_data['email'],
            "phone": request_data['phone'],
            "street": request_data['street'],
            "city": request_data['city'],
            "state": request_data['state'],
            "postal_code": request_data['postal_code'],
            "department": request_data['department'],
            "position": request_data['position'],
            "start_date": request_data['start_date'],
            "salary": request_data['salary'],
            "employment_status": request_data['employment_status'],
            "dbs_id": request_data['dbs_id']
        }


        # Insert the new_staff document into the MongoDB collection
        result = staff_data.insert_one(new_staff)

        # Return the inserted document ID as a response
        response = {
            "status": "success",
            "message": "Staff added successfully",
            "staff_id": str(result.inserted_id)
        }
        return jsonify(response), 201

    except Exception as e:
        # Handle any exceptions that may occur during the insertion
        response = {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }
        return jsonify(response), 500

@app.route('/get_staff/<staff_id>', methods=['GET'])
def get_staff(staff_id):
    try:
        # Find staff by ID
        staff = staff_data.find_one({"_id": ObjectId(staff_id)})

        if staff:
            # Return staff data as a response
            response = {
                "status": "success",
                "data": staff
            }
            return json.loads(json_util.dumps(response)), 200 
        else:
            response = {
                "status": "error",
                "message": "Staff not found"
            }
            return jsonify(response), 404

    except Exception as e:
        # Handle any exceptions that may occur
        response = {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }
        return jsonify(response), 500

@app.route('/update_staff/<staff_id>', methods=['PUT'])
def update_staff(staff_id):
    try:
        # Extract data from the request JSON
        request_data = request.json

        # Validate the request data
        is_valid, validation_error = validate_staff_data(request_data)
        if not is_valid:
            response = {
                "status": "error",
                "message": validation_error
            }
            return jsonify(response), 400

        # Construct the updated_staff document
        updated_staff = {
            "first_name": request_data['first_name'],
            "last_name": request_data['last_name'],
            "date_of_birth": request_data['date_of_birth'],
            "email": request_data['email'],
            "phone": request_data['phone'],
            "street": request_data['street'],
            "city": request_data['city'],
            "state": request_data['state'],
            "postal_code": request_data['postal_code'],
            "department": request_data['department'],
            "position": request_data['position'],
            "start_date": request_data['start_date'],
            "salary": request_data['salary'],
            "employment_status": request_data['employment_status'],
            "dbs_id": request_data['dbs_id']
        }

        # Update staff data in the MongoDB collection
        result = staff_data.update_one({"_id": ObjectId(staff_id)}, {"$set": updated_staff})

        if result.modified_count > 0:
            response = {
                "status": "success",
                "message": "Staff updated successfully"
            }
            return jsonify(response), 200
        else:
            response = {
                "status": "error",
                "message": "Staff not found or no changes made"
            }
            return jsonify(response), 404

    except Exception as e:
        # Handle any exceptions that may occur during the update
        response = {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }
        return jsonify(response), 500

@app.route('/delete_staff/<staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    try:
        # Delete staff by ID
        result = staff_data.delete_one({"_id": ObjectId(staff_id)})

        if result.deleted_count > 0:
            response = {
                "status": "success",
                "message": "Staff deleted successfully"
            }
            return jsonify(response), 200
        else:
            response = {
                "status": "error",
                "message": "Staff not found"
            }
            return jsonify(response), 404

    except Exception as e:
        # Handle any exceptions that may occur during the deletion
        response = {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }
        return jsonify(response), 500

if __name__ == '__main__':
	app.run(debug=True)