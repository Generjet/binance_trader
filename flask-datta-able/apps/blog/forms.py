from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=200)
    ])
    
    content = CKEditorField('Content', validators=[
        DataRequired(),
        Length(min=10)
    ])
    
    category = SelectField('Category', choices=[
        ('general', 'General'),
        ('technology', 'Technology'),
        ('finance', 'Finance'),
        ('crypto', 'Cryptocurrency'),
        ('trading', 'Trading')
    ], validators=[DataRequired()])
    
    thumbnail = FileField('Thumbnail Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
