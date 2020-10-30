from flask import Flask,request,jsonify
import os

app = Flask(__name__)

@app.route('/api',methods=['GET'])
def index():
    filename = str(request.args['Query'])
    return jsonify({filename:filename.split('.')[-1]})

if __name__ == "__main__":
    app.run(debug=True,port=int(os.environ.get('PORT',5000)))