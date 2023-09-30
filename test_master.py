import unittest

from psycopg2 import Date
from flask_testing import TestCase
from flask import url_for
from datacredit import app, db, CreditCard, Transaction # Import modul-modul yang diperlukan
import datetime


# Kelas MyTest untuk melakukan testing pada aplikasi
class MyTest(TestCase):

    # Metode untuk membuat aplikasi dalam mode testing
    def create_app(self):
        app.config['TESTING'] = True  # Mengaktifkan mode testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///credit.db'  # Menggunakan database in-memory untuk testing
        return app

    # Metode yang dijalankan sebelum setiap test
    def setUp(self):
        db.create_all()  # Membuat semua tabel dalam database

    # Metode yang dijalankan setelah setiap test
    def tearDown(self):
        db.session.remove()  # Menghapus sesi database
        db.drop_all()  # Menghapus semua tabel dalam database

    # Test untuk endpoint index '/'
    def test_index(self):
        response = self.client.get('/')  # Melakukan request GET ke '/'
        self.assert200(response)  # Memastikan response adalah 200 OK
        assert b"<title>Welcome to Aplikasi Pengelolaan Data Kartu Kredit</title>" in response.data
        # self.assert_template_used('index.html')  # Memastikan template yang digunakan adalah 'index.html'

    # Test untuk membuat karyawan baru
    def test_create_credit(self):
        # Melakukan request POST ke '/karyawan' dengan data karyawan baru
        response = self.client.post('/credit_card', json={
            'customer_id': '1',
            'limitt': '10',
            'balance': '20',
            'interest_rate':'30'
        })
        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
        karyawan = CreditCard.query.first()  # Mengambil karyawan pertama dari database
        self.assertEqual(karyawan.customer_id, '1')  # Memastikan nama karyawan adalah 'John Doe'

    # Test untuk menghapus karyawan
    def test_delete_credit(self):
        # Membuat objek karyawan baru dan menyimpannya ke database
        karyawan = CreditCard(customer_id='1', limitt='10000000', balance='100000000', interest_rate='8')
        db.session.add(karyawan)
        db.session.commit()

        # Melakukan request DELETE ke '/karyawan/{id_karyawan}'
        response = self.client.delete(f'/creditcard/{karyawan.card_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assertIsNone(CreditCard.query.get(karyawan.card_id))  # Memastikan karyawan dengan id tersebut sudah dihapus
        
    def test_delete_credit_ui(self):
        # Membuat objek karyawan baru dan menyimpannya ke database 
        karyawan5 = CreditCard(customer_id='3', limitt='30000000', balance='300000000', interest_rate='4')
        db.session.add(karyawan5)        
        db.session.commit()

        # Melakukan request POST ke '/delete_karyawan' dengan data nama karyawan
        response = self.client.post('/delete_credit_card', data={'customer': 1})
        self.assert200(response)  # Memastikan response adalah 200 OK
        # self.assert_template_used('deletedatatransaksi.html')  # Memastikan template yang digunakan adalah 'deletedata.html'
        self.assertIn(b'1', response.data)  # Memastikan 'John Doe' ada dalam response data


# =========================================================== TABEL NON MASTER ============================================

# Test untuk endpoint index '/'

    # Test untuk membuat karyawan baru
    # def test_create_karyawan2(self):
    #     # Melakukan request POST ke '/karyawan' dengan data karyawan baru
        
    #     karyawan = CreditCard(customer_id='1', limitt='10000000', balance='100000000', interest_rate='8')
    #     db.session.add(karyawan)
    #     db.session.commit()
                 
    #     response = self.client.post('/transaction', json={
    #         'card_id': karyawan.card_id,
    #         'amount': 100,
    #         # 'date': date('2023-09-29'),
    #         'date':datetime.date.today(),
    #         'merchant':30
    #     })
    #     self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
    #     karyawan = Transaction.query.first()  # Mengambil karyawan pertama dari database
    #     self.assertEqual(karyawan.card_id, '1')  # Memastikan nama karyawan adalah 'John Doe'

    # Test untuk menghapus karyawan
    def test_delete_transaksi(self):
        # Membuat objek karyawan baru dan menyimpannya ke database
        karyawan = CreditCard(customer_id='1', limitt='10000000', balance='100000000', interest_rate='8')
        db.session.add(karyawan)
        db.session.commit()

        karyawan2 = Transaction(card_id='1', amount='10000000', date=datetime.date.today(), merchant='8')
        db.session.add(karyawan2)
        db.session.commit()
        
        # Melakukan request DELETE ke '/karyawan/{id_karyawan}'
        response = self.client.delete(f'/transaksi/{karyawan2.transaction_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assertIsNone(Transaction.query.get(karyawan2.transaction_id))  # Memastikan karyawan dengan id tersebut sudah dihapus
        
    # Test untuk mendapatkan semua karyawan
    def test_get_all_transaksi(self):
        # Membuat dua objek karyawan baru dan menyimpannya ke database
        karyawan = CreditCard(customer_id='1', limitt='10000000', balance='100000000', interest_rate='8')
        db.session.add(karyawan)

        karyawan2 = Transaction(card_id='1', amount='10000000', date=datetime.date.today(), merchant='8')
        db.session.add(karyawan2)
        
        karyawan3 = CreditCard(customer_id='2', limitt='20000000', balance='200000000', interest_rate='9')
        db.session.add(karyawan3)

        karyawan4 = Transaction(card_id='2', amount='20000000', date=datetime.date.today(), merchant='3')
        db.session.add(karyawan4)
        
        karyawan5 = CreditCard(customer_id='3', limitt='30000000', balance='300000000', interest_rate='4')
        db.session.add(karyawan5)

        karyawan6 = Transaction(card_id='3', amount='30000000', date=datetime.date.today(), merchant='3')
        db.session.add(karyawan6)
        
        db.session.commit()

        # Melakukan request GET ke '/display_all'
        response = self.client.get('/display_all_transaksi')
        self.assert200(response)  # Memastikan response adalah 200 OK
        # self.assert_template_used('displayalltransaksi.html')  # Memastikan template yang digunakan adalah 'displayall.html'
        self.assertIn(b'3', response.data)  # Memastikan 'John Doe' ada dalam response data
        self.assertIn(b'2', response.data)  # Memastikan 'Jane Doe' ada dalam response data

    # # Test untuk mendapatkan satu karyawan berdasarkan id
    # def test_get_one_karyawan(self):
    #     # Membuat objek karyawan baru dan menyimpannya ke database
    #     karyawan = Karyawan(nama_karyawan='John Doe', cabang_bca='Jakarta', jabatan='Staff')
    #     db.session.add(karyawan)
    #     db.session.commit()

    #     # Melakukan request GET ke '/karyawan/{id_karyawan}'
    #     response = self.client.get(f'/karyawan/{karyawan.id_karyawan}')
    #     self.assert200(response)  # Memastikan response adalah 200 OK

    # Test untuk menghapus karyawan melalui UI
    def test_delete_transaksi_ui(self):
        # Membuat objek karyawan baru dan menyimpannya ke database
        karyawan4 = Transaction(card_id='2', amount='20000000', date=datetime.date.today(), merchant='3')
        db.session.add(karyawan4)
        
        karyawan5 = CreditCard(customer_id='3', limit='30000000', balance='300000000', interest_rate='4')
        db.session.add(karyawan5)        
        db.session.commit()

        # Melakukan request POST ke '/delete_karyawan' dengan data nama karyawan
        response = self.client.post('/delete_transaksi', data={'transaction_id': 1})
        self.assert200(response)  # Memastikan response adalah 200 OK
        # self.assert_template_used('deletedatatransaksi.html')  # Memastikan template yang digunakan adalah 'deletedata.html'
        self.assertIn(b'1', response.data)  # Memastikan 'John Doe' ada dalam response data

if __name__ == '__main__':
    unittest.main()  # Menjalankan semua test
