import pytest
import channels, channel, auth

'''
Tests for channels.py
'''

# Tokens are set to be the user's email.

#------------------------------------------------------------------------------#
#                               channels_create                                #
#------------------------------------------------------------------------------#

# Test for a public channel.
def test_channels_create():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')
    new_channel = channels.channels_create(test_user['token'], 'Channel_1', True)
    assert 1 in new_channel['channel_id']

    

# Testing for an invalid channel name (Invalid when name is >20 characters or <= 0).
def test_channels_invalid():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Indiana', 'Jones')
    auth.auth_login('testEmail@gmail.com', 'password123')

    with pytest.raises(InputError):
        new_channel = channels.channels_create(test_user['token'], 'Invalid_Channels_Name', True)
    


#------------------------------------------------------------------------------#
#                               channels_list                                  #
#------------------------------------------------------------------------------#

# Test for multiple created channels.
def test_channels_list():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

    # Create new channels.
    new_channel_1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    new_channel_2 = channels.channels_create(test_user['token'], 'Channel_2', True)
    new_channel_3 = channels.channels_create(test_user['token'], 'Channel_3', True)
    
    # Join new channels.
    channel.channel_join(test_user['token'], 1)
    channel.channel_join(test_user['token'], 2)

    # Store channels that the user is in into a list.
    result = channels_list(test_user['token'])
    list_channels = []
    list_channels.append(result['channels'[0]['channel_id']])
    list_channels.append(result['channels'[1]['channel_id']])

    assert list_channels[0] == 1
    assert list_channels[1] == 2

# Test for leaving joined channels and then listing joined channels.
def test_channels_list():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

    # Create new channels.
    new_channel_1 = channels.channels_create(test_user['token'], 'Channel_1', True)
    new_channel_2 = channels.channels_create(test_user['token'], 'Channel_2', True)
    new_channel_3 = channels.channels_create(test_user['token'], 'Channel_3', True)

    # Join the first 2 channels and then leave the first channel.
    channel.channel_join(test_user['token'], 1)
    channel.channel_join(test_user['token'], 2)
    channel.channel_leave(test_user['token'], 1)

    result = channels_list(test_user['token'])

    assert result[]

    

#------------------------------------------------------------------------------#
#                               channels_listall                               #
#------------------------------------------------------------------------------#

# Test list all channels.
def test_channels_listall():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')

# Test for 
def test_channels_list():
    test_user = auth.auth_register('testEmail@gmail.com', 'password123', 'Jon', 'Snow')
    auth.auth_login('testEmail@gmail.com', 'password123')