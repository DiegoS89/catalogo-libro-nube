from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://cxulgrmnebnqpt:3b525af9c5c9fd333bbea6c8886adb6efa16535c356bac39b08ea410c6686670@ec2-54-159-35-35.compute-1.amazonaws.com:5432/d6t1tvr2oer58i'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SuperSecretKey'

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

# CLASES DATABASE ------------------------------------------------------------------------------------------------------------------- DATABASE
class Usuarios(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    password = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email = email
        self.password = password

class Editorial(db.Model):
    __tablename__="editorial"
    id_editorial = db.Column(db.Integer, primary_key=True)
    nombre_editorial = db.Column(db.String(80))

    def __init__(self, nombre_editorial):
        self.nombre_editorial=nombre_editorial

class Libro(db.Model):
    __tablename__="libro"
    id_libro = db.Column(db.Integer, primary_key=True)
    titulo_libro = db.Column(db.String(80))
    fecha_publicacion = db.Column(db.Date)
    numero_paginas = db.Column(db.Integer)
    formato = db.Column(db.String(30))
    volumen = db.Column(db.Integer)
    imgLibro = db.Column(db.String(200))

    id_editorial = db.Column(db.Integer, db.ForeignKey("editorial.id_editorial"))
    id_genero = db.Column(db.Integer, db.ForeignKey("genero.id_genero"))
    id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))

    def __init__(self, titulo_libro, fecha_publicacion, numero_paginas, formato, volumen, imgLibro, id_editorial, id_genero, id_autor):
        self.titulo_libro = titulo_libro
        self.fecha_publicacion = fecha_publicacion
        self.numero_paginas = numero_paginas
        self.formato = formato
        self.volumen = volumen
        self.imgLibro = imgLibro
        self.id_editorial = id_editorial
        self.id_genero = id_genero
        self.id_autor = id_autor

class MisFavoritos(db.Model):
    __tablename__ = "misFavoritos"
    id_lista_favoritos = db.Column(db.Integer, primary_key=True)

    id_libro = db.Column(db.Integer, db.ForeignKey("libro.id_libro"))
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))

    def __init__(self, id_libro, id_usuario):
        self.id_libro = id_libro
        self.id_usuario = id_usuario

class Genero(db.Model):
    __tablename__ = "genero"
    id_genero = db.Column(db.Integer, primary_key=True)
    nombre_genero = db.Column(db.String(40))

    def __init__(self, nombre_genero):
        self.nombre_genero = nombre_genero

class Autor(db.Model):
    __tablename__ = "autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nombre_autor = db.Column(db.String(80))
    fecha_nac = db.Column(db.Date)
    nacionalidad = db.Column(db.String(40))

    def __init__(self, nombre_autor, fecha_nac, nacionalidad):
        self.nombre_autor = nombre_autor
        self.fecha_nac = fecha_nac
        self.nacionalidad = nacionalidad

# LOGINS MANAGERS ------------------------------------------------------------------------------------------------------------------- LOGINS
@login_manager.user_loader
def load_user(userid):
    return Usuarios.query.get(int(userid))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    consultaUsuario = Usuarios.query.filter_by(email=email).first()
    pass_cifrado = bcrypt.check_password_hash(consultaUsuario.password,password)

    if bcrypt.check_password_hash(consultaUsuario.password,password) == pass_cifrado:
        login_user(consultaUsuario)
        return redirect("/catalogo")
    else:
        return redirect("/")

@app.route("/registrar")
def registrar():
    return render_template("registro.html")

@app.route("/registrar_usuario", methods=["POST"])
def registrarusuario():
    email = request.form["email"]
    password = request.form["password"]

    pass_cifrado = bcrypt.generate_password_hash(password).decode('utf-8')

    usuario = Usuarios(email = email, password = pass_cifrado)
    db.session.add(usuario)
    db.session.commit()

    return redirect("/")


# CRUD LIBROS ------------------------------------------------------------------------------------------------------------------- LIBROS
@app.route("/addLibro")
@login_required
def addLibro():
    consulta_Autores = Autor.query.all()
    consulta_Generos = Genero.query.all()
    consulta_Editoriales = Editorial.query.all()
    return render_template("agregarlibro.html", autores = consulta_Autores, generos = consulta_Generos, editoriales = consulta_Editoriales)

