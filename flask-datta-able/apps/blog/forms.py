from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired
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

class YearlyWesternHoroscopeForm(FlaskForm):
    zodiac = SelectField('Zodiac', choices=[
        ('Aries', 'Aries'),
        ('Taurus', 'Taurus'),
        ('Gemini', 'Gemini'),
        ('Cancer', 'Cancer'),
        ('Leo', 'Leo'),
        ('Virgo', 'Virgo'),
        ('Libra', 'Libra'),
        ('Scorpio', 'Scorpio'),
        ('Sagittarius', 'Sagittarius'),
        ('Capricorn', 'Capricorn'),
        ('Aquarius', 'Aquarius'),
        ('Pisces', 'Pisces')
    ], validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
