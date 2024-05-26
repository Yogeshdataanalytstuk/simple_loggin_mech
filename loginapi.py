from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lprlogin.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)  # Store as binary
    ip_address = db.Column(db.String(45), nullable=True)  # Assuming IPv6 compatibility

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    print(f"Attempting to log in with username: {username}")  # Debug log
    user = User.query.filter_by(username=username).first()

    if user:
        print(f"User found in database: {user.username}")  # Debug log
        # Use bcrypt to check the password
        if bcrypt.checkpw(password.encode(), user.password):
            print(f"Successful login for {username}.")
            return jsonify({"status": "success", "ip_address": user.ip_address}), 200
        else:
            print(f"Failed login attempt for {username} with provided password.")
            return jsonify({"status": "failed"}), 401
    else:
        print(f"No user found for username: {username}")
        return jsonify({"status": "failed"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
