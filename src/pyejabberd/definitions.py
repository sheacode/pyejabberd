# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .core.arguments import StringArgument
from .core.definitions import API
from .core.serializers import StringSerializer
from .muc import muc_room_options_serializers
from .muc.arguments import MUCRoomArgument, AffiliationArgument
from .muc.enums import MUCRoomOption

from .errors import UserAlreadyRegisteredError
from pyejabberd.muc.enums import Affiliation
from .utils import format_password_hash_sha


class Echo(API):
    method = 'echothisnew'
    arguments = [StringArgument('sentence')]

    def transform_response(self, api, arguments, response):
        return response.get('repeated')


class RegisteredUsers(API):
    method = 'registered_users'
    arguments = [StringArgument('host')]

    def transform_response(self, api, arguments, response):
        return response.get('users', [])


class Register(API):
    method = 'register'
    arguments = [StringArgument('user'), StringArgument('host'), StringArgument('password')]

    def validate_response(self, api, arguments, response):
        if response.get('res') == 1:
            username = arguments.get('user')
            raise UserAlreadyRegisteredError('User with username %s already exists' % username)

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class UnRegister(API):
    method = 'unregister'
    arguments = [StringArgument('user'), StringArgument('host')]

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class ChangePassword(API):
    method = 'change_password'
    arguments = [StringArgument('user'), StringArgument('host'), StringArgument('newpass')]

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class CheckPasswordHash(API):
    method = 'check_password_hash'
    arguments = [StringArgument('user'), StringArgument('host'), StringArgument('passwordhash'),
                 StringArgument('hashmethod')]

    def transform_arguments(self, **kwargs):
        passwordhash = format_password_hash_sha(password=kwargs.pop('password'))
        kwargs.update({
            'passwordhash': passwordhash,
            'hashmethod': 'sha'
        })
        return kwargs

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class SetNickname(API):
    method = 'set_nickname'
    arguments = [StringArgument('user'), StringArgument('host'), StringArgument('nickname')]

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0

class ConnectedUsers(API):
    method = 'connected_users'
    arguments = []

    def transform_response(self, api, arguments, response):
        connected_users = response.get('connected_users', [])

        return [user["sessions"] for user in connected_users]

class ConnectedUsersInfo(API):
    method = 'connected_users_info'
    arguments = []

    def transform_response(self, api, arguments, response):
        connected_users_info = response.get('connected_users_info', [])

        return [user["sessions"] for user in connected_users_info]

class ConnectedUsersNumber(API):
    method = 'connected_users_number'
    arguments = []

    def transform_response(self, api, arguments, response):
        return response.get('num_sessions')

class UserSessionInfo(API):
    method = 'user_sessions_info'
    arguments = [StringArgument('user'), StringArgument('host')]

    def transform_response(self, api, arguments, response):
        sessions_info = response.get('sessions_info', [])
        return [
            dict((k, v) for property_k_v in session["session"] for k, v in property_k_v.items())
            for session in sessions_info
        ]

class MucOnlineRooms(API):
    method = 'muc_online_rooms'
    arguments = [StringArgument('host')]

    def transform_response(self, api, arguments, response):
        return [result_dict.get('room') for result_dict in response.get('rooms', {})]


class CreateRoom(API):
    method = 'create_room'
    arguments = [StringArgument('name'), StringArgument('service'), StringArgument('host')]

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class DestroyRoom(API):
    method = 'destroy_room'
    arguments = [StringArgument('name'), StringArgument('service'), StringArgument('host')]

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class GetRoomOptions(API):
    method = 'get_room_options'
    arguments = [StringArgument('name'), StringArgument('service')]

    def transform_response(self, api, arguments, response):
        result = {}
        for option_dict in response.get('options', []):
            option = option_dict.get('option')
            if option is None:
                raise ValueError('Unexpected option in response: ' % str(option_dict))
            name_dict, value_dict = option
            result[name_dict['name']] = value_dict['value']
        return result


class ChangeRoomOption(API):
    method = 'change_room_option'
    arguments = [StringArgument('name'), StringArgument('service'), MUCRoomArgument('option'), StringArgument('value')]

    def transform_arguments(self, **kwargs):
        option = kwargs.get('option')
        assert isinstance(option, MUCRoomOption)
        serializer_class = muc_room_options_serializers.get(option, StringSerializer)
        kwargs['value'] = serializer_class().to_api(kwargs['value'])
        return kwargs

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class SetRoomAffiliation(API):
    method = 'set_room_affiliation'
    arguments = [StringArgument('name'), StringArgument('service'), StringArgument('jid'),
                 AffiliationArgument('affiliation')]

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class GetRoomAffiliations(API):
    method = 'get_room_affiliations'
    arguments = [StringArgument('name'), StringArgument('service')]

    def transform_response(self, api, arguments, response):
        affiliations = response.get('affiliations', [])
        return [{
            'username': subdict['affiliation'][0]['username'],
            'domain': subdict['affiliation'][1]['domain'],
            'affiliation': Affiliation.get_by_name(subdict['affiliation'][2]['affiliation']),
            'reason': subdict['affiliation'][3]['reason'],
        } for subdict in affiliations]


class AddRosterItem(API):
    method = 'add_rosteritem'
    arguments = [StringArgument('localuser'), StringArgument('localserver'),
                 StringArgument('user'), StringArgument('server'),
                 StringArgument('nick'), StringArgument('group'), StringArgument('subs')]

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class DeleteRosterItem(API):
    method = 'delete_rosteritem'
    arguments = [StringArgument('localuser'), StringArgument('localserver'),
                 StringArgument('user'), StringArgument('server')]

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0


class GetRoster(API):
    method = 'get_roster'
    arguments = [StringArgument('user'), StringArgument('host')]

    def transform_response(self, api, arguments, response):
        roster = []
        for contact in response.get('contacts', []):
            contact_details = {}
            for parameter in contact['contact']:
                for key, value in parameter.items():
                    contact_details[key] = value
            roster.append(contact_details)
        return roster


class MucRoomOcuppants(API):
    method = 'get_room_occupants'
    arguments = [StringArgument('name'), StringArgument('service')]

    def transform_response(self, api, arguments, response):
        occupants = []
        for occupant in response.get('occupants', []):
            occupant_details = {}
            for parameter in occupant['occupant']:
                for key, value in parameter.items():
                    occupant_details[key] = value
            occupants.append(occupant_details)
        return occupants


class SendStanza(API):
    method = 'send_stanza'
    arguments = [StringArgument('from'), StringArgument('to'), StringArgument('stanza')]

    def transform_response(self, api, arguments, response):
        return response.get('res') == 0