from flask import Flask, request, jsonify
import psycopg2

# Initialize Flask app
app = Flask(__name__)

# Debugging: Log all incoming requests
@app.before_request
def log_request():
    print(f"Request Method: {request.method}, URL: {request.url}")

# Database connection
conn = psycopg2.connect(
    dbname="student_management",
    user="admin",
    password="admin_password",  # Change as per your config
    host="localhost",
    port="5432",
)
cursor = conn.cursor()

# -------------------- USERS --------------------
@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        try:
            data = request.get_json()
            name = data['name']
            email = data['email']
            role = data['role']

            # Insert user into the database
            cursor.execute("INSERT INTO users (name, email, role) VALUES (%s, %s, %s) RETURNING user_id", (name, email, role))
            user_id = cursor.fetchone()[0]
            conn.commit()

            return jsonify({"user_id": user_id, "name": name, "email": email, "role": role}), 201
        except Exception as e:
            print(f"Error: {str(e)}")  # Ensure the error is printed in the terminal
            return jsonify({"error": "An error occurred while creating the user."}), 500
    elif request.method == 'GET':
        # Handle GET request to fetch users
        cursor.execute("SELECT * FROM users;")
        users = cursor.fetchall()
        if not users:
            return jsonify({"message": "No users found."}), 404
        users_list = [{"user_id": user[0], "name": user[1], "email": user[2], "role": user[3]} for user in users]
        return jsonify(users_list), 200

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    role = data.get('role')
    if not name or not email or not role:
        return jsonify({'message': 'Name, email, and role are required'}), 400
    cursor.execute("UPDATE users SET name = %s, email = %s, role = %s WHERE user_id = %s RETURNING user_id;", (name, email, role, user_id))
    if cursor.rowcount == 0:
        return jsonify({'message': 'User not found'}), 404
    conn.commit()
    return jsonify({'user_id': user_id, 'name': name, 'email': email, 'role': role})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE user_id = %s RETURNING user_id;", (user_id,))
    if cursor.rowcount == 0:
        return jsonify({'message': 'User not found'}), 404
    conn.commit()
    return jsonify({'message': f'User {user_id} deleted successfully'})

# -------------------- SUBJECTS --------------------
@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if request.method == 'POST':
        try:
            # Handle POST request to create subject
            data = request.get_json()
            name = data.get('name')
            if not name:
                return jsonify({'message': 'Subject name is required'}), 400
            
            cursor.execute("INSERT INTO subjects (name) VALUES (%s) RETURNING subject_id;", (name,))
            subject_id = cursor.fetchone()[0]
            conn.commit()

            return jsonify({'subject_id': subject_id, 'name': name}), 201
        except Exception as e:
            print(f"Error: {str(e)}")  # Ensure the error is printed in the terminal
            return jsonify({"error": "An error occurred while creating the subject."}), 500

    elif request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM subjects;")
            subjects_list = cursor.fetchall()
            if not subjects_list:
                return jsonify({"message": "No subjects found."}), 404
            subjects_data = [{"subject_id": subject[0], "name": subject[1]} for subject in subjects_list]
            return jsonify(subjects_data), 200
        except Exception as e:
            print(f"Error: {str(e)}")  # Ensure the error is printed in the terminal
            return jsonify({"error": "An error occurred while fetching subjects."}), 500

@app.route('/subjects/<int:subject_id>', methods=['GET', 'PUT', 'DELETE'])
def single_subject(subject_id):
    try:
        if request.method == 'GET':
            cursor.execute("SELECT * FROM subjects WHERE subject_id = %s;", (subject_id,))
            subject = cursor.fetchone()
            if not subject:
                return jsonify({'message': 'Subject not found'}), 404
            return jsonify({'subject_id': subject[0], 'name': subject[1]})

        if request.method == 'PUT':
            data = request.get_json()
            name = data.get('name')
            if not name:
                return jsonify({'message': 'Subject name is required'}), 400
            cursor.execute("UPDATE subjects SET name = %s WHERE subject_id = %s RETURNING subject_id;", (name, subject_id))
            if cursor.rowcount == 0:
                return jsonify({'message': 'Subject not found'}), 404
            conn.commit()
            return jsonify({'subject_id': subject_id, 'name': name})

        if request.method == 'DELETE':
            cursor.execute("DELETE FROM subjects WHERE subject_id = %s RETURNING subject_id;", (subject_id,))
            if cursor.rowcount == 0:
                return jsonify({'message': 'Subject not found'}), 404
            conn.commit()
            return jsonify({'message': f'Subject {subject_id} deleted successfully'})
    except Exception as e:
        print(f"Error: {str(e)}")  # Ensure the error is printed in the terminal
        return jsonify({"error": "An error occurred while processing the subject."}), 500

