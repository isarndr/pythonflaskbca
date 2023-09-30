# Import Library
from flask import Flask, jsonify, request, render_template
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from
from datetime import datetime
from sqlalchemy.sql import func



import os

# Mendefinisikan app
app = Flask(__name__)

# Lokasi database
DATABASE_PATH = 'C:/Users/isara/OneDrive/Documents/Training Python Sep 2023/mypy/Project Isa Randra - Aplikasi Pengelolaan Data Kartu Kredit/credit.db'

# Konfigurasi database
app.config['SQLALCHEMY_ECH0'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:zAruUyl0mE232WV4xC3M@containers-us-west-159.railway.app:7138/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Konfigurasi Swagger
app.config['SWAGGER'] = {
    'title':'Data Aplikasi Pengelolaan Data Kartu Kredit',
    'uiversion':3,
    'headers':[],
    'specs':[
        {
            'endpoint':'apispec_1',
            'route':'/apispec_1.json',
            'rule_filter':lambda rule:True,
            'model_filter':lambda tag:True,
        }
    ],
    'static_url_path':'/flasgger_static',
    'swagger_ui':True,
    'specs_route':'/apidocs'
}
swagger= Swagger(app)

db = SQLAlchemy(app)

# Model Data Karyawan

class CreditCard(db.Model):
    card_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String,nullable=False)
    limit = db.Column(db.Float,nullable=False)
    balance = db.Column(db.Float,nullable=False)
    interest_rate = db.Column(db.Float,nullable=False)

class Transaction(db.Model):
    transaction_id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer,nullable=False)
    amount = db.Column(db.Float,nullable=False)
    date = db.Column(db.Date,nullable=False)
    merchant = db.Column(db.String,nullable=False)
    
# @app.before_first_request
# def create_tables():
#     db.create_all()
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input', methods=['GET','POST'])
def input_data():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        limit=request.form.get('limit')
        balance=request.form.get('balance')
        interest_rate=request.form.get('interest_rate')

        if not customer_id or not limit or not balance or not interest_rate:
            return render_template('createdatacredit.html', error="Semua field wajib diisi")

        new_credit = CreditCard(
            customer_id=customer_id,
            limit=limit,
            balance=balance,
            interest_rate=interest_rate
        )
        
        db.session.add(new_credit)
        db.session.commit()
        
        return render_template('confirmation.html')
    return render_template('createdatacredit.html')

# Koneksi API Create
@app.route('/credit_card', methods=['POST'])
@swag_from('swagger_docs/create_data_credit.yaml')
def create_credit():
    data = request.json
    
    new_credit = CreditCard(
        customer_id=data['customer_id'],
        limit=data['limit'],
        balance=data['balance'],
        interest_rate=data['interest_rate']
    )   
    
    db.session.add(new_credit)
    db.session.commit()
    
    return jsonify({'message':'Data credit card berhasil ditambahkan'}),201

@app.route('/display_all', methods=['GET'])
@swag_from('swagger_docs/get_all_data_credit.yaml')
def get_all_credit_card():
    credit_card_list = []
    try:
        all_credit_card = CreditCard.query.all()
        
        for credit_card in all_credit_card:
            credit_card_data = {
                'card_id': credit_card.card_id,
                'customer_id': credit_card.customer_id,
                'limit': credit_card.limit,
                'balance': credit_card.balance,
                'interest_rate': credit_card.interest_rate
            }  
            credit_card_list.append(credit_card_data)
    except Exception as e:
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data")
    finally:
        if credit_card_list:
            return render_template('displayallcredit.html', credit_card_list=credit_card_list)
        else:
            return render_template('error.html', pesan="Tidak ada data credit card"), 404


@app.route('/display', methods=['GET'])
def get_credit_card(card_id):
    try:
        credit = CreditCard.query.get(card_id)
    except Exception as e:
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data")
    finally:
        if credit:
            return render_template('displayallcredit.html', credit_card_list=credit)
        else:
            return render_template('error.html', pesan="Tidak ada data credit card"), 404


@app.route('/creditcard/<int:card_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_data_credit.yaml')
def delete_credit_card(card_id):
    try:
        credit_card_to_delete = CreditCard.query.filter_by(card_id=card_id).first()
        
        if credit_card_to_delete:
            db.session.delete(credit_card_to_delete)
            db.session.commit()
            return jsonify({'message':f'Data credit card dengan ID {card_id} berhasil dihapus'}), 200
        else:
            return jsonify({'message': f'Data credit card dengan ID {card_id} tidak ditemukan'}), 404
    except Exception as e:
        return  jsonify({'message':f"Terjadi kesalahan: {e}"}), 500 

@app.route('/delete_credit_card',methods=['GET','POST'])
def delete_credit_card_ui():
    data_list=[]
    try:
        if request.method == 'POST':
            search_customer_id = request.form['customer_id']
            all_credit_card=CreditCard.query.all()
            data_list=[credit_card for credit_card in all_credit_card if search_customer_id in credit_card.customer_id]
    except Exception as e:
        error_message = f"Terjadi kesalahan: {e}"
        print(error_message)
        return render_template('error.html', pesan=error_message), 500
    finally:
        return render_template('deletedatacredit.html',data_list=data_list)    

