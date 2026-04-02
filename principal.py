from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
from bson import ObjectId 
from flask_mail import Mail, Message

def usuario():
    pass

def password():
    pass

EXTENSIONES = ["png", "jpg", "jpeg"]
app = Flask(__name__)
# app.config["UPLOAD_FOLDER"] = "./static/fondos"
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "static", "fondos")

client = MongoClient("mongodb://127.0.0.1:27017")
db = client.fondos_flask
e_fondos = db.fondos

app.config["MAIL_SERVER"]= "localhost"
app.config["MAIL_PORT"] = 25
app.config["MAIL_USERNAME"] = None
app.config["MAIL_PASSWORD"] = None
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = False
mail= Mail(app)

def archivo_permitido(nombre):
    return "." in nombre and nombre.rsplit(".", 1)[1] in EXTENSIONES

@app.route("/", methods=["GET", "POST"])
@app.route("/galeria")
def galeria():
    te=request.values.get("tema")
    estilos={}
    if te == None:
        l=e_fondos.find()
        estilos["todos"]="active"
    else:
        l=e_fondos.find({"tags": {"$in":[te]}})
        estilos[te]="active"  
    return render_template("index.html",activo=estilos,lista=l)

@app.route("/aportar")
def aportar():
    return render_template("aportar.html")

@app.route("/insertar", methods=["POST"])
def insertar():
    vo = request.files["archivo"]
    archivo = ""
    if vo.filename == "":
         return render_template("aportar.html",mensaje="Hay que indicar un archivo de fondo")
    else:
        if archivo_permitido(vo.filename):
            archivo = secure_filename(vo.filename)
            vo.save(os.path.join(app.config["UPLOAD_FOLDER"], archivo))
        else:
             return render_template("aportar.html",mensaje="¡El archivo indicado no es una imagen!")

    ulo = request.values.get("titulo")
    descrip = request.values.get("descripcion")
    tags=[]
    if request.values.get("animales"):
        tags.append("animales")
    if request.values.get("naturaleza"):
        tags.append("naturaleza")
    if request.values.get("ciudad"):
        tags.append("ciudad")
    if request.values.get("deporte"):
        tags.append("deporte")
    if request.values.get("personas"):
        tags.append("personas")
    e_fondos.insert_one({"titulo":ulo, "descripcion":descrip, "fondo": archivo, "tags":tags})
    return redirect("/")

@app.route("/form_email")
def formulario_email():
    id=request.values.get("_id")
    documento=e_fondos.find_one({"_id":ObjectId(id)})
    return render_template("form_email.html", id=id, fondo=documento["fondo"],
     titulo=documento["titulo"], descripcion=documento["descripcion"])

@app.route("/email", methods=["POST"])
def enviaemail():
    id=request.values.get("_id")
    documento=e_fondos.find_one({"_id":ObjectId(id)})
    msg = Message("Fondos de pantalla Flask", sender = "cursopython@cepibase.com")
    msg.recipients = [request.values.get("email")]
    msg.body = "Este es el fondo de pantalla seleccionado de nuestra galería."
    msg.html = render_template("email.html", titulo=documento["titulo"], descripcion=documento["descripcion"])
    with app.open_resource("./static/fondos/" + documento["fondo"]) as imagen_adjunto:
        msg.attach(documento["fondo"], "image/jpeg", imagen_adjunto.read())
    mail.send(msg)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)