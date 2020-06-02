from flask import Flask, request, jsonify, url_for, copy_current_request_context
from init_db import initDB
import psycopg2.errors
import uuid
import jwt
import time
import pyqrcode
import os
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_mail import Mail, Message
import threading

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)


app.config['MAIL_SERVER'] = os.getenv('SMTP_SERVER')
app.config['MAIL_PORT'] = os.getenv('SMTP_PORT')
app.config['MAIL_USERNAME'] = os.getenv('EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD')
app.config['MAIL_USE_TLS'] = True



#--- GLOBAL--#

mail = Mail(app)
secret = ""
conn = ""
cur = ""
baseAddr = "" # change if executing from different dir
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

#---UTIL---#


def sendMail(sender, subject, body, recipients):
    msg = Message(subject, sender=sender +
                  f" <{os.getenv('EMAIL')}>", recipients=recipients)
    msg.body = body
    mail.send(msg)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def init():
    global secret, conn, cur
    file = open(baseAddr+"keys.txt", "r")
    data = file.readlines()
    secret = data[0].split()[1]
    conn=initDB()
    if conn is None:
        print("\nXX SERVER STARTUP FAILED XX")
    cur = conn.cursor()
    app.run(host='0.0.0.0', port=8080, debug=True)


def getUUID():
    return str(uuid.uuid4()).replace("-", "")


def token_verify(token, tim):
    try:
        res = jwt.decode(token, secret)
        if "complete" in res:
            if tim == 70 and (time.time()-res["issue_time"]) <= tim:
                return res
            if not res["complete"]:
                return False
        if tim == -1:
            return res
        elif (time.time()-res["issue_time"]) <= tim:
            return res
        else:
            False
    except:
        return False


def org_api_verifiy(id, key):
    cur.execute(
        "select * from org_api where org_id=%s and api_key=%s", (id, key))
    res = cur.fetchall()
    if len(res) == 0:
        return False
    return res[0]

#---UTIL END---#


@app.route('/')
def hello_world():
    return ("Welcome to Auth Service")


@app.route('/org/listing', methods=["POST"])
def org_listing():
    cur.execute("select * from organization")
    res = cur.fetchall()
    resp = {}
    for i in res:
        resp[i[0]] = [i[1], i[4]]
    return jsonify(resp), 200


@app.route('/org/api_listing', methods=["POST"])
def org_api_listing():
    try:
        token = request.json["token"]
        res = token_verify(token, 3600)
        if res:
            cur.execute("select * from org_api where org_id=%s", (res['id'],))
            res = cur.fetchall()
            response = []
            for i in res:
                response.append({
                    "client_id": i[0],
                    "api_key": i[1],
                    "description": i[2]
                })
            return jsonify(response), 200
        else:
            return jsonify(error="unauthorized access"), 401
    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/org/user_listing', methods=["POST"])
def org_user_listing():
    try:
        token = request.json["token"]
        res = token_verify(token, 3600)
        if res:
            cur.execute("select * from users where org_id=%s", (res['id'],))
            res = cur.fetchall()
            response = []
            for i in res:
                response.append({
                    "user_id": i[1],
                    "name": i[2],
                    "email": i[3],
                    "two_fact_enable": i[5]
                })
            return jsonify(response), 200
        else:
            return jsonify(error="unauthorized access"), 401
    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/org/register', methods=["POST"])
# @cross_origin()
def org_register():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        try:
            file = request.files["logo"]
        except:
            file = ""
        # print(name,email,file)
        password = request.form.get("password")
        org_id = getUUID()
        cur.execute("select * from organization where email=%s", (email,))
        res = cur.fetchall()
        if len(res) != 0:
            return jsonify(error="Email Already Registered"), 400
        passd = bcrypt.generate_password_hash(password).decode('utf-8')
        if file != "" and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_name = org_id+"."+filename.rsplit('.', 1)[1].lower()
            file.save(os.path.join(baseAddr, "static/logo/", file_name))
            file_name = url_for('static', filename="logo/"+file_name)
        else:
            file_name = ""
        cur.execute("insert into organization values(%s,%s,%s,%s,%s)",
                    (org_id, name, email, passd, file_name))
        conn.commit()
        response = jsonify(message="ORGANIZATION REGISTERED")
