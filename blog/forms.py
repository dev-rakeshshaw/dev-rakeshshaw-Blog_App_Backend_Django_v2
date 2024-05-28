from django import forms
from .models import Comment


## Form to gather information which is required to send post`s link to the client.
class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)  # Name of the post owner
    email = forms.EmailField()             # Email of the post owner
    to = forms.EmailField()                # Mail of the Client  
    comments = forms.CharField(required=False, 
                               widget=forms.Textarea)  # Addition Message which is send to client along with the post`s link.



## Form to gather name, email, body of the user who is commenting on a post.
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


#Form for Text-Based search.
class SearchForm(forms.Form):
    query = forms.CharField()
