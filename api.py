import os

from flask import Flask, jsonify, request, Response
from flask_sqlalchemy import SQLAlchemy
import dotenv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from marshmallow import Schema, fields
from apifairy import APIFairy, response
from flask_marshmallow import Marshmallow


dotenv.load_dotenv()


db_user = os.environ.get('DB_USERNAME')
db_pass = os.environ.get('DB_PASSWORD')
db_hostname = os.environ.get('DB_HOSTNAME')
db_name = os.environ.get('DB_NAME')


DB_URI = 'mysql+pymysql://{db_username}:{db_password}@{db_host}/{database}'.format(db_username=db_user, db_password=db_pass, db_host=db_hostname, database=db_name)


engine = create_engine(DB_URI, echo=True)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['APIFAIRY_TITLE'] = 'Docs created with APIFairy'
app.config['APIFAIRY_VERSION'] = '0.9.1'
db = SQLAlchemy(app)
ma = Marshmallow(app)
apifairy = APIFairy(app)


class UserSchema(ma.Schema):
    id = ma.Int()
    name = ma.Str()
    email = ma.Str()
    age = ma.Int()
    cellphone = ma.Str()


class HealthCheck(ma.Schema):
    pass


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    cellphone = db.Column(db.String(13), unique=True, nullable=False)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class StudentSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Str()
    age = fields.Integer()
    cellphone = fields.Str()


@app.route('/', methods=['GET'])
def home():
    return '<p>Hello from students API!</p>', 200


@app.route('/api', methods=['GET'])
def api_main():
    """
    /api
    Returns link to documentation.
    """
    return '<h1><p  style=text-align:center; width:100%><a href=/docs>Read the docs</a></p></h1>'


@app.route('/api/students', methods=['GET'])
@response(UserSchema)
def get_all_students():
    """
    /api/students
    Get list of students.
    """
    students = Student.get_all()
    student_list = StudentSchema(many=True)
    response_to_client = student_list.dump(students)
    return jsonify(response_to_client), 200


@app.route('/api/students/get/<int:id>', methods=['GET'])
@response(UserSchema)
def get_student(id):
    """
    /api/students/get/{id}
    Get students data.
    """
    student_info = Student.get_by_id(id)
    serializer = StudentSchema()
    response_to_client = serializer.dump(student_info)
    return jsonify(response_to_client), 200


@app.route('/api/students/add', methods=['POST'])
@response(UserSchema, 201)
def add_student():
    """
    /api/students/add
    Add new student to DB.
    """
    json_data = request.get_json()
    new_student = Student(
        name=json_data.get('name'),
        email=json_data.get('email'),
        age=json_data.get('age'),
        cellphone=json_data.get('cellphone')
    )
    new_student.save()
    serializer = StudentSchema()
    data = serializer.dump(new_student)
    return jsonify(data), 201


@app.route('/api/students/modify/<int:id>', methods=['PATCH'])
@response(UserSchema)
def modify_fields(id):
    """
    /api/students/modify/{id}
    Modify students data.
    """
    json_data = request.get_json()
    cur_student = Student.get_by_id(id)
    if json_data.get('name'):
        cur_student.name = json_data.get('name')
    if json_data.get('email'):
        cur_student.email = json_data.get('email')
    if json_data.get('age'):
        cur_student.age = json_data.get('age')
    if json_data.get('cellphone'):
        cur_student.age = json_data.get('cellphone')
    cur_student.save()
    serializer = StudentSchema()
    data = serializer.dump(cur_student)
    return jsonify(data), 200


@app.route('/api/students/change/<int:id>', methods=['PUT'])
@response(UserSchema)
def modify_all_fields(id):
    """
    /api/students/change/{id}
    Change student data.
    """
    json_data = request.get_json()
    cur_student = Student.get_by_id(id)
    if json_data.get('name'):
        cur_student.name = json_data.get('name')
    if json_data.get('email'):
        cur_student.email = json_data.get('email')
    if json_data.get('age'):
        cur_student.age = json_data.get("age")
    if json_data.get('cellphone'):
        cur_student.age = json_data.get('cellphone')
    cur_student.save()
    serializer = StudentSchema()
    data = serializer.dump(cur_student)
    return jsonify(data), 200


@app.route('/api/students/remove/<int:id>', methods=['DELETE'])
@response(UserSchema)
def remove_student(id):
    """
    /api/students/remove/{id}
    Remove student from database.
    """
    guide = Student.query.get(id)
    db.session.delete(guide)
    db.session.commit()
    return "Record deleted."


@app.route('/api/health-check/ok', methods=['GET'])
@response(HealthCheck)
def health_ok():
    """/api/health-check/ok
    The health check endpoint enables the health of a service instance to be periodically tested.
    """
    return Response("{'some':'json'}", status=200, mimetype='application/json')


@app.route('/api/health-check/bad', methods=['GET'])
@response(HealthCheck, 500)
def health_bad():
    """
    /api/health-check/bad
    The health check endpoint enables the health of a service instance to be periodically tested.
    """
    return Response("{'some':'json'}", status=500, mimetype='application/json')


if __name__ == '__main__':
    if not database_exists(engine.url):
        create_database(engine.url)
    db.create_all()
    app.run(debug=True)
