from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'beware'  # Add your secret key here  

# Database connection configuration
db = mysql.connector.connect(
    host='localhost',
    user='root',  # Add your username here
    password='blowwind25',  # Add your password here
    database='ams'  # Add your db name here
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        cur = db.cursor()
        if role == 'teacher':
            cur.execute("SELECT * FROM teachers WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            if user:
                session['loggedin'] = True
                session['username'] = user[0]
                session['role'] = 'teacher'
                return redirect('/teacher/dashboard')
            else:
                error = 'Invalid login credentials.'
                return render_template('login.html', error=error)
        elif role == 'admin':
            cur.execute("SELECT * FROM admins WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            if user:
                session['loggedin'] = True
                session['username'] = user[0]
                session['role'] = 'admin'
                return redirect('/admin/admin_dashboard')
            else:
                error = 'Invalid login credentials'
                return render_template('login.html', error=error)
        cur.close()
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        cursor = db.cursor()
        query = "SELECT username FROM teachers WHERE username = %s"
        cursor.execute(query, (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            error_message = "Username already exists. Please choose a different one."
            return render_template('teacher_registration.html', error=error_message)
        insert_query = "INSERT INTO teachers (teacher_name, username, password, email, phone) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (name, username, password, email, phone))
        db.commit()
        cursor.close()
        return render_template('teacher_registration.html', message="Teacher successfully registered.")
    return render_template('teacher_registration.html')

@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == "POST":
        student_id = request.form['student_id']
        name = request.form['name']
        class_sec = request.form['class_sec']
        email = request.form['email']
        phone = request.form['phone']
        cursor = db.cursor()
        query = "SELECT student_id FROM students WHERE student_id = %s"
        cursor.execute(query, (student_id,))
        existing_user = cursor.fetchone()
        if existing_user:
            error_message = "Invalid student_id"
            return render_template('student_registration.html', error=error_message)
        insert_query = "INSERT INTO students (student_id, student_name, class_sec, email, phone) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (student_id, name, class_sec, email, phone))
        db.commit()
        cursor.close()
        return render_template('student_registration.html', message="Student successfully registered.")
    return render_template('student_registration.html')

@app.route('/get_student', methods=['POST', 'GET'])
def get_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cur.fetchone()
        cur.close()
        if student:
            message = "Fetched student details"
            return render_template('update_student.html', student=student, msg=message)
        else:
            error = "Invalid Student ID"
            return render_template('update_student.html', err=error)
    return render_template('update_student.html') 

@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        new_name = request.form['new_name']
        new_email = request.form['new_email']
        new_phone = request.form['new_phone']
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student = cur.fetchone()
        if student:
            cur.execute("UPDATE students SET student_name = %s, email = %s, phone = %s WHERE student_id = %s",
                       (new_name, new_email, new_phone, student_id))
            db.commit()
            message = f"Student ID {student_id} details have been successfully updated."
            cur.close()
            return render_template('update_student.html', student=student, message=message)
        else:
            error = "Invalid Student ID"
            cur.close()
            return render_template('update_student.html', error=error)
    return render_template('update_student.html')

@app.route('/teacher/teacher_profile')
def teacher_profile():
    if 'loggedin' in session and session['role'] == 'teacher':
        cur = db.cursor()
        cur.execute("SELECT teacher_name, email, phone FROM teachers WHERE username = %s", (session['username'],))
        profile_data = cur.fetchone()
        cur.close()
        return render_template('teacher_profile.html', profile_data=profile_data)
    else:
        return redirect('/')

@app.route('/teacher/update_profile', methods=['POST'])
def update_profile():
    if 'loggedin' in session and session['role'] == 'teacher':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        cur = db.cursor()
        cur.execute("UPDATE teachers SET teacher_name = %s, email = %s, phone = %s WHERE username = %s",
                   (name, email, phone, session['username']))
        db.commit()
        cur.close()
        return redirect('/teacher/teacher_profile')
    else:
        return redirect('/')

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'loggedin' in session and session['role'] == 'teacher':
        cur = db.cursor()
        
        # Fetch classes associated with the logged-in teacher
        cur.execute("SELECT * FROM classes WHERE teacher_username = %s", (session['username'],))
        classes = cur.fetchall()

        # Fetch all students to view in the dashboard
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()

        cur.close()  # Close the cursor
        
        return render_template('teacher_dashboard.html', classes=classes, students=students)
    else:
        return redirect('/')

@app.route('/admin/admin_dashboard')
def admin_dashboard():
    if 'loggedin' in session and session['role'] == 'admin':
        cur = db.cursor()
        cur.execute("SELECT * FROM teachers")
        teachers = cur.fetchall()
        cur.close()
        return render_template('admin_dashboard.html', teachers=teachers)
    else:
        return redirect('/')

@app.route('/admin/attendance_report')
def attendance_report():
    if 'loggedin' in session and session['role'] == 'admin':
        cur = db.cursor()
        cur.execute("SELECT * FROM attendance")  # Adjust the query as necessary
        attendance_records = cur.fetchall()
        cur.close()
        return render_template('attendance_report.html', attendance_records=attendance_records)
    else:
        return redirect('/')

@app.route('/admin/admin_profile')
def admin_profile():
    if 'loggedin' in session and session['role'] == 'admin':
        cur = db.cursor()
        cur.execute("SELECT admin_name, email, phone FROM admins WHERE username = %s", (session['username'],))
        profile_data = cur.fetchone()
        cur.close()
        return render_template('admin_profile.html', profile_data=profile_data)
    else:
        return redirect('/')
    
@app.route('/teacher/add_class', methods=['GET', 'POST'])
def add_class():
    if 'loggedin' in session and session['role'] == 'teacher':
        cur = db.cursor()
        if request.method == 'POST':
            class_name = request.form['class_name']
            class_section = request.form['class_section']
            attendance_date = request.form['attendance_date']
            cur.execute("INSERT INTO classes (class_sec, class_name, class_date, teacher_username) VALUES (%s, %s, %s, %s)",
                       (class_section, class_name, attendance_date, session['username']))
            db.commit()
            cur.close()
            return redirect('/teacher/dashboard')
        cur.execute('SELECT DISTINCT class_sec FROM classes')
        class_sections = cur.fetchall()
        cur.close()
        return render_template('add_class.html', class_sections=class_sections)
    else:
        return redirect('/')

@app.route('/teacher/mark_attendance/<int:class_id>', methods=['GET', 'POST'])
def mark_attendance(class_id):
    if 'loggedin' in session and session['role'] == 'teacher':
        cur = db.cursor()
        
        if request.method == 'POST':
            # Retrieve attendance data from the form
            attendance_data = request.form.getlist('attendance')  # Expecting a list of student_id,status
            for data in attendance_data:
                student_id, status = data.split(',')  # Split the data into student_id and status
                cur.execute("INSERT INTO attendance (class_id, student_id, status) VALUES (%s, %s, %s)",
                            (class_id, student_id, status))
            db.commit()
            cur.close()
            return redirect('/teacher/dashboard')  # Redirect to the dashboard after successful submission

        # Fetch students based on the class_id
        cur.execute("""
            SELECT s.student_id, s.student_name
            FROM students s
            JOIN classes c ON s.class_sec = c.class_sec
            WHERE c.class_id = %s
        """, (class_id,))
        students = cur.fetchall()
        cur.close()

        return render_template('mark_attendance.html', students=students, class_id=class_id)
    else:
        return redirect('/')


    
@app.route('/admin/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
