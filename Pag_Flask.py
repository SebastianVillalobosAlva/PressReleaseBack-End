from flask import Flask, render_template, session, url_for, redirect, jsonify, request
import numpy as np
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, TextField 
import joblib
import json
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
##########################
from Tools import Func
import datetime
import pandas as pd
import sklearn
import sklearn.pipeline
import sklearn.feature_extraction
import sklearn.utils._cython_blas
import sklearn.neighbors
import sklearn.neighbors._typedefs
import sklearn.tree
import sklearn.tree._utils
import re
        
app = Flask(__name__)

# Google Cloud SQL (change this accordingly) 
# PASSWORD ="Lusw7sbiMylOkAbc"
# PUBLIC_IP_ADDRESS = "34.70.119.102"
# DBNAME ="Notas"
# PROJECT_ID = "nth-rarity-307801"
# INSTANCE_NAME ="notas-guardadas123"

# configuration 
app.config["SECRET_KEY"] = "yoursecretkey"
# app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+mysqldb://root:{1q2w3e4r5t}@localhost/notasservicio?charset=utf8' 
#engine = SQLAlchemy.create_engine('mysql+mysqldb://root:{1q2w3e4r5t}@localhost/notasservicio')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

CORS(app,support_credentials=True)
db = SQLAlchemy(app)

class Nota(db.Model):
    __tablename__ = 'notasguardadasV2'
    id   = db.Column(db.Integer, primary_key = True)
    Titulo = db.Column(db.String(200))
    Autor = db.Column(db.String(200))
    Texto = db.Column(db.Text(4294967295))
    Link = db.Column(db.String(200))
    P_Si = db.Column(db.Float)
    P_No = db.Column(db.Float)  

db.create_all()

@app.route("/notas",methods=['POST'])
@cross_origin(support_credentials=True)
def Notes(): 
    # Read json
    first_engine = create_engine('mysql+mysqldb://root:{1q2w3e4r5t}@localhost/notasservicio?charset=utf8').connect()
    data = request.get_json()
    print(data) 
    
    notas_json = Func.Bajar_Notas(data,Nota,db,first_engine)
    
    first_engine.close()
    # first_engine.dispose()
   
    return notas_json

@app.route("/read-notas",methods=['POST'])
@cross_origin(support_credentials=True)
def Read_database():
    engine = create_engine('mysql+mysqldb://root:{1q2w3e4r5t}@localhost/notasservicio?charset=utf8').connect()
    all_notes_df = pd.read_sql_table('notasguardadasv2', engine)
    engine.close()
    # engine.dispose()
    
    return all_notes_df.to_json(orient='split')


@app.route("/delete-notas",methods=['POST'])
@cross_origin(support_credentials=True)
def Delete_notas():
    try:
        num_rows_deleted = db.session.query(Nota).delete()
        db.session.commit()
        notas_borradas = f"Se borraron {num_rows_deleted} notas"
        return jsonify(notas_borradas)
    except:
        db.session.rollback()
        return jsonify("No se logro borrar ninguna nota")

if __name__ == '__main__':
    app.run()