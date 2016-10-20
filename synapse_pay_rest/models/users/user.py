from synapse_pay_rest.client import Client
from .base_document import BaseDocument


class User():
    """Abstraction of a user record with methods for constructing User instances.
    """

    def __init__(self, **kwargs):
        for arg, value in kwargs.items():
            setattr(self, arg, value)

    @classmethod
    def from_response(cls, client, response):
        """Construct a user from a response dict."""
        user = cls(
          client=client,
          id=response['_id'],
          refresh_token=response['refresh_token'],
          logins=response['logins'],
          phone_numbers=response['phone_numbers'],
          legal_names=response['legal_names'],
          permission=response['permission'],
          note=response.get('extra').get('note'),
          supp_id=response.get('extra').get('supp_id'),
          is_business=response.get('extra').get('is_business'),
          cip_tag=response.get('extra').get('cip_tag')
        )
        user.base_documents = BaseDocument.multiple_from_response(user,
                                                                  response['documents'])
        return user

    @classmethod
    def multiple_from_response(cls, client, response):
        """Construct multiple users from a response dict."""
        users = [cls.from_response(client, user_data) for user_data in response]
        return users

    @staticmethod
    def payload_for_create(email, phone_number, legal_name, **kwargs):
        """Build the API 'create user' payload from property values."""
        payload = {
          'logins': [{'email': email}],
          'phone_numbers': [phone_number],
          'legal_names': [legal_name],
          'extra': {
            'supp_id': kwargs.get('supp_id'),
            'note': kwargs.get('note'),
            'is_business': kwargs.get('is_business'),
            'cip_tag': kwargs.get('cip_tag')
          }
        }
        return payload

    @classmethod
    def create(cls, client=None, email=None, phone_number=None,
               legal_name=None, **kwargs):
        """Create a user record in API and corresponding User instance.

        Args:
            client (Client): an instance of the API Client
            email (str): user's login email
            password (str): (opt) password (only if users log in via web portal)
            read_only (bool): (opt) False if admin user (default)
            phone_number (str): user's phone number
            legal_name (str): user's legal name
            note (str): (opt) note to SynapsePay
            supp_id (str): (opt) supplemental id
            is_business (bool): (opt) False if personal user (default)
            cip_tag (int): (opt) determined by your cip flow (default=1)

        Returns:
            User: a new User instance
        """
        payload = cls.payload_for_create(email, phone_number, legal_name,
                                         **kwargs)
        response = client.users.create(payload)
        return cls.from_response(client, response)

    @classmethod
    def by_id(cls, client=None, id=None):
        """Retrieve a user record by id and create a User instance from it.

        Args:
            client (Client): an instance of the API Client
            id (str): id of the user to retrieve

        Returns:
            User: a User instance corresponding to the record
        """
        response = client.users.get(id)
        return cls.from_response(client, response)

    @classmethod
    def all(cls, client=None, **kwargs):
        """Retrieve all user records (limited by pagination).

        Args:
            client (Client): an instance of the API Client
            per_page (int, str): (opt) number of records to retrieve
            page (int, str): (opt) page number to retrieve
            query (str): (opt) substring to filter for in user names/emails

        Returns:
            list: containing 0 or more User instances
        """
        response = client.users.get(**kwargs)
        return cls.multiple_from_response(client, response['users'])

    def authenticate(self):
        """Refresh the User's oauth token.

        Returns:
            User: self
        """
        payload = {'refresh_token': self.refresh_token}
        self.client.users.refresh(self.id, payload)
        return self

    def payload_for_update(self, **kwargs):
        """Build the API 'update user' payload from property values."""
        payload = {
            'refresh_token': self.refresh_token,
            'update': {}
        }
        # TODO: Can simplify this when the API accepts null values w/o barfing
        if 'email' in kwargs:
            payload['update']['login'] = {'email': kwargs['email']}
            options = ['password', 'read_only']
            for option in options:
                if option in kwargs:
                    payload['update']['login'][option] = kwargs[option]
        if 'remove_login' in kwargs:
            payload['update']['remove_login'] = {'email': kwargs['remove_login']}
        options = ['legal_name', 'phone_number', 'remove_phone_number',
                   'cip_tag']
        for option in options:
            if option in kwargs:
                payload['update'][option] = kwargs[option]
        return payload

    def add_base_document(self, **kwargs):
        """Add a BaseDocument to the User.

        Args:
            email (str): user's email
            phone_number (str): user's phone number
            ip (str): user's IP address
            name (str): user's name
            alias (str): user's alias or DBA (use name if no alias)
            entity_type (str): https://docs.synapsepay.com/docs/user-resources#section-supported-entity-types
            entity_scope (str): https://docs.synapsepay.com/docs/user-resources#section-supported-entity-scope
            day (int): day of birth
            month (int): month of birth
            year (int): year of birth
            address_street (str): street address (as '123 Maple Street')
            address_city (str): address city
            address_subdivision (str): state, province, or other division
            address_postal_code (str): postal code
            address_country_code (str): country code (as 'US')

        Returns:
            BaseDocument: a new BaseDocument instance
        """
        return BaseDocument.create(self, **kwargs)

    def add_legal_name(self, new_name):
        """Add an additional legal name to the User.

        Args:
            new_name (str): name to add

        Returns:
            User: a new instance representing the same API record
        """
        payload = self.payload_for_update(legal_name=new_name)
        response = self.client.users.update(self.id, payload)
        return User.from_response(self.client, response)

    def add_login(self, email, password=None, read_only=None):
        """Add an additional email and other optional login info to the User.

        Args:
            email (str): user's login email
            password (str): (opt) password (only if users log in via web portal)
            read_only (bool): (opt) False if admin user (default)

        Returns:
            User: a new instance representing the same API record
        """
        payload = self.payload_for_update(email=email, password=password,
                                          read_only=read_only)
        response = self.client.users.update(self.id, payload)
        return User.from_response(self.client, response)

    def remove_login(self, email):
        """Remove a login email from the User.

        Args:
            email (str): login email to remove

        Returns:
            User: a new instance representing the same API record
        """
        payload = self.payload_for_update(remove_login=email)
        response = self.client.users.update(self.id, payload)
        return User.from_response(self.client, response)

    def add_phone_number(self, phone_number):
        """Add a phone number to the User.

        Args:
            phone_number (str): phone number to add

        Returns:
            User: a new instance representing the same API record
        """
        payload = self.payload_for_update(phone_number=phone_number)
        response = self.client.users.update(self.id, payload)
        return User.from_response(self.client, response)

    def remove_phone_number(self, phone_number):
        """Remove a phone number from the User.

        Args:
            phone_number (str): phone number to remove

        Returns:
            User: a new instance representing the same API record
        """
        payload = self.payload_for_update(remove_phone_number=phone_number)
        response = self.client.users.update(self.id, payload)
        return User.from_response(self.client, response)

    def change_cip_tag(self, new_cip):
        """Change the User's cip_tag.

        Args:
            new_cip (int): the cip tag you want to change the user to

        Returns:
            User: a new instance representing the same API record
        """
        payload = self.payload_for_update(cip_tag=new_cip)
        response = self.client.users.update(self.id, payload)
        return User.from_response(self.client, response)
