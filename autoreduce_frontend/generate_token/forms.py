from django import forms
from django.contrib.auth.models import User
from django.forms import ModelChoiceField


class VerboseUserChoiceField(ModelChoiceField):
    """
    Subclasses Django's ModelChoiceField and overrides the label_from_instance method to
    display the first+last name+username instead of the just the username of the User model.

    This is because the usernames stored in the database are the user ID's, which makes it hard to
    visually recognise which user is which.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def label_from_instance(self, obj: User) -> str:
        """
        Returns a custom made label for the given object.

        :param obj: The object to get the label for.
        :return: A string to use as the label.
        """
        return f"{obj.first_name} {obj.last_name} ({obj.username})"


class GenerateTokenForm(forms.Form):
    user = VerboseUserChoiceField(queryset=User.objects.filter(auth_token__pk=None).order_by("first_name"))
