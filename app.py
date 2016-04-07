from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flaskext.markdown import Markdown
from forms import SubmitForm, ImpressionForm, SongPasswordForm
import database
import logging

# boilerplate
app = Flask(__name__)
app.config.from_object("config")
Markdown(app)


# routes
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/events/')
def events_list_index():
    return render_template("events.html", events=database.get_events())


@app.route('/event/<int:event_id>')
def event_index(event_id):
    try:
        evt = database.Event(event_id)
        return render_template("event.html", event=evt)
    except database.IncorrectEvent as e:
        return render_template("section_closed.html", event=None)


@app.route('/event/<int:event_id>/submit')
def event_submit(event_id, form=None):
    if form is None:
        form = SubmitForm()

    evt = database.Event(event_id)
    if evt.are_submissions_open:
        return render_template("submit.html", form=form, event=evt)
    else:
        return render_template("section_closed.html", event=evt)


@app.route('/event/<int:event_id>/entry/<int:song_id>/edit/', methods=['POST'])
def event_edit_entry(event_id, song_id):
    evt = database.Event(event_id)
    pwform = SongPasswordForm()
    if pwform.validate_on_submit():
        form = SubmitForm()
        song = database.get_song_by_token_and_id(pwform.token.data, song_id)
        if song:
            form.bga_author.default = song.bga_author
            form.bms_author.default = song.author
            form.bms_email.default = song.email
            form.bms_link.default = song.link
            form.bms_name.default = song.name
            form.description.default = song.description
            form.fake_author.default = song.fake_author
            form.token.default = song.token  # token is valid anyway
            form.process()  # actually set the defaults

            # okay we're set, modification in progress
            return render_template("submit.html", event=evt, form=form, modify=True, song=song)
        else:
            logging.error("Null song.")
            return render_template("section_closed.html", event=evt)
    else:
        logging.error("Null form.")
        return render_template("section_closed.html", event=evt)


@app.route('/event/<int:event_id>/entry/<int:song_id>/update', methods=['POST'])
def event_update_entry(event_id, song_id):
    evt = database.Event(event_id)
    form = SubmitForm()
    if form.validate_on_submit():
        evt.update_entry(form.bms_name.data,
                         form.bms_author.data,
                         form.fake_author.data,
                         form.bga_author.data,
                         form.description.data,
                         form.bms_link.data,
                         form.bms_email.data,
                         song_id, form.token.data)
    return redirect(url_for('event_song_impressions', event_id=event_id, song_id=song_id))


@app.route('/event/<int:event_id>/submit/handle_submit', methods=['POST'])
def event_handle_submission(event_id):
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

                token = evt.insert_entry(name,
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
                                       token=token,
                                       success=True)
            return render_template("submit.html",
                                   form=form,
                                   event=evt,
                                   success=False)
        else:
            return render_template("section_closed.html", event=evt)
    except database.IncorrectEvent as e:
        return render_template("section_closed.html", event=None)


@app.route('/event/<int:event_id>/admin')
def event_admin(event_id):
    return render_template("admin_event.html", event=database.Event(event_id))


@app.route("/about/")
def about():
    return render_template("index.html")


@app.route("/bmsvsbmson/")
def event_vs():
    return render_template("bmson.html")


@app.route("/event/<int:event_id>/impressions/")
def event_songs(event_id):
    evt = database.Event(event_id)
    if evt.can_see_submissions:
        return render_template("impressions.html", entries=evt.entries, event=evt)
    else:
        return render_template("section_closed.html")


@app.route("/event/<int:event_id>/impressions/id/<int:song_id>")
def event_song_impressions(event_id, song_id, form=None, pwform=None):
    if form is None:
        form = ImpressionForm()

    if pwform is None:
        pwform = SongPasswordForm()

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
                                       pwform=pwform,
                                       impression_count=len(impressions),
                                       is_impression_period=evt.are_impressions_open,
                                       event=evt)
            else:
                return render_template("wrong_event.html")
        else:
            return render_template("section_closed.html", event=evt)
    except database.IncorrectEvent as e:
        return render_template("section_closed.html", event=None)


@app.route("/event/<int:event_id>/impressions/id/<int:song_id>/submit", methods=["POST"])
def event_submit_impression(event_id, song_id):
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

        return redirect(url_for('event_song_impressions', event_id=event_id, song_id=song_id))
    else:
        return render_template("section_closed.html")


if __name__ == '__main__':
    database.generate()
    app.run()
