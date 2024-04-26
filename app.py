
from flask import Flask,render_template,request,redirect,session,flash,url_for,jsonify
import os
import pymysql
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'healthcare',
}

def connect():
        """ Connect to the PostgreSQL database server """
        conn = None
        try:
            # connect to the PostgreSQL server
            #self.log.info('Connecting to the PostgreSQL database...')
            conn = pymysql.connect(**db_config)
        except (Exception) as error:
            #self.log.error(error)
            raise error
        return conn



def single_insert(insert_req):
        """ Execute a single INSERT request """
        conn = None
        cursor = None
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute(insert_req)
            conn.commit()
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            if conn is not None:
                conn.rollback()
            raise error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
def execute(req_query):
        """ Execute a single request """
        """ for Update/Delete request """
        conn = None
        cursor = None
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute(req_query)
            conn.commit()
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            if conn is not None:
                conn.rollback()
            raise error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
def executeAndReturnId( req_query):
        """ Execute a single request and return id"""
        """ for insert request """
        conn = None
        cursor = None
        try:
            conn =connect()
            cursor = conn.cursor()
            cursor.execute(req_query)
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            last_inserted_id = cursor.fetchone()[0]
            return last_inserted_id
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            if conn is not None:
                conn.rollback()
            raise error
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
def fetchone( get_req):
        conn=None
        cur=None
        try:
            conn = connect()
            cur = conn.cursor()
            cur.execute(get_req)
            data = cur.fetchone()
            return data
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            raise error
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
def fetchall(get_req):
        conn = None
        cur = None
        try:
            conn = connect()
            cur = conn.cursor()
            cur.execute(get_req)
            data = cur.fetchall()
            return data
        except (Exception) as error:
            #self.log.error("Error: %s" % error)
            raise error
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()



@app.route("/")
def index():
    return render_template("index.html")

def authenticate(username, password):
    """ Authenticate user """
    
    query="SELECT * FROM `login` WHERE `name`='{}' AND `password`='{}'"
  
    user = fetchone(query.format(username, password))
    
    return user



@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']
    user = authenticate(username, password)
    print("user",user)
    if user:
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        if user[3] == 'admin':
            return redirect(url_for('admin_home'))
        elif user[3] == 'user':
            return redirect(url_for('user_home'))
        elif user[3] == 'staff':
            return redirect(url_for('staff_home'))
        elif user[3] == 'Dietician':
            return redirect(url_for('dietician_home'))
    else:
        flash('Invalid Username or Password')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect to the index page
    return redirect(url_for('index'))

@app.route("/admin")
def admin_home():
    # Add admin home logic here
    return render_template("Admin/index.html")

@app.route("/user")
def user_home():
    # Add user home logic here
    return render_template("User/index.html")

@app.route("/staff")
def staff_home():
    login_id = session.get('user_id')
    print("login_id",login_id) 
    query="SELECT * FROM `medicine` WHERE `staff_id`='{}'"
    medicine_data = fetchall(query.format(login_id))
    # Add staff home logic here
    return render_template("Staff/index.html",medicine_data=medicine_data)

@app.route("/dietician")
def dietician_home():
    Uid_dietician = session.get('user_id')  # Assuming you have a session object
    place_query = "SELECT login.name FROM medical_report INNER JOIN login ON medical_report.user_id = login.id AND medical_report.dietician_id = '{}'"
    place_results = fetchall(place_query.format(Uid_dietician))
    print("place_result",place_results)
    place_data = [row[0] for row in place_results]

    message_query = "SELECT * FROM `diet` WHERE `dietician_id` = '{}' AND `type` = 'user_to_dietician'"
    message_results = fetchall(message_query.format(Uid_dietician))
    message_data = [row['message'] for row in message_results]
    print("message_data",message_data)
    
    return render_template("Dietician/index.html",place_data=place_data, message_data=message_data)


        
        
        
        
