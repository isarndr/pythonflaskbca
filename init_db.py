import sqlite3
from sqlalchemy import create_engine, Column, Integer, Float, MetaData, Table, Date, String, ForeignKey

DATABASE_URI = 'mysql://root:zAruUyl0mE232WV4xC3M@containers-us-west-159.railway.app:7138/railway'
engine = create_engine(DATABASE_URI, echo=True)
metadata = MetaData()

# Mendefinisikan tabel 'karyawan'
credit_card = Table('credit_card', metadata,
                 Column('card_id', Integer, primary_key=True),
                 Column('customer_id', String),
                 Column('limitt', Float),
                 Column('balance', Float),
                 Column('interest_rate', Float),
                 )

transaction = Table('transaction', metadata,
                 Column('transaction_id', Integer, primary_key=True),
                 Column('card_id', Integer, ForeignKey('credit_card.card_id')),
                 Column('amount', Float),
                 Column('date', Date),
                 Column('merchant', String),
                 )

# Membuat tabel
metadata.create_all(engine)

print("Database credit_cards.db dan tabel credit_cards telah berhasil dibuat")