#                response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200

    except psycopg2.errors.UniqueViolation as e:
        return jsonify(error="Email Already Registered"), 400
    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/org/login', methods=["POST"])
def org_login():
    try:
        email = request.json["email"]
        password = request.json["password"]
        cur.execute("select * from organization where email=%s", (email,))
        res = cur.fetchall()
        if len(res) == 0:
            return jsonify(error="incorrect credentials"), 401
        res = res[0]
        if bcrypt.check_password_hash(res[3], password):
            jwt_token = jwt.encode({"id": res[0], "name": res[1], "email": res[2], "issue_time": time.time(
            )}, secret, algorithm="HS256").decode('utf-8')
            return jsonify(token=jwt_token, valid_period="3600"), 200
        else:
            return jsonify(error="incorrect credentials"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/org/forgot_password', methods=["POST"])
def org_forgot_password():
    try:
        email = request.json["email"]
        cur.execute("select * from organization where email=%s", (email,))
        res = cur.fetchall()
        if len(res) == 0:
            return jsonify(error="email doesn't exist"), 400
        cur.execute(
            "delete from code_verify where org_id=%s and email=%s and type=%s", ('0', email, "PASS"))
        conn.commit()
        code = getUUID()[:7]
        tim = time.time()
        cur.execute("insert into code_verify values(%s,%s,%s,%s,%s)",
                    ('0', email, code, tim, "PASS"))
        conn.commit()

        @copy_current_request_context
        def work():
            sendMail("Authenza", "PASSWORD RESET", "CODE : " +
                     code+"\nCode Valid for 5 mins", [email])
        thread1 = threading.Thread(target=work)
        thread1.start()
        return jsonify(message="RESET CODE SENT CHECK EMAIL", valid_period="300"), 200

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/org/reset_password', methods=["POST"])
def org_reset_password():
    try:
        code = request.json["code"]
        email = request.json["email"]
        password = request.json["password"]
        cur.execute("select * from code_verify where org_id=%s and code=%s and email=%s and type=%s",
                    ('0', code, email, "PASS"))
        res = cur.fetchall()
        if len(res) == 0:
            return jsonify(error="wrong data"), 400
        res = res[0]
        cur.execute(
            "delete from code_verify where org_id=%s and code=%s and type=%s", ('0', code, "PASS"))
        if float(time.time())-float(res[3]) > 360:
            conn.commit()
            return jsonify(error="code expired"), 400
        passd = bcrypt.generate_password_hash(password).decode('utf-8')
        cur.execute(
            "update organization set password=%s where email=%s", (passd, email))
        conn.commit()
        return jsonify(message="success"), 200

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/org/self_reset_password', methods=["POST"])
def org_self_reset_password():
    try:
        old_password = request.json["old_password"]
        token = request.json["token"]
        new_password = request.json["new_password"]
        res1 = token_verify(token, 3600)
        if res1:
            cur.execute("select * from organization where email=%s",
                        (res1["email"],))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="incorrect credentials"), 401
            res = res[0]
            if bcrypt.check_password_hash(res[3], old_password):
                passd = bcrypt.generate_password_hash(
                    new_password).decode('utf-8')
                cur.execute(
                    "update organization set password=%s where email=%s", (passd, res1["email"]))
                conn.commit()
                return jsonify(message="success"), 200
            else:
                return jsonify(error="incorrect credentials"), 401
        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/org/create_api_key', methods=["POST"])
def org_api_gen():
    try:
        token = request.json["token"]
        description = request.json["description"]
        res = token_verify(token, 3600)
        if res:
            api_key = getUUID()
            cur.execute("insert into org_api values(%s,%s,%s,%s)",
                        (res['id'], api_key, description, res["name"]))
            conn.commit()
            return jsonify(client_id=res['id'], api_key=api_key), 200
        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/org/force_user_password_reset', methods=["POST"])
