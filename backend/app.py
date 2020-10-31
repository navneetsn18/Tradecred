import os,json
from flask import Flask, flash, request, redirect, url_for, session,jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import numpy as np
import pandas as pd
from datetime import date

UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/result', methods=['GET'])
def result():
    file = open('data.json')
    data = json.load(file)
    return jsonify(data)

@app.route('/upload', methods=['GET','POST'])
def fileUpload():
    ext_type=['csv','xls','xlsx']
    target=os.path.join(UPLOAD_FOLDER,'excel_files')
    if not os.path.isdir(target):
        os.mkdir(target)
    file = request.files['file'] 
    if file.filename.split('.')[-1] in ext_type:
        filename = secure_filename(file.filename)
        destination="/".join([target, filename])
        file.save(destination)
        session['uploadFilePath']=destination
        path = os.path.join(destination)
        print(path)
        workfunction(path)
    else:
        wrongfilefunction()
    return jsonify({"File Upload": "Success"})

def workfunction(filename):
    file = pd.read_excel(filename)
    data = pd.DataFrame(file)
    result={}
    result['Number_of_invoices']=int(data.count()[0])
    newData = data.dropna(axis=0)
    newData = newData[pd.to_datetime(data['Doc. Date'], errors='coerce') <= pd.to_datetime('today')]
    newData = newData[pd.to_datetime(data['Pstng Date'], errors='coerce') <= pd.to_datetime('today')]
    newData = newData[pd.to_datetime(data['Net due dt'], errors='coerce') >= pd.to_datetime(data['Pstng Date'])]
    vendordata = {k:v for k,v in zip(newData['Vendor Code'],newData['Vendor name'])}
    for i in newData.index:
        if newData['Vendor Code'][i] in vendordata:
            if newData['Vendor name'][i] != vendordata[newData['Vendor Code'][i]]:
                newData.drop([i])
    vendordata1 = {k:v for k,v in zip(newData['Vendor Code'],newData['Vendor name'])}
    vendordata2 = {k:v for k,v in zip(newData['Vendor name'],newData['Vendor Code'])}

    for i in newData.index:
        if newData['Vendor name'][i] != vendordata1[newData['Vendor Code'][i]]:
                newData.drop([i])

    for i in newData.index:
        if newData['Vendor Code'][i] != vendordata2[newData['Vendor name'][i]]:
                newData.drop([i])
    result['Total_sum']=float(newData['Amt in loc.cur.'].sum())
    df = newData.drop_duplicates(subset='Vendor name', keep="first")
    result['No_Up']=int(df['Vendor name'].count())
    result['Invalid']=int(data.shape[0]-newData.shape[0])
    json_object = json.dumps(result, indent = 4) 
    with open("data.json", "w") as outfile: 
        outfile.write(json_object)
    os.remove(filename)

def wrongfilefunction():
    json_object = json.dumps({}, indent = 4) 
    with open("data.json", "w") as outfile: 
        outfile.write(json_object)

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True,port=int(os.environ.get('PORT',5000)))