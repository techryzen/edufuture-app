from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Featured Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])
    tags = StringField('Tags (comma separated)')
    status = SelectField('Status', choices=[('published', 'Published'), ('draft', 'Draft')])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')

class BlogSearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search') 