def force_user_password_reset():
    try:
        token = request.json["token"]
        email = request.json["email"]
        password = request.json["password"]
        res1 = token_verify(token, 3600)
        if res1:
            cur.execute(
                "select * from users where org_id=%s and email=%s", (res1["id"], email))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="no such user"), 400
            res = res[0]
            passd = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute(
                "update users set password=%s where org_id=%s and email=%s", (passd, res1["id"], email))
            conn.commit()
            return jsonify(message="success"), 200
        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/register', methods=["POST"])
def user_register():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        name = request.json["name"]
        email = request.json["email"]
        password = request.json["password"]
        res = org_api_verifiy(client_id, key)
        if res:
            cur.execute(
                "select * from users where org_id=%s and email=%s", (client_id, email))
            res = cur.fetchall()
            if len(res) != 0:
                return jsonify(error="Email Already Registered"), 400
            u_id = getUUID()
            passd = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute("insert into users values(%s,%s,%s,%s,%s,%s)",
                        (client_id, u_id, name, email, passd, "false"))
            conn.commit()
            return jsonify(message="USER REGISTERED", email_verify="true"), 200
        else:
            return jsonify(error="unauthorized access"), 401

    except psycopg2.errors.UniqueViolation as e:
        return jsonify(error="Email Already Registered"), 400
    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/login', methods=["POST"])
def user_login():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        email = request.json["email"]
        password = request.json["password"]
        res = org_api_verifiy(client_id, key)
        if res:
            cur.execute(
                "select * from users where org_id=%s and email=%s", (client_id, email))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="incorrect credentials"), 401
            res = res[0]
            if bcrypt.check_password_hash(res[4], password):
                # print(res)
                if not res[6]:
                    return jsonify(error="EMAIL NOT VERIFIED", email=email), 403
                if res[5]:
                    cur.execute(
                        "select * from user_2_factor where org_id=%s and u_id=%s", (client_id, res[1]))
                    res1 = cur.fetchall()
                    if len(res1) != 0:
                        res1 = res1[0]
                        if float(time.time())-float(res1[4]) > 60:
                            cur.execute(
                                "delete from user_2_factor where org_id=%s and u_id=%s", (client_id, res[1]))
                            conn.commit()
                        else:
                            return jsonify(error="2FA has been already initialized please complete it first or wait for it to expire"), 400
                    tim = time.time()
                    cur.execute("insert into user_2_factor values(%s,%s,%s,%s,%s)",
                                (client_id, res[1], "LOG", "", tim))
                    conn.commit()
                    jwt_token = jwt.encode({"id": res[1], "name": res[2], "email": res[3],
                                            "issue_time": tim, "complete": False}, secret, algorithm="HS256").decode('utf-8')
                    return jsonify(token=jwt_token, two_factor=True, valid_period="60"), 200
                else:
                    jwt_token = jwt.encode({"id": res[1], "name": res[2], "email": res[3], "issue_time": time.time(
                    ), "complete": True}, secret, algorithm="HS256").decode('utf-8')
                    return jsonify(token=jwt_token, valid_period="3600"), 200
            else:
                return jsonify(error="incorrect credentials"), 401
        else:
            return jsonify(error="unauthorized access"), 401

    except psycopg2.errors.UniqueViolation as e:
        return jsonify(error="2FA has been already initialized please complete it first or wait for it to expire"), 400
    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/init_email_verify', methods=["POST"])
def init_email_verify():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        email = request.json["email"]
        res1 = org_api_verifiy(client_id, key)
        if res1:
            cur.execute(
                "select * from users where org_id=%s and email=%s", (client_id, email))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="email doesn't exist"), 400
            cur.execute("delete from code_verify where org_id=%s and email=%s and type=%s",
                        (client_id, email, "EMAIL"))
            conn.commit()
            code = getUUID()[:7]
            tim = time.time()
            cur.execute("insert into code_verify values(%s,%s,%s,%s,%s)",
                        (client_id, email, code, tim, "EMAIL"))
            conn.commit()
            # print(res1)

            @copy_current_request_context
            def work():
                sendMail(res1[3], "EMAIL VERIFICATION", "CODE : " +
                         code+"\nCode Valid for 5 mins", [email])
            thread1 = threading.Thread(target=work)
            thread1.start()
            return jsonify(message="VERIFICATION CODE SENT CHECK EMAIL", valid_period="300"), 200

        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/email_verify', methods=["POST"])