@app.route('/updatedata', methods=['GET', 'POST'])
def updatedata():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        data_list = CreditCard.query.filter(CreditCard.customer_id.like(f"%{customer_id}%")).all()
        return render_template('updatedatacredit.html', data_list=data_list)
    return render_template('updatedatacredit.html')

@app.route('/update_credit', methods=['POST'])
def update_credit():
    try:
        card_id = request.form.get('card_id')
        customer_id = request.form.get('customer_id')
        limit = request.form.get('limit')
        balance = request.form.get('balance')
        interest_rate = request.form.get('interest_rate')
        # print("test ",card_id)
        credit = CreditCard.query.get(card_id)
        
        if not credit:
            return jsonify({'message': 'Credit card tidak ditemukan'}), 404
        
        credit.customer_id = customer_id
        credit.limit = limit
        credit.balance = balance
        credit.interest_rate = interest_rate
        
        db.session.commit()
        
        return redirect(url_for('get_all_credit_card'))

    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}),500

# @app.route('/creditcard/<int:card_id>', methods=['GET'])
# @swag_from('swagger_docs/get_one_credit.yaml')
# def get_one_credit(card_id):
#     if request.method == 'GET':
#         card_id = request.form.get('card_id')
#         credit = CreditCard.query.get(card_id)
#         return render_template('displaycredit.html', credit)
#     return render_template('displaycredit.html')

@app.route('/input_transaksi', methods=['GET','POST'])
def input_data_transaksi():
    if request.method == 'POST':
        card_id = request.form.get('card_id')
        amount=request.form.get('amount')
        date=datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        merchant=request.form.get('merchant')
        
        credit = CreditCard.query.get(card_id)
                
        if not credit:
            return render_template('createdatatransaksi.html', error="Card ID tidak exist")        
        # print("date ", date, type(date))
        if credit.balance < float(amount):
            return render_template('createdatatransaksi.html', error=f"Your balance is {credit.balance}")
        
        if credit.limit < float(amount):
            return render_template('createdatatransaksi.html', error=f"Your limit is {credit.limit}")   

        if not card_id or not amount or not date or not merchant:
            return render_template('createdatatransaksi.html', error="Semua field wajib diisi")

        credit.balance = credit.balance - float(amount) - ((float(amount)* credit.interest_rate/100))
        
        if credit.balance<0:
            return render_template('createdatatransaksi.html', error="Saldo tidak cukup")
                
        new_transaction = Transaction(
            card_id=card_id,
            amount=amount,
            date=date,
            merchant=merchant
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        return render_template('confirmation.html')
    return render_template('createdatatransaksi.html')

# Koneksi API Create
@app.route('/transaction', methods=['POST'])
# @swag_from('swagger_docs/create_data_transaksi.yaml')
def create_transaksi():
    data = request.json
    
    print("card id", data['card_id'])
    credit = CreditCard.query.get(data['card_id'])
                
    if not credit:
        return jsonify({'message': 'Card ID tidak ditemukan'}), 404
            
    credit.balance = credit.balance - data['amount']
    
    new_transaksi = Transaction(
        card_id=data['card_id'],
        amount=data['amount'],
        date=data['date'],
        merchant=data['merchant']  
    )   
    
    db.session.add(new_transaksi)
    db.session.commit()
    
    return jsonify({'message':'Data transaksi berhasil ditambahkan'}),201



@app.route('/display_all_transaksi', methods=['GET'])
@swag_from('swagger_docs/get_all_data_transaksi.yaml')
def get_all_transactions():
    transaction_list = []
    try:
        all_transaction = Transaction.query.all()
        
        for transaction in all_transaction:
            transaction_data = {
                'transaction_id': transaction.transaction_id,
                'card_id': transaction.card_id,
                'amount': transaction.amount,
                'date': transaction.date,
                'merchant': transaction.merchant
            }  
            transaction_list.append(transaction_data)
    except Exception as e:
        return render_template('error.html', pesan="Terjadi kesalahan saat mengambil data")
    finally:
        if transaction_list:
            return render_template('displayalltransaksi.html', transaction_list=transaction_list)
        else:
            return render_template('error.html', pesan="Tidak ada data transaksi"), 404

@app.route('/updatedata_transaksi', methods=['GET', 'POST'])
def updatedata_transaksi():
    if request.method == 'POST':
        card_id = request.form.get('card_id')
        data_list = Transaction.query.filter(Transaction.card_id.like(f"%{card_id}%")).all()
        return render_template('updatedatatransaction.html', data_list=data_list)
    return render_template('updatedatatransaction.html')

@app.route('/update_transaksi', methods=['POST'])
def update_transaksi():
    try:
        transaction_id = request.form.get('transaction_id')
        card_id = request.form.get('card_id')
        amount = request.form.get('amount')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
        merchant = request.form.get('merchant')
        # print("test ",card_id)
        transaksi = Transaction.query.get(transaction_id)
        
        if not transaksi:
            return jsonify({'message': 'Transaksi tidak ditemukan'}), 404
        
        transaksi.card_id = card_id
        transaksi.amount = amount
        transaksi.date = date
        transaksi.merchant = merchant
        
        db.session.commit()
        
        return redirect(url_for('get_all_transactions'))

    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}),500
    
