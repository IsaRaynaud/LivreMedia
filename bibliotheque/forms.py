from django import forms

class EmpruntForm(forms.Form):
    membre_id = forms.IntegerField(label='ID du membre')