def email_verify():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        code = request.json["code"]
        email = request.json["email"]
        res1 = org_api_verifiy(client_id, key)
        if res1:
            cur.execute("select * from code_verify where org_id=%s and code=%s and email=%s and type=%s",
                        (client_id, code, email, "EMAIL"))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="wrong code"), 400
            res = res[0]
            cur.execute(
                "delete from code_verify where org_id=%s and code=%s and type=%s", (client_id, code, "EMAIL"))
            if float(time.time())-float(res[3]) > 360:
                conn.commit()
                return jsonify(error="code expired"), 400
            cur.execute(
                "update users set verified=%s where org_id=%s and email=%s", (True, client_id, email))
            conn.commit()
            return jsonify(message="success"), 200

        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/forgot_password', methods=["POST"])
def forgot_password():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        email = request.json["email"]
        res1 = org_api_verifiy(client_id, key)
        if res1:
            cur.execute(
                "select * from users where org_id=%s and email=%s", (client_id, email))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="email doesn't exist"), 400
            res = res[0]
            if not res[6]:
                return jsonify(error="EMAIL NOT VERIFIED", email=email), 403
            cur.execute(
                "delete from code_verify where org_id=%s and email=%s and type=%s", (client_id, email, "PASS"))
            conn.commit()
            code = getUUID()[:7]
            tim = time.time()
            cur.execute("insert into code_verify values(%s,%s,%s,%s,%s)",
                        (client_id, email, code, tim, "PASS"))
            conn.commit()
            # print(res1)

            @copy_current_request_context
            def work():
                sendMail(res1[3], "PASSWORD RESET", "CODE : " +
                         code+"\nCode Valid for 5 mins", [email])
            thread1 = threading.Thread(target=work)
            thread1.start()
            return jsonify(message="RESET CODE SENT CHECK EMAIL", valid_period="300"), 200

        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/reset_password', methods=["POST"])
def reset_password():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        code = request.json["code"]
        email = request.json["email"]
        password = request.json["password"]
        res1 = org_api_verifiy(client_id, key)
        if res1:
            cur.execute("select * from code_verify where org_id=%s and code=%s and email=%s and type=%s",
                        (client_id, code, email, "PASS"))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="wrong code"), 400
            res = res[0]
            cur.execute(
                "delete from code_verify where org_id=%s and code=%s and type=%s", (client_id, code, "PASS"))
            if float(time.time())-float(res[3]) > 360:
                conn.commit()
                return jsonify(error="code expired"), 400
            passd = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute(
                "update users set password=%s where org_id=%s and email=%s", (passd, client_id, email))
            conn.commit()
            return jsonify(message="success"), 200

        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/self_reset_password', methods=["POST"])
def user_self_reset_password():
    try:
        old_password = request.json["old_password"]
        token = request.json["token"]
        new_password = request.json["new_password"]
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        res = org_api_verifiy(client_id, key)
        res2 = token_verify(token, 3600)
        if res:
            if not res2:
                return jsonify(error="token invalid"), 401
            cur.execute(
                "select * from users where org_id=%s and email=%s", (client_id, res2["email"]))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="incorrect credentials"), 401
            res = res[0]
            if bcrypt.check_password_hash(res[4], old_password):
                passd = bcrypt.generate_password_hash(
                    new_password).decode('utf-8')
                cur.execute("update users set password=%s where org_id=%s and email=%s",
                            (passd, client_id, res2["email"]))
                conn.commit()
                return jsonify(message="success"), 200
            else:
                return jsonify(error="incorrect credentials"), 401
        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/two_factor/enable', methods=["POST"])