@app.route("/registrar_libro", methods=["POST"])
@login_required
def registrarlibro():
    nombreLibro = request.form["nombreLibro"]
    fechaPublic = request.form["fecha"]
    paginas = request.form["numeroLibro"]
    formato = request.form["formato"]
    volumen = request.form["volumen"]
    editorial = request.form["editorial"]
    genero = request.form["genero"]
    autor = request.form["autor"]
    img = request.form["img"]

    libro = Libro(titulo_libro=nombreLibro, fecha_publicacion=fechaPublic, numero_paginas=paginas, formato=formato, volumen=volumen, imgLibro=img, id_editorial=editorial, id_genero=genero, id_autor=autor)
    db.session.add(libro)
    db.session.commit()

    return redirect("/catalogo")

@app.route("/eliminarLibro/<id>")
@login_required
def eliminar(id):
    libro = Libro.query.filter_by(id_libro = int(id)).delete()
    db.session.commit()
    return redirect("/catalogo")

@app.route("/editarLibro/<ID>")
@login_required
def editar(ID):
    libros = Libro.query.filter_by(id_libro = int(ID)).first()
    genero = Genero.query.all()
    autor = Autor.query.all()
    editorial = Editorial.query.all()
    formato = ["1","2"]

    return render_template("editarLibro.html", libro = libros, generos = genero, autores = autor, editoriales = editorial, formt =formato)

@app.route("/editar_libro", methods=["POST"])
@login_required
def editarlibro():
    idlibro = request.form["idlibro"]
    nombreLibro = request.form["nombreLibro"]
    fechaPublic = request.form["fecha"]
    paginas = request.form["numeroLibro"]
    formato = request.form["formato"]
    volumen = request.form["volumen"]
    editorial = request.form["editorial"]
    genero = request.form["genero"]
    autor = request.form["autor"]
    img = request.form["img"]

    libro = Libro.query.filter_by(id_libro=int(idlibro)).first()
    libro.titulo_libro = nombreLibro
    libro.fecha_publicacion = fechaPublic
    libro.numero_paginas = paginas
    libro.formato = formato
    libro.volumen = volumen
    libro.imgLibro = img
    libro.id_editorial= editorial
    libro.id_genero = genero
    libro.id_autor = autor
    db.session.commit()

    return redirect("/catalogo")

@app.route("/catalogo")
@login_required
def catalogo():
    Libros = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).add_columns(Genero.nombre_genero, Libro.titulo_libro, Libro.numero_paginas, Libro.formato, Autor.nombre_autor, Editorial.nombre_editorial, Libro.fecha_publicacion, Libro.volumen, Libro.imgLibro, Libro.id_libro)

    print("EL ID DEL USUARIO ESS ---- "+ str(current_user.id ))

    return render_template("catalogoLibros.html", libros = Libros)

# CRUD EDITORIALES ------------------------------------------------------------------------------------------------------------------- EDITORIALES
@app.route("/addGeneroEditorial")
@login_required
def addGenero():
    return render_template("agregargenero.html")

@app.route("/registrar_editorial", methods=["POST"])
@login_required
def registrareditorial():
    editorial = request.form["editorial"]

    editorial = Editorial(editorial)
    db.session.add(editorial)
    db.session.commit()

    return redirect("/addGeneroEditorial")

@app.route("/editoriales")
@login_required
def editorial():
    editorial = Editorial.query.all()

    return render_template("editores.html", editoriales = editorial)

@app.route("/eliminarEditor/<id>")
@login_required
def eliminarEditor(id):
    editorial = Editorial.query.filter_by(id_editorial = int(id)).delete()
    db.session.commit()
    return redirect("/editoriales")

@app.route("/modificarEditorial/<ID>")
@login_required
def modificarEditorial(ID):
    editorial = Editorial.query.filter_by(id_editorial = int(ID)).first()

    return render_template("editorialEditar.html", editoriales = editorial)

@app.route("/editar_Editorial", methods=["POST"])
@login_required
def editarEditor():
    idlibro = request.form["ideditorial"]
    editorial = request.form["editorial"]

    editorial1 = Editorial.query.filter_by(id_editorial = int(idlibro)).first()
    editorial1.nombre_editorial = editorial
    db.session.commit()

    return redirect("/editoriales")


# CRUD GENERO ------------------------------------------------------------------------------------------------------------------- GENERO

