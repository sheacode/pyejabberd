# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .core.arguments import StringArgument, IntegerArgument, PositiveIntegerArgument, BooleanArgument
from .core.definitions import API

from .errors import UserAlreadyRegisteredError
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
