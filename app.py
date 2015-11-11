from flask import Flask
from flask import render_template, url_for, redirect, request
from wtforms import TextAreaField, TextField, IntegerField
from wtforms.fields.html5 import URLField
from wtforms.validators import url, DataRequired
from flask.ext.wtf import Form
from flask.ext.wtf import RecaptchaField
import database

app = Flask(__name__)
app.config.from_object("config")
database.generate()

@app.route('/')
def submissions_list():
    return render_template("about.html")

class SubmitForm(Form):
    bms_name = TextField("Title", validators=[DataRequired()])
    bms_author = TextField("BMS author(s) (comma separated)")
    bga_author = TextField("BGA author(s) (comma separated, optional)")
    description = TextAreaField("Description (1024 chars)")
    bms_link = URLField("Download URL", validators=[url(), DataRequired()])
    captcha = RecaptchaField()

class ImpressionForm(Form):
    author = TextField("Name")
    rating = IntegerField("Score (0 - 100)", validators=[DataRequired()])
    comment = TextAreaField("Comment")
    captcha = RecaptchaField()

@app.route('/submit/')
def submit_bms(form=None):
    if form is None:
        form = SubmitForm()
    return render_template("submit.html", form=form)

@app.route('/submit/handle_submit', methods=['POST'])
def handle_bms_submission():
    form = SubmitForm()
    if form.validate_on_submit():
        name = form.bms_name.data
        author = form.bms_author.data
        bga_author = form.bga_author.data
        description = form.description.data
        link = form.bms_link.data
        database.insert_entry(name, author, bga_author, description, link)
        return render_template("submit_success.html", name=name, author=author, link=link, success=True)
    return render_template("submit_success.html", success=False)

@app.route('/admin')
def evt_admin():
    return "evt admin"

@app.route("/about/")
def evt_about():
    return render_template("about.html")

@app.route("/rules/")
def evt_rules():
    return render_template("rules.html")

@app.route("/impressions/")
def evt_songs():
    return render_template("impressions.html", entries=database.get_entries())

@app.route("/impressions/id/<id>")
def sng_impressions(id, form=None):
    if form is None:
        form = ImpressionForm()
    impressions = database.get_impressions(id)
    return render_template("songimpressions.html",
        impressions=impressions,
        song=database.get_song_by_id(id),
        rating=database.get_song_rating(id),
        form=form,
        impression_count=len(impressions))

@app.route("/impressions/id/submit/<id>", methods=["POST"])
def submit_impression(id):
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

app.debug = True
if __name__ == '__main__':
    app.run()
