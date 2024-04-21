from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import boto3
import os
import requests
import json


app = Flask(__name__)
app.secret_key = os.urandom(24)

# AWS configuration

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

import requests
from flask import Flask, render_template, request, redirect, url_for, session



@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        print(f"Login request: email={email}, password={password}")

        # Send a POST request to the API endpoint
        api_endpoint = "https://jsq2nvtp4b.execute-api.us-east-1.amazonaws.com/userLogin/LoginFunction"
        payload = {
            "body": json.dumps({
                "email": email,
                "password": password
            })
        }
        print(f"Sending login request to API: {api_endpoint}")
        print(f"Payload: {payload}")

        try:
            response = requests.post(api_endpoint, json=payload)
            print(f"API response status code: {response.status_code}")
            print(f"API response content: {response.text}")
            response_data = response.json()
            print(f"Response data: {response_data}")

            if response.status_code == 200 and response_data.get('body') == '"Login successful"':
                # Login successful
                session['Email'] = email + '\n'
                print("Login successful. Redirecting to main page")
                return redirect(url_for('main'))
            elif response.status_code == 401:
                # Invalid email or password
                error = response_data.get('body', "Invalid email or password")
                print(f"Login failed: {error}")
            else:
                # Other error
                error = response_data.get('body', "An error occurred during login")
                print(f"Login failed: {error}")
        except requests.exceptions.RequestException as e:
            
            error = f"An error occurred during login: {str(e)}"
            print(error)

        return render_template('login.html', form=form, error=error)
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        print(f"Registration request: email={email}, username={username}, password={password}")

        # Send a POST request to the API endpoint
        api_endpoint = "https://j8abf7aqxg.execute-api.us-east-1.amazonaws.com/Registration_user/useRegistrationFunction"
        payload = {
            "body": json.dumps({
                "email": email,
                "username": username,
                "password": password
            })
        }
        print(f"Sending registration request to API: {api_endpoint}")
        print(f"Payload: {payload}")

        try:
            response = requests.post(api_endpoint, json=payload)
            print(f"API response status code: {response.status_code}")
            print(f"API response content: {response.text}")
            response_data = response.json()
            print(f"Response data: {response_data}")

            if response.status_code == 200 and response_data.get('body') == '"User registered successfully"':
                # Registration successful
                success_message = "User registered successfully"
                print(success_message)
                return redirect(url_for('login'))  # Redirect to the login page
            elif response.status_code == 400:
                # Email already exists or missing required fields
                error = response_data.get('body', "An error occurred during registration")
                print(f"Registration failed: {error}")
            else:
                # Other error
                error = response_data.get('body', "An error occurred during registration")
                print(f"Registration failed: {error}")
        except requests.exceptions.RequestException as e:
            # Handle exceptions raised by the requests library
            error = f"An error occurred during registration: {str(e)}"
            print(error)

        return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form)

@app.route('/main', methods=['GET', 'POST'])
def main():
    print(f"Session: {session}")
    if 'Email' in session:
        email = session['Email']

        # Fetch user information from the login table
        login_table = dynamodb.Table('Login')
        response = login_table.get_item(Key={'Email': email})
        print(f"Response from 'Login' table in main route: {response}")  # Debugging statement
        if 'Item' in response:
            user = response['Item']

            # Fetch the user's subscribed music from the 'subscription' table
            subscription_table = dynamodb.Table('subscription')
            response = subscription_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_email').eq(email)
            )
            subscribed_music_list = response['Items']
            print(f"User's subscribed music: {subscribed_music_list}")  # Debugging statement

            if request.method == 'POST':
                # Handle query form submission
                title = request.form.get('title')
                year = request.form.get('year')
                artist = request.form.get('artist')

                # Send a POST request to the API endpoint with the search criteria
                api_endpoint = "https://sfvwyc1l97.execute-api.us-east-1.amazonaws.com/musicquery/Musicquery"
                payload = {
                    "event": {
                        "title": title,
                        "year": year,
                        "artist": artist
                    }
                }

                try:
                    response = requests.post(api_endpoint, json=payload)
                    response.raise_for_status()  # Raise an exception for non-2xx status codes

                    # Handle the API response
                    if response.status_code == 200:
                        response_data = response.json()
                        print("Response Data:")
                        print(response_data)
                        print("Type of Response Data:")
                        print(type(response_data))
                        if 'body' in response_data:
                            music_list = json.loads(response_data['body'])
                            print("Music List:")
                            print(music_list)
                            print("Type of Music List:")
                            print(type(music_list))
                            if not music_list:
                                message = "No result is retrieved. Please query again."
                                return render_template('main.html', user=user, message=message, subscribed_music_list=subscribed_music_list)
                            else:
                                return render_template('main.html', user=user, music_list=music_list, subscribed_music_list=subscribed_music_list)
                        else:
                            # Other error
                            error = "An error occurred during query"
                            return render_template('main.html', user=user, message=error, subscribed_music_list=subscribed_music_list)
                    else:
                        # Other error
                        error = "An error occurred during query"
                        return render_template('main.html', user=user, message=error, subscribed_music_list=subscribed_music_list)
                except requests.exceptions.RequestException as e:
                    # Handle exceptions raised by the requests library
                    error = f"An error occurred during query: {str(e)}"
                    return render_template('main.html', user=user, error=error, subscribed_music_list=subscribed_music_list)

            else:
                # Check if an error message is passed from the 'remove' function
                error = request.args.get('error')
                return render_template('main.html', user=user, subscribed_music_list=subscribed_music_list, error=error)
        else:
            print("User not found in 'Login' table. Redirecting to login.")  # Debugging statement
            return redirect(url_for('login'))
    else:
        print("User not logged in. Redirecting to login.")  # Debugging statement
        return redirect(url_for('login'))


