from flask import Flask
from flask import render_template, redirect, request, flash
from flaskext.markdown import Markdown
from forms import SubmitForm, ImpressionForm
import database

# boilerplate
app = Flask(__name__)
app.config.from_object("config")
Markdown(app)


# routes
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/events/')
def events_index():
    return render_template("events.html", events=database.get_events())


@app.route('/event/<int:event_id>')
def event_index(event_id):
    try:
        evt = database.Event(event_id)
        return render_template("event.html", event=evt)
    except database.IncorrectEvent as e:
        return render_template("section_closed.html", event=None)


@app.route('/event/<int:event_id>/submit')
def submit_bms(event_id, form=None):
    if form is None:
        form = SubmitForm()

    evt = database.Event(event_id)
    if evt.are_submissions_open:
        return render_template("submit.html", form=form, event=evt)
    else:
        return render_template("section_closed.html", event=evt)


@app.route('/event/<int:event_id>/submit/handle_submit', methods=['POST'])
def handle_bms_submission(event_id):
    try:
        evt = database.Event(event_id)
        if evt.are_submissions_open:
            form = SubmitForm()

            if form.validate_on_submit():
                name = form.bms_name.data
                author = form.bms_author.data
                fake_author = form.fake_author.data
                bga_author = form.bga_author.data
                description = form.description.data
                link = form.bms_link.data
                email = form.bms_email.data

                evt.insert_entry(name,
                                 author,
                                 fake_author,
                                 bga_author,
                                 description,
                                 link,
                                 email)

                return render_template("submit_success.html",
                                       name=name,
                                       author=author,
                                       link=link,
                                       event=evt,
                                       success=True)
            return render_template("submit_success.html",
                                   event=evt,
                                   success=False)
        else:
            return render_template("section_closed.html", event=evt)
    except database.IncorrectEvent as e:
        return render_template("section_closed.html", event=None)


@app.route('/event/<int:event_id>/admin')
def evt_admin(event_id):
    return render_template("admin_event.html", event=database.Event(event_id))


@app.route("/about/")
def evt_about():
    return render_template("index.html")


@app.route("/bmsvsbmson/")
def evt_vs():
    return render_template("bmson.html")


@app.route("/event/<int:event_id>/rules/")
def evt_rules(event_id):
    return render_template("rules.html", event=database.Event(event_id))


@app.route("/event/<int:event_id>/impressions/")
def evt_songs(event_id):
    evt = database.Event(event_id)
    if evt.can_see_submissions:
        return render_template("impressions.html", entries=evt.entries, event=evt)
    else:
        return render_template("section_closed.html")


@app.route("/event/<int:event_id>/impressions/id/<int:song_id>")
def sng_impressions(event_id, song_id, form=None):
    if form is None:
        form = ImpressionForm()

    try:
        evt = database.Event(event_id)
        if evt.can_see_submissions:
            sng = database.get_song_by_id(song_id)
            if sng.event_id == evt.id:
                impressions = evt.get_impressions(sng)
                return render_template("song_impressions.html",
                                       impressions=impressions,
                                       song=sng,
                                       rating=evt.get_rating_impressions(impressions),
                                       form=form,
                                       impression_count=len(impressions),
                                       is_impression_period=evt.are_impressions_open,
                                       event=evt)
            else:
                return render_template("wrong_event.html")
        else:
            return render_template("section_closed.html", event=evt)
    except database.IncorrectEvent as e:
        return render_template("section_closed.html", event=None)


@app.route("/event/<int:event_id>/impressions/id/submit/<int:song_id>", methods=["POST"])
def submit_impression(event_id, song_id):
    evt = database.Event(event_id)
    if evt.are_impressions_open:
        form = ImpressionForm()
        if form.validate_on_submit():
            author = form.author.data
            rating = form.rating.data
            comment = form.comment.data
            try:
                ip = request.environ["REMOTE_ADDR"]
                evt.insert_impression(song_id, author, rating, comment, ip)
            except ValueError as e:
                flash(str(e))
            except database.IncorrectEvent as e:
                flash(str(e))
        else:
            flash("Incomplete form.")

        return redirect("/event/{}/impressions/id/{}".format(event_id, song_id))
    else:
        return render_template("section_closed.html")


if __name__ == '__main__':
    database.generate()
    app.run()
