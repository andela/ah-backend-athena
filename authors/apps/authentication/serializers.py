import re
from django.contrib.auth import authenticate
from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError
from .models import User
from .social.google_token_validator import GoogleValidate
from .social.facebook_token_validator import FacebookValidate
from .social.twitter_token_validator import TwitterValidate


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    password = serializers.CharField(
        write_only=True
    )
    """
    Overide default varidation to make sure users receive descriptive
    error messages
    """
    email = serializers.EmailField()
    username = serializers.CharField()

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.

    class Meta:
        model = User

        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.

        fields = ['email', 'username', 'password']

    def validate_password(self, password):
        """
        User's password should be between 8 to 128 characters
        and  should contain atleas one number and a capital letter
        """
        msg = 'Passwords must be between 8 to 128 characters'
        if not len(password) > 8:
            raise serializers.ValidationError(msg)

        if not len(password) < 128:
            raise serializers.ValidationError(msg)

        if re.search('[0-9]', password) is None\
                and re.search('[A-Z]', password) is None:
            raise serializers.ValidationError(
                'Password must contain atleast one number and a capital letter'
            )
        return password

    def validate_email(self, email):
        email_db = User.objects.filter(email=email)
        if email_db.exists():
            raise serializers.ValidationError(
                'A user with that email adress already exists'
            )
        return email

    def validate_username(self, username):

        username_db = User.objects.filter(username=username)
        if username_db.exists():
            raise serializers.ValidationError(
                'The user name you entered is already taken, try another one'
            )

        msg = 'User names must be between 3 and 10 characters'
        if not len(username) > 3:
            raise serializers.ValidationError(msg)

        if not len(username) < 10:
            raise serializers.ValidationError(msg)

        if re.match('^[A-Za-z0-9_]*$', username) is None:
            raise serializers.ValidationError(
                'User names must be characters, letters and underscores only'
            )
        return username

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

        if user.is_superuser:
            user.is_verified = True
            user.save()

        if user.is_verified == False:
            raise serializers.ValidationError(
                'Your email is not verified, Please check your email for a verification link'
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


class PasswordResetSerializer(serializers.Serializer):
    """ 
    serializer for requesting a password reset via email 
    """

    email = serializers.EmailField(max_length=255)

    def validate_email(self, email):
        """
        check if the email entered has a corresponding user
        """
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError(
                'User with this email is not found'
            )
        return email


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    serializer for requesting a new password
    """
    password = serializers.CharField(
        max_length=128,
        min_length=8
    )
    confirm_password = serializers.CharField(
        max_length=128,
        min_length=8
    )


class GoogleAuthSerializer(serializers.ModelSerializer):
    """
    Serializer for the google social login/user creation
    """
    auth_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['auth_token']

    def validate_auth_token(self, auth_token):
        """
        Validate auth_token, decode the auth_token, retrieve user info
        """

        decoded_google_user_data = GoogleValidate.validate_google_token(
            auth_token)

        if decoded_google_user_data is None:
            raise serializers.ValidationError(
                'Invalid token please try again'
            )

        if 'sub' not in decoded_google_user_data:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.'
            )

        user = User.objects.filter(
            social_id=decoded_google_user_data.get('sub'))
        if not user.exists():
            user_obj = {
                'social_id': decoded_google_user_data.get('sub'),
                'username': decoded_google_user_data.get('name', decoded_google_user_data['email']),
                'email': decoded_google_user_data.get('email'),
                'password': 'Password@AAA'
            }

            try:
                User.objects.create_user(**user_obj)
            except:
                raise serializers.ValidationError(
                    'Failed to register the user. Email already exists in the database')

        authenticated_user = User.objects.get(
            social_id=decoded_google_user_data.get('sub'))
        return authenticated_user.token()


class FacebookAuthSerializer(serializers.ModelSerializer):
    """
    Serializer for the facebook social login/user creation
    """

    auth_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['auth_token']

    def validate_auth_token(self, auth_token):
        """
        Validate auth_token, decode the auth_token, retrieve user info
        """

        facebook_user_data = FacebookValidate.validate_facebook_token(
            auth_token)

        if facebook_user_data is None:
            raise serializers.ValidationError(
                'Invalid token please try again'
            )

        if 'id' not in facebook_user_data:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.'
            )

        user = User.objects.filter(social_id=facebook_user_data.get('id'))
        if not user.exists():
            user_obj = {
                'social_id': facebook_user_data.get('id'),
                'username': facebook_user_data.get('name', facebook_user_data.get('email')),
                'email': facebook_user_data.get('email'),
                'password': 'Password@AAA'
            }

            try:
                User.objects.create_user(**user_obj)
            except:
                raise serializers.ValidationError(
                    'Failed to register the user. Email already exists in the database')

        authenticated_user = User.objects.get(
            social_id=facebook_user_data.get('id'))
        return authenticated_user.token()


class TwitterAuthSerializer(serializers.ModelSerializer):
    """
    Serializer for the twitter social login/user creation
    """

    auth_token = serializers.CharField()

    class Meta:
        model = User
        fields = ['auth_token']

    def validate_auth_token(self, auth_token):

        twitter_user_data = TwitterValidate.validate_twitter_token(
            auth_token)
        if twitter_user_data is None:
            raise serializers.ValidationError(
                'Invalid token please try again'
            )

        if 'id_str' not in twitter_user_data:
            raise serializers.ValidationError(
                'Token is not valid or has expired. Please get a new one.'
            )

        user = User.objects.filter(social_id=twitter_user_data.get('id_str'))
        if not user.exists():
            user_obj = {
                'social_id': twitter_user_data.get('id_str'),
                'username': twitter_user_data.get('name'),
                'email': twitter_user_data.get('email'),
                'password': 'Password@AAA'
            }

            try:
                User.objects.create_user(**user_obj)
            except:
                raise serializers.ValidationError(
                    'Failed to register the user. Email already exists in the database')

        authenticated_user = User.objects.get(
            social_id=twitter_user_data.get('id_str'))
        return authenticated_user.token()