@app.route('/remove', methods=['POST'])
def remove():
    if 'Email' in session:
        email = session['Email'].strip()
        title = request.form.get('title')
        print(f"Remove request: email={email}, title={title}")

        # Check if the required fields are present
        if not title:
            error = "Please provide the title field."
            print(error)
            return redirect(url_for('main', error=error))

        # Send a POST request to the API endpoint
        api_endpoint = "https://pfvq2wy0m0.execute-api.us-east-1.amazonaws.com/Remove_music/Remove_music"
        payload = {
            "body": json.dumps({
                "email": email,
                "title": title
            })
        }
        print(f"Sending remove request to API: {api_endpoint}")
        print(f"Payload: {payload}")

        try:
            response = requests.post(api_endpoint, json=payload)
            print(f"API response status code: {response.status_code}")
            print(f"API response content: {response.text}")
            response_data = response.json()
            print(f"Response data: {response_data}")

            if response.status_code == 200 and response_data.get('body') == '"Subscription removed successfully"':
                # Subscription removal successful
                print("Subscription removed successfully")
                return redirect(url_for('main'))
            elif response.status_code == 401:
                # Unauthorized - Email not found in the login table
                error = response_data.get('body', "Unauthorized: Email not found in the login table")
                print(f"Subscription removal failed: {error}")
                return redirect(url_for('main', error=error))
            elif response.status_code == 404:
                # Subscription not found
                error = response_data.get('body', "Subscription not found")
                print(f"Subscription removal failed: {error}")
                return redirect(url_for('main', error=error))
            else:
                # Other error
                error = response_data.get('body', "An error occurred during subscription removal")
                print(f"Subscription removal failed: {error}")
                return redirect(url_for('main', error=error))
        except requests.exceptions.RequestException as e:
            # Handle exceptions raised by the requests library
            error = f"An error occurred during subscription removal: {str(e)}"
            print(error)
            return redirect(url_for('main', error=error))
    else:
        print("User not logged in. Redirecting to login.")
        return redirect(url_for('login'))



# Subscribe route
@app.route('/subscribe', methods=['POST'])
def subscribe():
    if 'Email' in session:
        email = session['Email'].strip()
        title = request.form.get('title')
        artist = request.form.get('artist')
        year = request.form.get('year')
        image_url = request.form.get('image_url')

        print(f"Subscription request: email={email}, title={title}, artist={artist}, year={year}, image_url={image_url}")

        # Check if all required fields are present
        if not title or not artist or not year:
            error = "Please provide title, artist, and year fields."
            print(error)
            return redirect(url_for('main', error=error))

        # Send a POST request to the API endpoint
        api_endpoint = "https://zl6h3s47wk.execute-api.us-east-1.amazonaws.com/subscription/SubscriptionFunction"
        payload = {
            "body": json.dumps({
                "email": email,
                "title": title,
                "artist": artist,
                "year": year,
                "image_url": image_url
            })
        }

        print(f"Sending subscription request to API: {api_endpoint}")
        print(f"Payload: {payload}")

        try:
            response = requests.post(api_endpoint, json=payload)
            print(f"API response status code: {response.status_code}")
            print(f"API response content: {response.text}")

            response_data = response.json()
            print(f"Response data: {response_data}")

            if response.status_code == 200 and response_data.get('body') == '"Subscription successful"':
                # Subscription successful
                print("Subscription successful")
                return redirect(url_for('main'))
            else:
                # Subscription failed or other error
                error = response_data.get('body', "An error occurred during subscription")
                print(f"Subscription failed: {error}")
                return redirect(url_for('main', error=error))

        except requests.exceptions.RequestException as e:
            # Handle exceptions raised by the requests library
            error = f"An error occurred during subscription: {str(e)}"
            print(error)
            return redirect(url_for('main', error=error))
    else:
        print("User not logged in. Redirecting to login.")
        return redirect(url_for('login'))
    
# Logout route
@app.route('/logout')
def logout():
    session.pop('Email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    
    with app.app_context():
        print(app.url_map)
    app.run(debug=True)