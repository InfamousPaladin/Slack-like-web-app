"""
auth feature implementation as specified by the specification

Feature implementation was written by Christian Ilagan.

2020 T3 COMP1531 Major Project
"""

import hashlib
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets
from src.feature.validate import (
    validate_create_email,
    validate_names,
    validate_names_characters,
    validate_password_length,
    validate_password,
    validate_token_by_u_id,
    validate_password_chars,
)
from src.feature.action import (
    convert_email_to_u_id, 
    generate_handle_str,
    generate_token,
)
from src.feature.error import InputError
from src.feature.data import data
from src.globals import DATA_FILE, FIRST_FLOCKR_OWNER_ID, NON_EXIST, OWNER, MY_ADDRESS, PASSWORD
import pickle


def auth_login(email, password):
    """Given a registered users' email and password and generates a valid token
    for the user to remain authenticated

    Args:
        email (string): [description]
        password (string): [description]

    Returns:
        (dict): { u_id, token }
    """
    data = pickle.load(open(DATA_FILE, "rb"))

    # input handling
    email = email.lower()
    u_id = convert_email_to_u_id(data, email)
    token = generate_token(data, email)
    if not validate_password_length(password):
        raise InputError("Invalid password input.")
    if not validate_password_chars(password):
        raise InputError("Invalid characters entered.")
    if not validate_create_email(email):
        raise InputError("Invalid Email.")
    if u_id == NON_EXIST:
        raise InputError("Email is not registered")
    if validate_token_by_u_id(data, u_id):
        raise InputError("User is already logged in.")

    # Checking if password is valid.
    password = hashlib.sha256(password.encode()).hexdigest()
    if not validate_password(data, password):
        raise InputError("Incorrect password.")

    # adding to database
    data.create_active_user(u_id, token)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return {
        'u_id': u_id,
        'token': token,
    }

def auth_logout(token):
    """Given an active token, invalidates the token to log the user out. If a
    valid token is given, and the user is successfully logged out, it returns
    true, otherwise false.

    Args:
        token (string): unique identifier for user

    Returns:
        (dict): { is_success }
    """
    data = pickle.load(open(DATA_FILE, "rb"))
    is_success = False
    for user in data.get_active_users():
        if user['token'] == token:
            data.delete_active_user(token)
            is_success = True

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return {
        'is_success': is_success,
    }

def auth_register(email, password, name_first, name_last):
    """Given a user's first and last name, email address, and password, create
    a new account for them and return a new token for authentication in their
    session. A handle is generated that is the concatentation of a lowercase-only
    first name and last name. If the concatenation is longer than 20 characters,
    it is cutoff at 20 characters. If the handle is already taken, you may modify
    the handle in any way you see fit to make it unique.

    Args:
        email (string)
        password (string)
        name_first (string)
        name_last (string)

    Returns:
        (dict): { u_id, token }
    """
    data = pickle.load(open(DATA_FILE, "rb"))

    # error handling email
    email = email.lower()
    if not validate_create_email(email):
        raise InputError(description="Invalid email.")
    u_id = convert_email_to_u_id(data, email)
    if u_id != NON_EXIST:
        raise InputError(description="A user with that email already exists.")

    # error handling password
    if not validate_password_length(password) or not validate_password_chars(password):
        raise InputError(description="Invalid characters. Between 6 - 128 characters (inclusive).")

    # error handling names
    if not validate_names(name_first) or not validate_names(name_last):
        raise InputError(description="First/Last name should be between 1 - 50 characters (inclusive).")
    if not validate_names_characters(name_first) or not validate_names_characters(name_last):
        raise InputError(description="Please include only alphabets, hyphens and whitespaces.")

    # error handling handle string
    hstring = generate_handle_str(data, name_first, name_last)

    # creating a new user
    u_id = len(data.get_users()) + 1
    data.create_user(email, password, name_first, name_last, u_id, hstring)
    user = data.get_user_details(u_id)
    assert len(user['handle_str']) <= 20

    # assigning flockr owner
    if user['u_id'] == FIRST_FLOCKR_OWNER_ID:
        data.set_user_permission_id(u_id, OWNER)
        data.set_first_owner_u_id(u_id)
    
    # logging in user
    token = generate_token(data, email)
    data.create_active_user(u_id, token)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return {
        'u_id': u_id,
        'token': token,
    }

def read_template(file):
    """
    Helper function that returns a template object of file
    """
    path = 'src/feature/message.txt'
    with open (path, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def auth_passwordreset_request(email):
    """Given an email address, if the user is a registered user, send's them a 
    an email containing a specific secret code, that when entered in 
    auth_passwordreset_reset, shows that the user trying to reset the password 
    is the one who got sent this email.

    Args:
        email (string)

    Returns:
        (dict): {}
    """
    data = pickle.load(open(DATA_FILE, "rb"))

    # Checking that user is registered
    found = False
    for user in data.get_users():
        if user['email'] == email:
            found = True
    if not found:
        raise InputError("Invalid Email, please register gain access.")

    # generating secret
    secret = secrets.token_urlsafe(8)
    # adding user to reset users field
    found = False
    # if user already exists in structure
    for user in data.get_reset_users():
        if user['email'] == email:
            # update only the secret
            data.update_secret(email, secret)
            found = True
    # if user does not exist
    if not found:
        u_id = convert_email_to_u_id(data, email)
        # add user to reset_user structure
        data.create_password_request(email, u_id, secret)

    # sending an email to the user
    message_template = read_template('message.txt')

    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(MY_ADDRESS, PASSWORD)

    msg = MIMEMultipart()   # creating a message
    full_name = ''
    for user in data.get_users():
        if user['email'] == email:
            full_name = user['name_first'] + ' ' + user['name_last']

    message = message_template.substitute(PERSON_NAME=full_name.title(), SECRET_CODE = secret)
    # setup parameters of message
    msg['From'] = MY_ADDRESS
    msg['To'] = email
    msg['Subject'] = "flockr - Password Reset"

    msg.attach(MIMEText(message, 'plain'))
    s.send_message(msg)
    del msg
    s.quit()   

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE) 
    
    return {}

def auth_passwordreset_reset(reset_code, new_password):
    """Given a reset code for a user, set that user's new password to the 
    password provided

    Args:
        reset_code (string)
        new_password (string)

    Returns:
        (dict): {}
    """
    data = pickle.load(open(DATA_FILE, "rb"))
    if not validate_password_length(new_password) or not validate_password_chars(new_password):
        raise InputError("Invalid characters. Between 6 - 128 characters (inclusive).")
    # getting the user with a reset code
    u_id = 0
    found = False
    for user in data.get_reset_users():
        if user['secret'] == reset_code:
            u_id = user['u_id']
            found = True
    if not found:
        raise InputError("Incorrect reset code.")

    # hashing password
    password = hashlib.sha256(new_password.encode()).hexdigest()
    for user in data.get_users():
        if user['u_id'] == u_id:
            # changing password
            data.set_user_password(u_id, password)

    # removing user from reset_users
    data.remove_request(u_id)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)
    return {}