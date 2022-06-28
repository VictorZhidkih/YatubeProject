from django import forms

from .models import Post



class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')

    def clean_subject(self):
        data = self.cleaned_data['text']
        
        if '' in data.lower():
            raise forms.ValidationError('обязательное для заполнения поле')
        return data