def user_enable_two_factor():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        token = request.json["token"]
        res = org_api_verifiy(client_id, key)
        res2 = token_verify(token, 3600)
        if res:
            if not res2:
                return jsonify(error="token invalid"), 401
            # print(res2)
            cur.execute(
                "select * from users where org_id=%s and email=%s", (client_id, res2["email"]))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="user has been removed"), 401
            res = res[0]
            if res[5]:
                return jsonify(error="two factor already enabled"), 400
            else:
                cur.execute(
                    "select * from user_2_factor where org_id=%s and u_id=%s", (client_id, res[1]))
                res1 = cur.fetchall()
                if len(res1) != 0:
                    res1 = res1[0]
                    if float(time.time())-float(res1[4]) > 300:
                        img = baseAddr+"static/images/"+res1[3]+".png"
                        img = os.path.join(app.root_path, img)
                        os.remove(img)
                        cur.execute(
                            "delete from user_2_factor where org_id=%s and u_id=%s", (client_id, res[1]))
                        conn.commit()
                    else:
                        return jsonify(error="2FA activation already initialized please complete it first or cancel it"), 400
                qr_id = getUUID()
                tim = time.time()
                jwt_token = jwt.encode({"client_id": client_id, "api_key": key, "u_id": res[1], "name": res[
                                       2], "email": res[3], "qr": qr_id, "issue_time": tim}, secret, algorithm="HS256").decode('utf-8')
                qr = pyqrcode.create(jwt_token)
                qr.png(baseAddr+"static/images/"+qr_id+".png", scale=3)
                cur.execute("insert into user_2_factor values(%s,%s,%s,%s,%s)",
                            (client_id, res[1], "REG", qr_id, tim))
                conn.commit()
                return jsonify(qr=url_for('static', filename="images/"+qr_id+".png"), valid_period="300"), 200
        else:
            return jsonify(error="unauthorized access"), 401

    except psycopg2.errors.UniqueViolation as e:
        return jsonify(error="2FA has been already initialized please complete it first or cancel it"), 400
    except KeyError as e:
        print(e)
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/two_factor/disable', methods=["POST"])
def user_disable_two_factor():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        token = request.json["token"]
        password = request.json["password"]
        res = org_api_verifiy(client_id, key)
        res2 = token_verify(token, 3600)
        if res:
            if not res2:
                return jsonify(error="token invalid"), 401
            cur.execute(
                "select * from users where org_id=%s and email=%s", (client_id, res2["email"]))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="user has been removed"), 401
            res = res[0]
            if bcrypt.check_password_hash(res[4], password):
                if not res[5]:
                    return jsonify(error="two factor already disabled"), 400
                cur.execute("update users set two_fact=%s where org_id=%s and email=%s",
                            (False, client_id, res2["email"]))
                conn.commit()
                return jsonify(message="success"), 200
            else:
                return jsonify(error="incorrect password"), 401
        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/two_factor/confirm_reg', methods=["POST"])
