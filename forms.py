from wtforms import TextAreaField, StringField, IntegerField, HiddenField, RadioField, BooleanField
from wtforms.fields.html5 import URLField, EmailField, DateField
from wtforms.validators import DataRequired, Email, InputRequired
from flask.ext.wtf import Form
from flask.ext.wtf import RecaptchaField
import urllib


def url_validator(optional):
    def validator(_, field):
        if optional and len(field.data) == 0:
            return True
        else:
            try:
                urllib.parse.parse_qs(field.data, strict_parsing=True)
            except ValueError:
                return False
            return True
    return validator


def email_optional(optional):
    em_val = Email()

    def validator(form, field):
        if optional and len(field.data) == 0:
            return True
        else:
            return em_val(form, field)
    return validator


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
    bms_link = URLField("Download URL", validators=[url_validator(False), InputRequired()])
    bms_email = EmailField("Author E-Mail", validators=[email_optional(False)])
    captcha = RecaptchaField()
    token = HiddenField("Registration password")


class ImpressionForm(Form):
    author = StringField("Name (Anonymous if left blank)")
    rating = IntegerField("Score")
    comment = TextAreaField("Comment (supports markdown)")
    captcha = RecaptchaField()


class SongPasswordForm(Form):
    token = StringField("Registration password", validators=[InputRequired()])

score_choices = [('none', "No scoring"), ('bmwest2016', "BMWest 2016 scoring")]


class EventForm(Form):
    # should match Scoring.xx

    name = StringField("Event Name", validators=[InputRequired()])

    description = TextAreaField("Event Description (supports markdown)", description="""
    The description of your event. Can include rules and others.
    """, validators=[InputRequired()])

    organizers = StringField("Event Organizers", validators=[InputRequired()])

    package_url = URLField("Download link",
                           description="If not blank, adds a link to event package download.",
                           validators=[url_validator(True)])

    email = EmailField("Event E-Mail", description="""
    If not blank, adds a link on the footer with the email for your event.""", validators=[email_optional(True)])

    twitter = StringField("Twitter username", description="Displayed at the footer.")

    banner_url = URLField("Banner URL",
                          description="URL to event banner.",
                          validators=[url_validator(True)])

    css_url = URLField("CSS URL", description="URL to custom css.", validators=[url_validator(True)])

    impression_start = DateField("Impression start date (Open at start of this day)")

    impression_end = DateField("Impression end date (Close at end of this day)")

    submission_start = DateField("Submission start date (Open at start of this day)")

    submission_end = DateField("Submission end date (Close at end of this day)")

    scoring_method = RadioField("Scoring method", choices=score_choices,
                                description="""
                                Use the scoring method you prefer.
                                BMWest is the average * log10(impressions + 1).
                                None just allows non-empty comments in impressions.
                                """)

    fake_name = BooleanField("Allow fake names",
                             description="Whether to allow the use of aliases in your event.")

    token = StringField("Authorization token",
                        description="The password sent to you by email to edit this event.",
                        validators=[InputRequired()])
