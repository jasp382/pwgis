from django import forms

class InputsForm(forms.Form):
    """
    Obtain data to create susceptibility maps
    to landslides
    """

    landslides = forms.FileField(
        label="Upload Landslides data",
        widget=forms.ClearableFileInput(attrs={
            'multiple' : True
        })
    )

    variables = forms.FileField(
        label="Upload Independent Variables",
        widget=forms.ClearableFileInput(attrs={
            'multiple' : True
        })
    )