@app.route('/add-caretaker', methods=['GET', 'POST'])
def add_caretaker():
    if request.method == 'POST':
        # Handle form submission
        name = request.form['username']
        email = request.form['email']
        address = request.form['address']
        qualification = request.form['qualification']
        caretaker_type = request.form['type']
        zip_code = request.form['zip']

        if request.form.get('hid')!= 'None':
            # If hid is present, it means it's an update operation
            hid = request.form['hid']
            print("ffff")
            print("hid",hid)
            query = "UPDATE caretaker SET name='{}', email='{}', address='{}', qualification='{}', type='{}', zip='{}' WHERE id='{}'"
            execute(query.format(name, email, address, qualification, caretaker_type, zip_code, hid))
            
           
            return redirect(url_for('caretaker_data'))
        else:
            print("hhh")
            query = "INSERT INTO caretaker (name, email, address, qualification, type, zip) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')"
            datain=single_insert(query.format(name, email, address, qualification, caretaker_type, zip_code))
            #execute(sql, (name, email, address, qualification, type, zip))


            return redirect(url_for('caretaker_data'))
    else:
      
       if request.method == 'GET':
            up_id = request.args.get('up_id')
            row = None
            #u_name = u_email = u_address = u_qualification = u_type = u_zip = ''

            if up_id:
                query = "SELECT * FROM caretaker WHERE id='{}'"
           
           
                row=fetchone( query.format (up_id))
                print("row",row)
                #if row:
                    #u_name, u_email, u_address, u_qualification, u_type, u_zip = row

            return render_template('Admin/add-caretaker.html', caretaker=row)
    return render_template('Admin/add-caretaker.html', caretaker=row)
        
        
        



@app.route('/caretaker-data')
def caretaker_data():
    
   
    query = "SELECT * FROM caretaker"
    caretakers =fetchall(query.format())
    print("caretakers",caretakers)
    return render_template('Admin/caretaker-data.html', caretakers=caretakers)



@app.route('/delete-caretaker/<int:id>')
def delete_caretaker(id):
    print("id",id)
    query="DELETE FROM caretaker WHERE id = '{}'"
    data=execute(query.format(id))
    print("deletedata",data)
    return redirect(url_for('caretaker_data'))


@app.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if request.method == 'POST':
        
        name = request.form['username']
        email = request.form['email']
        address = request.form['address']
        qualification = request.form['qualification']
        password=request.form['password']
        zip_code = request.form['zip']
       

        # Check if it's an update operation
        if request.form.get('hid'):
            hid = request.form['hid']
            # Perform update operation
            query = "UPDATE staff SET name='{}', email='{}',address='{}',qualification='{}',password='{}',zip='{}' WHERE id='{}'"
            execute(query.format(name, email,address,qualification,password,zip_code, hid))
            return redirect(url_for('staff_data'))
        else:
            # Perform insert operation
            login_id = session.get('user_id') 
            print("login_id",login_id)
            query = "INSERT INTO staff (login_id,name, email,address,qualification,password,zip) VALUES ('{}', '{}','{}','{}', '{}', '{}', '{}')"
            datain=single_insert(query.format(login_id,name, email,address,qualification,password,zip_code))
            return redirect(url_for('staff_data'))
    else:
        # Handle GET request
        up_id = request.args.get('up_id')
        row = None
        if up_id:
            query = "SELECT * FROM staff WHERE id='{}'"
            row = fetchone(query.format(up_id))
        return render_template('Admin/add_staff.html', staff=row)
    return render_template('Admin/add_staff.html', staff=row)


@app.route('/staff_data')
def staff_data():
    # Retrieve staff data from database
    query = "SELECT * FROM staff"
    staff_data = fetchall(query)
    return render_template('Admin/staff_data.html', staff_data=staff_data)


@app.route('/delete_staff/<int:id>')
def delete_staff(id):
    query = "DELETE FROM staff WHERE id = '{}'"
    execute(query.format(id))
    return redirect(url_for('staff_data'))

@app.route('/add_dietician', methods=['GET', 'POST'])
def add_dietician():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        password = request.form['password']
        address = request.form['address']
        qualification = request.form['qualification']
        zip_code = request.form['zip']

        if request.form.get('hid') != 'None':
            hid = request.form['hid']
            query = "UPDATE dietician SET name='{}', email='{}', password='{}', address='{}', qualification='{}', zip='{}' WHERE id='{}'"
            execute(query.format(name, email, password, address, qualification, zip_code, hid))
            return redirect(url_for('dietician_data'))
        else:
            login_id = session.get('user_id') 
            print("login_id",login_id)
            query = "INSERT INTO dietician (login_id,name, email, password, address, qualification, zip) VALUES ('{}','{}', '{}', '{}', '{}', '{}', '{}')"
            execute(query.format(login_id,name, email, password, address, qualification, zip_code))
            return redirect(url_for('dietician_data'))
    else:
        up_id = request.args.get('up_id')
        row = None

        if up_id:
            query = "SELECT * FROM dietician WHERE id='{}'"
            row = fetchone(query.format(up_id))

        return render_template('Admin/add-dietician.html', dietician=row)

