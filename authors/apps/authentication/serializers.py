from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User
from .social.auth import GoogleSocialAuth


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and can not be read by the client.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        # Use the `create_user` method we wrote earlier to create a new user.
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # As mentioned above, an email is required. Raise an exception if an
        # email is not provided.
        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        # As mentioned above, a password is required. Raise an exception if a
        # password is not provided.
        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token

        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token')

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance


class GoogleAuthSerializer(serializers.ModelSerializer):
    # email = serializers.CharField(max_length=255, read_only=True)
    # username = serializers.CharField(max_length=255, read_only=True)
    # social_id = serializers.CharField(max_length=128, read_only=True)
    # auth_token = serializers.CharField(read_only=True)
    auth_token = serializers.CharField()

    class Meta:
        model = User
        # fields = ['email', 'username', 'auth_token']
        fields = ['auth_token']

    """
    Validate auth_token, decode the auth_token, retrieve user info
    """
    def validate_auth_token(self, auth_token):
        print("################# AUTH TOKEN: ", auth_token)

        response = GoogleSocialAuth.validate_google_token(auth_token)
        print("############## RESPONSE: ", response)

        if response is None:
            # return error message to user
            raise serializers.ValidationError(
                'Invalid token please try again'
            )

        if not response['sub']:  # doesn't have social_id
            raise serializers.ValidationError(
                'Token is not valid please log in again'
            )

        user = User.objects.filter(social_id=response['sub'])
        print("##########################  USER SEARCH: ", user)
        if not user.exists():
            #create the user and log them in
            user_obj = {
                'social_id': response['sub'],
                'username': response['name'],
                'email': response['email'],
                # TODO: replace hardcoded password value with random generated value
                'password': 'Password@AAA'
            }

            try:
                #try to create user
                User.objects.create_user(**user_obj)
            except:
                #some error occured, probably duplicate email
                raise serializers.ValidationError(
                    'Failed to register the user. Email already exists in the database')

            #TODO: we could instead update the created user with the social_id
            # User.objects.filter(email=response['email']).update(social_id=response['sub'])

            # email_param = user_obj['email']
            # password_param = user_obj['password']
            # authenticated_user = authenticate(email=email_param, password=password_param)

            authenticated_user = User.objects.get(social_id=response['sub'])
        else:
            # authenticated_user = User.objects.get(social_id=response['sub'])
            authenticated_user = User.objects.filter(social_id=response['sub'])[0]
            print("############## AUTHENTICATED_USER", authenticated_user.email)
            print("############## AUTHENTICATED_USER", authenticated_user.username)
            #user exists, log them in
            # email_param = response['email']
            # password_param = response['password']

        
        # return {
        #     'email': authenticated_user.email,
        #     'username': authenticated_user.username,
        #     'auth_token': authenticated_user.token()
        # }
        return authenticated_user.token()
     