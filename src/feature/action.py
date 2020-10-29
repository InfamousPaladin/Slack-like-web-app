"""
File containing helper functions that ease proccess in some feature functions.
These functions often perform certain action to extract/store information from
the database.

2020 T3 COMP1531 Major Project
"""

import jwt
from src.feature.data import data
from src.feature.globals import NON_EXIST, SECRET

def generate_token(email):
    """Generates a unique token identifier

    Args:
        email (string): email address of user

    Returns:
        (string): token identifier
    """
    for user in data.get_users():
        if user['email'] == email:
            encoded_jwt = jwt.encode({'email': user['email']}, SECRET, algorithm='HS256')
            return str(encoded_jwt)
    return 'invalid_token'

def convert_token_to_u_id(token):
    """Returns the corressponding u_id for the given token

    Args:
        token (string)

    Returns:
        (int): user u_id for the token
    """
    tokens_list = data.get_active_tokens()
    if token in tokens_list:
        user = data.get_active_user_details(token)
        return user['u_id']
    return NON_EXIST

def get_lowest_u_id_in_channel(channel_id):
    """Returns lowest u_id in the channel with channel_id

    Args:
        channel_id (int)

    Returns:
        (int): lowest u_id
    """
    channel_details = data.get_channel_details(channel_id)
    channel_u_ids = list(map(lambda member: member['u_id'], channel_details['all_members']))
    return min(channel_u_ids)

def convert_email_to_u_id(email):
    """Returns the u_id of a user, given the token.

    Args:
        email (str): email address of user

    Returns:
        u_id (int): corressponding u_id of email address
    """
    u_id = NON_EXIST
    for user in data.get_users():
        if user['email'] == email:
            u_id = user['u_id']
    return u_id

def generate_handle_str(name_first, name_last):
    ''' Generates a basic handle string given a users first and last name

    Args:
        name_first (str): first name of user
        name_last (str): last name of user

    Returns:
        handle_str (str): concat version of first and last name
    '''
    first_name_concat = name_first[0:1].lower()
    if len(name_last) >= 17:
        last_name_concat = name_last[0:17].lower()
    else:
        last_name_concat = name_last.lower()
    hstring = first_name_concat + last_name_concat
    count = 0
    for user in data.get_users():
        if user['handle_str'].startswith(hstring):
            count += 1
    hstring += str(count)
    return hstring