@app.route('/dietician_data')
def dietician_data():
    query = "SELECT * FROM dietician"
    dieticians = fetchall(query.format())
    return render_template('Admin/dietician-data.html', dieticians=dieticians)


@app.route('/delete_dietician/<int:id>')
def delete_dietician(id):
    print("id",id)
    query="DELETE FROM dietician WHERE id = '{}'"
    data=execute(query.format(id))
    print("deletedata",data)
    return redirect(url_for('dietician_data'))



@app.route('/add_hospital', methods=['GET', 'POST'])
def add_hospital():
    if request.method == 'POST':
        name = request.form['hospitalname']
        place = request.form['place']
        location = request.form['location']
        

        if request.form.get('hid') != 'None':
            hid = request.form['hid']
            query = "UPDATE hospital SET name='{}', place='{}', Location='{}' WHERE id='{}'"
            execute(query.format(name, place, location,hid))
            return redirect(url_for('hospital_data'))
        else:
            #login_id = session.get('user_id') 
            #print("login_id",login_id)
            query = "INSERT INTO hospital (name,place, Location) VALUES ('{}', '{}', '{}')"
            execute(query.format(name, place, location))
            return redirect(url_for('hospital_data'))
    else:
        up_id = request.args.get('up_id')
        row = None

        if up_id:
            query = "SELECT * FROM hospital WHERE id='{}'"
            row = fetchone(query.format(up_id))

        return render_template('Admin/add-hospital.html', hospital=row)

@app.route('/hospital_data')
def hospital_data():
    query = "SELECT * FROM hospital"
    hospitals = fetchall(query.format())
    return render_template('Admin/hospital-data.html', hospitals=hospitals)


@app.route('/delete_hospital/<int:id>')
def delete_hospital(id):
    print("id",id)
    query="DELETE FROM hospital WHERE id = '{}'"
    data=execute(query.format(id))
    print("deletedata",data)
    return redirect(url_for('hospital_data'))

@app.route("/medicalreport_data")
def medical_report_data():
    query = """
    SELECT medical_report.id, medical_report.report, login.name
    FROM medical_report
    INNER JOIN login ON medical_report.user_id = login.id
    """
    medical_reports = fetchall(query)
    print("medical report",medical_reports)
    query = "SELECT * FROM `login` WHERE `category`='Dietician'"
    dieticians = fetchall(query.format())
    print("dieticians",dieticians)
    return render_template("Admin/medicalreport-data.html", medical_reports=medical_reports, dieticians=dieticians)

@app.route("/user_data")
def user_data():
    query = "SELECT * FROM `login` WHERE `category`='user'"
    users = fetchall(query.format())
    return render_template("Admin/user-data.html", users=users)



# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     if request.method == 'GET':
#         up_id = request.args.get('up_id')
#         #u_name = u_email = u_password = ''

#         if up_id:
            
#             query = "SELECT * FROM `login` WHERE `id`='{}'"
            
#             user =fetchone(query.format(up_id))
#             print("userdaa",user)
#             # if user:
                
#             #     u_name = user[1]
#             #     u_email = user[2]
#             #     u_password = user[3]
            

#         return render_template('Admin/profile.html', users=user)
#     elif request.method == 'POST':
#         # Handle form submission for updating profile
        
#         #up_id = request.form.get('hid')
#         u_name = request.form.get('fullName')
#         u_email = request.form.get('email')
#         u_password = request.form.get('password')
#         if request.form.get('hid') != 'None':
#             hid = request.form['hid']
#             query = "UPDATE login SET name='{}', email='{}', password='{}' WHERE id='{}'"
#             execute(query.format(u_name, u_email, u_password,hid))
#             return redirect(url_for('profile'))




@app.route('/submit_diet', methods=['POST'])
def submit_diet():
    if request.method == 'POST' and 'signin' in request.form:
        message = request.form['message']
        type = 'dietician_to_user'
        dietician_id = session.get('user_id')

        query = "SELECT * FROM `medical_report` WHERE `dietician_id` = '{}'"
        row = fetchone(query.format(dietician_id))
        print(row,"row")
        
        if row:
            user_id = row[1]
            print("user_id",user_id)
            query = "INSERT INTO `diet`(`user_id`, `message`, `dietician_id`, `type`) VALUES ('{}', '{}', '{}', '{}')"
            datain=single_insert(query.format(user_id, message, dietician_id, type))
           
            return redirect(url_for('index'))
        else:
            return "Error: No medical report found for this dietician"

