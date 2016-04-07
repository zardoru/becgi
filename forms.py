from wtforms import TextAreaField, StringField, IntegerField, HiddenField
from wtforms.fields.html5 import URLField, EmailField
from wtforms.validators import url, DataRequired, Email
from flask.ext.wtf import Form
from flask.ext.wtf import RecaptchaField


class SubmitForm(Form):
    bms_name = StringField("Title", validators=[DataRequired()])
    bms_author = StringField("BMS author(s) (comma separated)", description="""
    Music composer, chart artist,
    etc... Add details on the description field.""", validators=[DataRequired()])
    fake_author = StringField("Fake Name",
                              description="""This will be displayed as the artist
                            during impression period.
                            Once impression period is over the real artist name
                            will be revealed.
                            Useful for pseudonyms.""")
    bga_author = StringField("BGA author(s) (comma separated, optional)")
    description = TextAreaField("Description", description="""
    Entry description (supports markdown)""")
    bms_link = URLField("Download URL", validators=[url(), DataRequired()])
    bms_email = EmailField("Author E-Mail", validators=[Email()])
    captcha = RecaptchaField()
    token = HiddenField("Registration password")


class ImpressionForm(Form):
    author = StringField("Name (Anonymous if left blank)")
    rating = IntegerField("Score")
    comment = TextAreaField("Comment (supports markdown)")
    captcha = RecaptchaField()


class SongPasswordForm(Form):
    token = StringField("Registration password")


