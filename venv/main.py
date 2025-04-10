from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS with proper settings
CORS(app, resources={r"/expenses/*": {"origins": "*"}}, supports_credentials=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/expenses'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Expense Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Handle CORS preflight requests explicitly
@app.route('/expenses', methods=['OPTIONS'])
@app.route('/expenses/<int:id>', methods=['OPTIONS'])
def handle_options(*args, **kwargs):
    return '', 204

# Route to get all expenses
@app.route('/expenses', methods=['GET'])
def get_expenses():
    expenses = Expense.query.all()
    return jsonify([{
        "id": exp.id,
        "name": exp.name,
        "amount": exp.amount,
        "category": exp.category,
        "date": exp.date,
        "payment_type": exp.payment_type
    } for exp in expenses])

# Route to add an expense
@app.route('/expenses', methods=['POST'])
def add_expense():
    data = request.json
    new_expense = Expense(
        name=data['name'],
        amount=data['amount'],
        category=data['category'],
        date=data['date'],
      payment_type = data.get('payment_type', 'CASH')

    )
    db.session.add(new_expense)
    db.session.commit()
    return jsonify({"message": "Expense added successfully"}), 201

# Route to delete an expense
@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    expense = Expense.query.get(id)
    if not expense:
        return jsonify({"message": "Expense not found"}), 404
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Expense deleted successfully"})

# Route to update an expense
@app.route('/expenses/<int:id>', methods=['PUT'])
def update_expense(id):
    data = request.json
    expense = Expense.query.get(id)
    if not expense:
        return jsonify({"message": "Expense not found"}), 404
    expense.name = data['name']
    expense.amount = data['amount']
    expense.category = data['category']
    expense.date = data['date']
    expense.payment_type = data['payment_type']
    db.session.commit()
    return jsonify({"message": "Expense updated successfully"})


if __name__ == '__main__':
    app.run(debug=True)