@app.route('/patient_data')
def patient_data():
    
    user_id=session.get('user_id')
    query = "SELECT medical_report.report, login.name FROM medical_report INNER JOIN login ON medical_report.user_id = login.id WHERE medical_report.dietician_id = '{}'"
    
    place_data =fetchall(query.format (user_id))
    print("place_data",place_data)

    if place_data:
        return render_template('Dietician/patient-data.html', place_data=place_data)
    else:
        return render_template('Dietician/patient-data.html', place_data=None)


UPLOAD_FOLDER = 'path_to_your_upload_folder'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/medicine_action', methods=['POST'])
def medicine_action():
    if request.method == 'POST':
        medicinename = request.form['medicinename']
        rate = request.form['rate']
        stock = request.form['stock']
        brand = request.form['brand']
        #staff_id = session['uid']  # Assuming you store user id in session
        staff_id  = session.get('user_id')
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            if request.form.get('hid'):
                hid = request.form['hid']
                query = "UPDATE medicine SET name='{}', rate='{}', stock='{}', brand='{}' WHERE id='{}'"
                execute(query.format(medicinename, rate, stock, brand, hid))
                
                flash('Medicine updated successfully')
                return redirect(url_for('medicine_data'))

            else:
                query = "INSERT INTO medicine (name, rate, file, stock, brand, staff_id) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')"
                datain=single_insert(query.format(medicinename, rate, file_path, stock, brand, staff_id))
                
                flash('Medicine added successfully')
                return redirect(url_for('medicine_data'))

    return redirect(url_for('medicine_data'))


@app.route('/medicine_data')
def medicine_data():
    login_id = session.get('user_id')
    query = "SELECT * FROM `medicine` WHERE `staff_id`='{}'"
    medicine_data = fetchall(query.format(login_id))
    print("medicine_data", medicine_data)
    return render_template("Staff/medicine-data.html", medicine_data=medicine_data)


@app.route('/delete_medicine/<int:id>')
def delete_medicine(id):
    query="DELETE FROM `medicine` WHERE `id`='{}'"
    data=execute(query.format(id))
    return redirect(url_for('medicine_data'))

@app.route('/hospitals')
def hospital():
   
    query="SELECT * FROM `hospital`"
    hospitals = fetchall(query.format())
    return render_template('User/hospitals.html',hospitals=hospitals)

@app.route('/get_hospitals', methods=['POST'])
def get_hospitals():
    location = request.form['location']
    
    query="SELECT * FROM hospital WHERE Location = '{}'"
    hospitals = fetchall(query.format(location))
   
    return jsonify(hospitals)


@app.route('/medical_report')
def medical_report():
    
    user_id  = session.get('user_id')
    print("user_id",user_id)
    
    query="SELECT login.name FROM medical_report INNER JOIN login ON medical_report.dietician_id = login.id AND medical_report.user_id = '{}'"
   
    result = fetchone(query.format(user_id))
    print(result,"result")
    dietician_name = result[0]
    return render_template('User/medical_report.html', dietician_name=dietician_name)



@app.route('/submit_medical_report', methods=['POST'])
def submit_medical_report():
   

    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['pdf_file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        user_id  = session.get('user_id')
        query = "INSERT INTO medical_report (user_id, report) VALUES ('{}', '{}')"
        execute(query.format(user_id, filename))
        

        return redirect(url_for('medical_report_success'))
@app.route('/caretaker')
def caretaker():
    # Get the user ID from the session
    user_id = session.get('user_id')
    
    
    if user_id is None:
        return "User ID not found in session."
    
    # Execute the SQL query to retrieve the caretaker information
    query = "SELECT caretaker.name, caretaker.type FROM caretaker INNER JOIN login ON login.caretaker_id = caretaker.id WHERE login.id = '{}'"
    result = fetchone(query.format(user_id))
   
   
    if result:
        caretaker_name, caretaker_type = result
        caretaker_info =  {"name": caretaker_name, "type": caretaker_type}
        print("caretaker_info",caretaker_info)
        
    else:
        caretaker_info = "No caretaker found"
    
    sql = "SELECT * FROM caretaker"
    caretaker_details = fetchall(sql.format())

    return render_template('User/caretaker.html', caretaker_info=caretaker_info,caretaker_details=caretaker_details)


if __name__ == '__main__':
    app.run(debug=True)