# -------------------- MARKS --------------------
@app.route('/marks', methods=['GET', 'POST'])
def marks():
    if request.method == 'POST':
        try:
            # Handle POST request to create marks
            data = request.get_json()
            student_id = data.get('user_id')
            subject_id = data.get('subject_id')
            marks = data.get('marks')
            if not student_id or not subject_id or marks is None:
                return jsonify({'message': 'Student ID, Subject ID, and Marks are required'}), 400
            
            cursor.execute("SELECT * FROM users WHERE user_id = %s;", (student_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'message': 'Student not found'}), 404

            cursor.execute("SELECT * FROM subjects WHERE subject_id = %s;", (subject_id,))
            subject = cursor.fetchone()
            if not subject:
                return jsonify({'message': 'Subject not found'}), 404

            cursor.execute("INSERT INTO marks (user_id, subject_id, marks) VALUES (%s, %s, %s) RETURNING mark_id;", 
                           (student_id, subject_id, marks))
            mark_id = cursor.fetchone()[0]
            conn.commit()

            return jsonify({'mark_id': mark_id, 'user_id': student_id, 'subject_id': subject_id, 'marks': marks}), 201
        except Exception as e:
            print(f"Error: {str(e)}")  # Ensure the error is printed in the terminal
            return jsonify({"error": "An error occurred while creating the marks entry."}), 500

    elif request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM marks;")
            marks_list = cursor.fetchall()
            if not marks_list:
                return jsonify({"message": "No marks found."}), 404
            marks_data = [{"mark_id": mark[0], "user_id": mark[1], "subject_id": mark[2], "marks": mark[3]} for mark in marks_list]
            return jsonify(marks_data), 200
        except Exception as e:
            print(f"Error: {str(e)}")  # Ensure the error is printed in the terminal
            return jsonify({"error": "An error occurred while fetching marks."}), 500

@app.route('/marks/<int:mark_id>', methods=['GET', 'PUT', 'DELETE'])
def single_mark(mark_id):
    try:
        if request.method == 'GET':
            cursor.execute("SELECT * FROM marks WHERE mark_id = %s;", (mark_id,))
            mark = cursor.fetchone()
            if not mark:
                return jsonify({'message': 'Marks entry not found'}), 404
            return jsonify({'mark_id': mark[0], 'user_id': mark[1], 'subject_id': mark[2], 'marks': mark[3]})

        if request.method == 'PUT':
            data = request.get_json()
            marks = data.get('marks')
            if marks is None:
                return jsonify({'message': 'Marks are required'}), 400
            cursor.execute("UPDATE marks SET marks = %s WHERE mark_id = %s RETURNING mark_id;", (marks, mark_id))
            if cursor.rowcount == 0:
                return jsonify({'message': 'Marks entry not found'}), 404
            conn.commit()
            return jsonify({'mark_id': mark_id, 'marks': marks})

        if request.method == 'DELETE':
            cursor.execute("DELETE FROM marks WHERE mark_id = %s RETURNING mark_id;", (mark_id,))
            if cursor.rowcount == 0:
                return jsonify({'message': 'Marks entry not found'}), 404
            conn.commit()
            return jsonify({'message': f'Marks entry {mark_id} deleted successfully'})
    except Exception as e:
        print(f"Error: {str(e)}")  # Ensure the error is printed in the terminal
        return jsonify({"error": "An error occurred while processing the marks entry."}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
