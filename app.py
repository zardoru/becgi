from flask import Flask
from flask import render_template, url_for, redirect, request, flash
from wtforms import TextAreaField, TextField, IntegerField
from wtforms.fields.html5 import URLField, EmailField
from wtforms.validators import url, DataRequired, Email
from flask.ext.wtf import Form
from flask.ext.wtf import RecaptchaField
import database
from date import *

# boilerplate
app = Flask(__name__)
app.config.from_object("config")



# app
@app.route('/')
def submissions_list():
    return render_template("about.html")

class SubmitForm(Form):
    bms_name = TextField("Title", validators=[DataRequired()])
    bms_author = TextField("BMS author(s) (comma separated)", description="""
    Music composer, chart artist,
    etc... Add details on the description field.""", validators=[DataRequired()])
    fake_author = TextField("Fake Name",
                            description="""This will be displayed as the artist 
                            during impression period.
                            Once impression period is over the real artist name
                            will be revealed.
                            Useful for pseudonyms.""")
    bga_author = TextField("BGA author(s) (comma separated, optional)")
    description = TextAreaField("Description (1024 chars)")
    bms_link = URLField("Download URL", validators=[url(), DataRequired()])
    bms_email = EmailField("Author E-Mail", validators=[Email()])
    captcha = RecaptchaField()

class ImpressionForm(Form):
    author = TextField("Name")
    rating = IntegerField("Score (1 - 100)", validators=[DataRequired()])
    comment = TextAreaField("Comment")
    captcha = RecaptchaField()

@app.route('/submit/')
def submit_bms(form=None):
    if form is None:
        form = SubmitForm()
    if are_submissions_open():
        return render_template("submit.html", form=form)
    else:
        return render_template("section_closed.html")

@app.route('/submit/handle_submit', methods=['POST'])
def handle_bms_submission():
    if are_submissions_open():
        form = SubmitForm()
        if form.validate_on_submit():
            name = form.bms_name.data
            author = form.bms_author.data
            fake_author = form.fake_author.data
            bga_author = form.bga_author.data
            description = form.description.data
            link = form.bms_link.data
            email = form.bms_email.data
            database.insert_entry(name,
                                  author, fake_author, bga_author,
                                  description, link, email)
            return render_template("submit_success.html", name=name, author=author, link=link, success=True)
        return render_template("submit_success.html", success=False)
    else:
        return render_template("section_closed.html")

@app.route('/admin')
def evt_admin():
    return "evt admin"

@app.route("/about/")
def evt_about():
    return render_template("about.html")

@app.route("/bmsvsbmson/")
def evt_vs():
    return render_template("bmson.html")

@app.route("/rules/")
def evt_rules():
    return render_template("rules.html")

@app.route("/impressions/")
def evt_songs():
    if can_see_submissions():
        return render_template("impressions.html", entries=database.get_entries())
    else:
        return render_template("section_closed.html")

@app.route("/impressions/id/<id>")
def sng_impressions(id, form=None):
    if form is None:
        form = ImpressionForm()

    if can_see_submissions():
        impressions = database.get_impressions(id)
        sng = database.get_song_by_id(id)
        return render_template("song_impressions.html",
            impressions=impressions,
            song=sng,
            rating=database.get_song_rating(id),
            form=form,
            impression_count=len(impressions),
            is_impression_period=are_impressions_open())
    else:
        return render_template("section_closed.html")

@app.route("/impressions/id/submit/<id>", methods=["POST"])
def submit_impression(id):
    if are_impressions_open():
        form = ImpressionForm()
        if form.validate_on_submit():
            author = form.author.data
            rating = form.rating.data
            comment = form.comment.data
            try:
                rating = int(rating)
                if rating < 0 or rating > 100:
                    raise ValueError()
                ip = request.environ["REMOTE_ADDR"]
                database.insert_impression(id, author, rating, comment, ip)
            except ValueError:
                flash("Rating out of bounds or not a number.")
        else:
            flash("Incomplete form.")
        return redirect("/impressions/id/{}".format(id))
    else:
        return render_template("section_closed.html")


if __name__ == '__main__':
    database.generate()
    app.run()