@app.route("/registrar_genero", methods=["POST"])
@login_required
def registrargenero():

    genero = request.form["genero"]

    genero = Genero(genero)
    db.session.add(genero)
    db.session.commit()

    return redirect("/addGeneroEditorial")

@app.route("/generos")
@login_required
def generos():
    genero = Genero.query.all()

    return render_template("generos.html", generos = genero)

@app.route("/eliminarGenero/<id>")
@login_required
def eliminarGenero(id):
    genero = Genero.query.filter_by(id_genero = int(id)).delete()
    db.session.commit()
    return redirect("/generos")

@app.route("/modificarGenero/<ID>")
@login_required
def modificarGenero(ID):
    generos = Genero.query.filter_by(id_genero = int(ID)).first()

    return render_template("editarGenero.html", genero = generos)


@app.route("/editar_Genero", methods=["POST"])
@login_required
def editar_Genero():
    idgenero = request.form["idgenero"]
    genero = request.form["genero"]

    genero1 = Genero.query.filter_by(id_genero = int(idgenero)).first()
    genero1.nombre_genero = genero
    db.session.commit()

    return redirect("/generos")

# CRUD AUTOR ------------------------------------------------------------------------------------------------------------------- AUTOR

@app.route("/addAutor")
@login_required
def addAutor():
    return render_template("agregarautor.html")

@app.route("/registrar_autor", methods=["POST"])
@login_required
def registrarautor():
    autor = request.form["nombreAutor"]
    fechanac = request.form["fecha"]
    nacionalidad = request.form["nacionalidad"]

    autor1 = Autor(nombre_autor=autor,fecha_nac=fechanac,nacionalidad=nacionalidad)
    db.session.add(autor1)
    db.session.commit()

    return redirect("/addAutor")

@app.route("/autores")
@login_required
def autores():
    autor = Autor.query.all()

    return render_template("autores.html", autores = autor)

@app.route("/eliminarAutor/<id>")
@login_required
def eliminarAutor(id):
    autor = Autor.query.filter_by(id_autor = int(id)).delete()
    db.session.commit()
    return redirect("/autores")

@app.route("/modificarAutor/<ID>")
@login_required
def modificarAutor(ID):
    autores = Autor.query.filter_by(id_autor = int(ID)).first()

    return render_template("editarAutor.html", autor = autores)


@app.route("/editar_Autor", methods=["POST"])
@login_required
def editar_Autor():
    idautor = request.form["idautor"]
    nombre = request.form["nombreAutor"]
    fecha = request.form["fecha"]
    nacionalidad = request.form["nacionalidad"]

    autor1 = Autor.query.filter_by(id_autor = int(idautor)).first()
    autor1.nombre_autor = nombre
    autor1.fecha_nac = fecha
    autor1.nacionalidad = nacionalidad
    db.session.commit()

    return redirect("/autores")




# MIS FAVORITOS ------------------------------------------------------------------------------------------------------------------- MIS FAVORITOS

@app.route("/MisFavoritos")
@login_required
def misFavoritos():
    Libros = Libro.query.join(Genero, Libro.id_genero == Genero.id_genero).join(Autor, Libro.id_autor == Autor.id_autor).join(Editorial, Libro.id_editorial == Editorial.id_editorial).join(MisFavoritos, Libro.id_libro == MisFavoritos.id_libro).add_columns(Genero.nombre_genero, Libro.titulo_libro, Libro.numero_paginas, Libro.formato, Autor.nombre_autor, Editorial.nombre_editorial, Libro.fecha_publicacion, Libro.volumen, Libro.id_libro, MisFavoritos.id_usuario, MisFavoritos.id_lista_favoritos, Libro.imgLibro)

    return render_template("misFavoritos.html", libros = Libros, iduser = current_user.id)

@app.route("/agregarFavorito/<id>")
@login_required
def agregarFavorito(id):
    fav = MisFavoritos(id_libro=id,id_usuario=current_user.id)
    db.session.add(fav)
    db.session.commit()
    return redirect("/catalogo")

@app.route("/quitarFavorito/<id>")
@login_required
def quitarFavorito(id):
    fav = MisFavoritos.query.filter_by(id_lista_favoritos = int(id)).delete()
    db.session.commit()
    return redirect("/MisFavoritos")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)