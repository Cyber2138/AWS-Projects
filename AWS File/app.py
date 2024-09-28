from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import pywhatkit as kit
import datetime
import os






app = Flask(__name__)
app.secret_key = "your_secret_key"  # Use a secure, random key for production




# MySQL connection configuration
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',  # Replace with your MySQL Workbench host
            user='root',  # Replace with your MySQL username
            password='abdulrmohammed@38',  # Replace with your MySQL password
            database='marketing'  # Replace with your MySQL database
        )
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None
    




# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Change to your email provider
app.config['MAIL_PORT'] = 587  # For starttls
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')  # Your email
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER')
mail = Mail(app)




# Home route
@app.route('/')
def home():
    return render_template('index.html')




# Registration route
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        # Get form data
        company_name = request.form['company_name']
        industry = request.form['industry']
        company_size = request.form['company_size']
        country = request.form['country']
        mobile = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('registration'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='sha256')

        # Insert company data into the database
        connection = create_connection()
        if connection is None:
            flash("Database connection failed. Please try again.", "danger")
            return redirect(url_for('registration'))
        cursor = connection.cursor()

        try:
            cursor.execute(
                '''INSERT INTO company 
                   (company_name, industry, company_size, country, mobile, email, password) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (company_name, industry, company_size, country, mobile, email, hashed_password)
            )
            connection.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Error as e:
            flash(f"An error occurred: {e}", 'danger')
        finally:
            cursor.close()
            connection.close()

    return render_template('registration.html')




# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check user credentials
        connection = create_connection()
        if connection is None:
            flash("Database connection failed. Please try again.", "danger")
            return redirect(url_for('login'))
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute('SELECT * FROM company WHERE email = %s', (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                flash('Login successful!', 'success')
                return redirect(url_for('campaign'))
            else:
                flash('Login failed. Check your credentials.', 'danger')
        except Error as e:
            flash(f"An error occurred: {e}", 'danger')
        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')





@app.route('/campaign', methods=['GET', 'POST'])
def campaign():
    if request.method == 'POST':
        try:
            # Get form data
            campaign_name = request.form['campaign_name']
            message_type = request.form['message_type']
            schedule_date = request.form['schedule_date']
            schedule_time = request.form['schedule_time']
            whatsapp_message = request.form['whatsapp_message']
            recipient_list = request.form['whatsapp_recipient_list'].split(',')

            # Combine date and time into a datetime object
            schedule_datetime = datetime.strptime(f"{schedule_date} {schedule_time}", '%Y-%m-%d %H:%M')
            hour, minute = schedule_datetime.hour, schedule_datetime.minute

            # If the message type is WhatsApp, send WhatsApp message
            if message_type == 'whatsapp':
                for recipient in recipient_list:
                    recipient = recipient.strip()  # Clean up spaces
                    
                    # Send WhatsApp message at the scheduled time
                    kit.sendwhatmsg(recipient, whatsapp_message, hour, minute)
                
                flash('WhatsApp messages successfully scheduled and will be sent at the specified time!', 'success')
            
            return redirect(url_for('campaign_success'))
        
        except Exception as e:
            flash(f"An error occurred while sending the messages: {str(e)}", 'danger')
            return redirect(url_for('campaign'))
    
    return render_template('campaign.html')

@app.route('/campaign_success')
def campaign_success():
    return "Campaign Launched Successfully!"
# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