def two_factor_confirm_reg():
    try:
        token = request.json["token"]
        res = token_verify(token, 300)
        if not res:
            return jsonify(error="token invalid"), 401
        client_id = res["client_id"]
        key = res["api_key"]
        res2 = org_api_verifiy(client_id, key)
        if not res2:
            return jsonify(error="unauthorized access"), 401
        cur.execute("select * from users where org_id=%s and id=%s",
                    (client_id, res["u_id"]))
        res2 = cur.fetchall()
        res2 = res2[0]
        if res2[5]:
            return jsonify(error="two factor already enabled"), 400
        cur.execute("select * from user_2_factor where org_id=%s and u_id=%s and qr=%s",
                    (client_id, res["u_id"], res["qr"]))
        res2 = cur.fetchall()
        if len(res2) == 0:
            return jsonify(error="two factor already enabled"), 400
        img = baseAddr+"static/images/"+res["qr"]+".png"
        img = os.path.join(app.root_path, img)
        os.remove(img)
        cur.execute("update users set two_fact=%s where org_id=%s and id=%s",
                    (True, client_id, res["u_id"]))
        cur.execute("delete from user_2_factor where org_id=%s and u_id=%s and qr=%s",
                    (client_id, res["u_id"], res["qr"]))
        conn.commit()
        return jsonify(message="success"), 200
    except KeyError as e:
        print(e)
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/two_factor/active_check', methods=["POST"])
def two_factor_active_check():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        token = request.json["token"]
        res = org_api_verifiy(client_id, key)
        res2 = token_verify(token, 3600)
        if res:
            if not res2:
                return jsonify(error="token invalid"), 401
            # print(res2)
            cur.execute(
                "select * from users where org_id=%s and email=%s", (client_id, res2["email"]))
            res = cur.fetchall()
            if len(res) == 0:
                return jsonify(error="user has been removed"), 401
            res = res[0]
            if res[5]:
                return jsonify(two_factor=True), 200
            else:
                return jsonify(two_factor=False), 200
        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        print(e)
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/two_factor/confirm_login', methods=["POST"])
def two_factor_confirm_login():
    try:
        token = request.json["token"]
        res = token_verify(token, -1)
        if not res:
            return jsonify(error="token invalid"), 401
        client_id = res["client_id"]
        key = res["api_key"]
        res2 = org_api_verifiy(client_id, key)
        if not res2:
            return jsonify(error="unauthorized access"), 401
        cur.execute("select * from users where org_id=%s and id=%s",
                    (client_id, res["u_id"]))
        res2 = cur.fetchall()
        res2 = res2[0]
        if not res2[5]:
            return jsonify(error="two factor not enabled"), 400
        cur.execute("select * from user_2_factor where org_id=%s and u_id=%s and type=%s",
                    (client_id, res["u_id"], "LOG"))
        res2 = cur.fetchall()
        if len(res2) == 0:
            return jsonify(error="no 2FA request found"), 400
        res2 = res2[0]
        if float(time.time())-float(res2[4]) > 60:
            return jsonify(error="expired restart 2FA"), 400
        cur.execute("delete from user_2_factor where org_id=%s and u_id=%s and type=%s",
                    (client_id, res["u_id"], "LOG"))
        conn.commit()
        return jsonify(message="success"), 200
    except KeyError as e:
        print(e)
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/two_factor/cancel_reg', methods=["POST"])
def two_factor_cancel_reg():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        token = request.json["token"]
        res = org_api_verifiy(client_id, key)
        res2 = token_verify(token, 3600)
        if res:
            if not res2:
                return jsonify(error="token invalid"), 401
            cur.execute("select * from user_2_factor where org_id=%s and u_id=%s and type=%s",
                        (client_id, res2["id"], "REG"))
            res1 = cur.fetchall()
            if len(res1) == 0:
                return jsonify(error="no active 2FA flow found"), 400
            res1 = res1[0]
            img = baseAddr+"static/images/"+res1[3]+".png"
            img = os.path.join(app.root_path, img)
            os.remove(img)
            cur.execute("delete from user_2_factor where org_id=%s and u_id=%s and type=%s",
                        (client_id, res2["id"], "REG"))
            conn.commit()
            return jsonify(message="success"), 200
        else:
            return jsonify(error="unauthorized access"), 401
    except KeyError as e:
        print(e)
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/two_factor/check_login', methods=["POST"])
def two_factor_check_login():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        token = request.json["token"]
        res = org_api_verifiy(client_id, key)
        res2 = token_verify(token, 70)
        if res:
            if not res2:
                return jsonify(error="token invalid"), 401
            cur.execute("select * from user_2_factor where org_id=%s and u_id=%s and type=%s",
                        (client_id, res2["id"], "LOG"))
            res1 = cur.fetchall()
            if len(res1) == 0:
                res2['complete'] = True
                jwt_token = jwt.encode(
                    res2, secret, algorithm="HS256").decode('utf-8')
                return jsonify(token=jwt_token, valid_period="3600"), 200
            return jsonify(message="2FA not complete"), 200
        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        print(e)
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify(error="malformed data"), 400


@app.route('/user/token_verify', methods=["POST"])
def user_token_verify():
    try:
        client_id = request.json["client_id"]
        key = request.json["api_key"]
        token = request.json["token"]
        res = org_api_verifiy(client_id, key)
        res2 = token_verify(token, 3600)
        if res:
            if not res2:
                return jsonify(error="token invalid"), 401
            else:
                return jsonify(message="valid token"), 200
        else:
            return jsonify(error="unauthorized access"), 401

    except KeyError as e:
        print(e)
        return jsonify(error="missing data"), 400
    except Exception as e:
        print(e)
        return jsonify(error="malformed data"), 400


if __name__ == '__main__':
    init()
    