@app.route('/transaksi/<int:transaction_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_data_transaksi.yaml')
def delete_transaction(transaction_id):
    try:
        transaction_to_delete = Transaction.query.filter_by(transaction_id=transaction_id).first()
        
        if transaction_to_delete:
            db.session.delete(transaction_to_delete)
            db.session.commit()
            return jsonify({'message':f'Data transaksi dengan ID {transaction_id} berhasil dihapus'}), 200
        else:
            return jsonify({'message': f'Data transaksi dengan ID {transaction_id} tidak ditemukan'}), 404
    except Exception as e:
        return  jsonify({'message':f"Terjadi kesalahan: {e}"}), 500 

@app.route('/delete_transaksi',methods=['GET','POST'])
def delete_transaksi_ui():
    data_list=[]
    try:
        if request.method == 'POST':
            search_transaksi_id = request.form['transaction_id']
            # print("test ",search_transaksi_id)
            all_transaksi=Transaction.query.all()
            data_list=[transaction for transaction in all_transaksi if int(search_transaksi_id) is transaction.transaction_id]
    except Exception as e:
        error_message = f"Terjadi kesalahan: {e}"
        print(error_message)
        return render_template('error.html', pesan=error_message), 500
    finally:
        return render_template('deletedatatransaksi.html',data_list=data_list)    
  
@app.route('/creditcard', methods=['GET', 'POST'])
# @swag_from('swagger_docs/get_data_credit.yaml')
def get_one_credit():
    data_list=[]
    if request.method == 'POST':
        card_id = request.form.get('card_id')
        creditcard = CreditCard.query.get(card_id)
        data_list.append(creditcard)
        return render_template('creditdata.html',data_list=data_list)
    return render_template('creditdata.html')


@app.route('/creditcard/<int:card_id>', methods=['POST'])
@swag_from('swagger_docs/get_data_credit.yaml')
def get_one_credit_swag(card_id):
        data_list=[]

        creditcard = CreditCard.query.get(card_id)
        data_list.append(creditcard)

        return render_template('creditdata.html',data_list=data_list)
    

@app.route('/update_credit/<int:card_id>', methods=['POST'])
@swag_from('swagger_docs/update_data_credit.yaml')
def update_credit2(card_id):
    data = request.json
    
    new_credit = CreditCard(
        customer_id=data['customer_id'],
        limit=data['limit'],
        balance=data['balance'],
        interest_rate=data['interest_rate']
    )   
    
    try:
        customer_id = new_credit.customer_id
        limit = new_credit.limit
        balance = new_credit.balance
        interest_rate = new_credit.interest_rate
        # print("test ",card_id)
        credit = CreditCard.query.get(card_id)
        
        if not credit:
            return jsonify({'message': 'Credit card tidak ditemukan'}), 404
        
        credit.customer_id = customer_id
        credit.limit = limit
        credit.balance = balance
        credit.interest_rate = interest_rate
        
        db.session.commit()
        
        return redirect(url_for('get_all_credit_card'))

    except Exception as e:
        return jsonify({'message': f'Terjadi kesalahan: {str(e)}'}),500

@app.route('/input_transaksi2', methods=['POST'])
@swag_from('swagger_docs/create_data_transaksiswagger.yaml')
def input_data_transaksi2():
        data = request.json

        print("test",data)
        card_id = data['card_id']
        amount=data['amount']
        date=datetime.strptime(str(data['date']), '%Y-%m-%d')
        merchant=data['merchant']
        
        credit = CreditCard.query.get(card_id)
                
        if not credit:
            return render_template('createdatatransaksiswagger.html', error="Card ID tidak exist")        
        # print("date ", date, type(date))
        if credit.balance < float(amount):
            return render_template('createdatatransaksiswagger.html', error=f"Your balance is {credit.balance}")
        
        if credit.limit < float(amount):
            return render_template('createdatatransaksiswagger.html', error=f"Your limit is {credit.limit}")   

        if not card_id or not amount or not date or not merchant:
            return render_template('createdatatransaksiswagger.html', error="Semua field wajib diisi")

        credit.balance = credit.balance - float(amount) - ((float(amount)* credit.interest_rate/100))
        
        if credit.balance<0:
            return render_template('createdatatransaksiswagger.html', error="Saldo tidak cukup")
                
        new_transaction = Transaction(
            card_id=card_id,
            amount=amount,
            date=date,
            merchant=merchant
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        return render_template('confirmation.html')
    
if __name__ == '__main__':
    app.run(debug=True, port=5030)
