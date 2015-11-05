import json
from flask import render_template, redirect, url_for, flash, session, request, abort, current_app
from flask.ext.classy import FlaskView, route
from eveauth.forms import LoginForm, RegisterForm
from eveauth.models import User, db
from eveauth.services import sso_service
from eveauth.services.sso import InvalidSSORequestError, UnavailableSSOError, SSOInfo


class MetaView(FlaskView):
    route_base = '/'

    def index(self):
        return render_template('meta/index.html')

    def login(self):
        return render_template('meta/login.html', form=LoginForm())

    @route('/login', methods=['POST'])
    def do_login(self):
        form = LoginForm()
        if form.validate_on_submit():
            return "Success"
        return render_template('meta/login.html', form=form)

    @route('/register', endpoint='MetaView:register')
    def register_(self):
        sso_url, state = sso_service.make_sso_url()
        if 'sso_data' in session:
            del session['sso_data']
        session['sso_state'] = state
        return render_template('meta/register.html', sso_url=sso_url)

    @route('/register_cb', methods=['GET', 'POST'])
    def register_cb(self):
        form = RegisterForm()
        code = request.args.get('code')
        state = request.args.get('state')
        if request.method == 'GET':
            if 'sso_data' in session:
                return render_template('meta/complete_register.html', form=form, sso_data=SSOInfo(*json.loads(session['sso_data'])))
            if state != session['sso_state']:
                flash('Bad OAuth session.', 'danger')
                return redirect(url_for('MetaView:register'))
            try:
                token = sso_service.verify_code(code)
                session['sso_data'] = json.dumps(sso_service.verify_account(token))
            except InvalidSSORequestError:
                flash('Authentication rejected.', 'danger')
                return redirect(url_for('MetaView:register'))
            except UnavailableSSOError:
                flash('Eve Online SSO server sent back an error.', 'danger')
                return redirect(url_for('MetaView:register'))
            except Exception:
                flash('Unknown server error, please try again.', 'danger')
                return redirect(url_for('MetaView:register'))
            else:
                return render_template('meta/complete_register.html', form=form, sso_data=SSOInfo(*json.loads(session['sso_data'])))
        else:
            if 'sso_data' not in session:
                abort(400)
            if not form.validate_on_submit():
                return render_template('meta/complete_register.html', form=form, sso_data=SSOInfo(*json.loads(session['sso_data'])))
            sso_data = SSOInfo(*json.loads(session['sso_data']))
            user_id = sso_data.character_name.lower().replace(' ', '_')
            if User.exists(user_id):
                flash('This user already exists.', 'danger')
                return redirect(url_for('MetaView:login'))
            crest_guest = User.new_crest_guest(form, sso_data)
            try:
                db.session.add(crest_guest)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.exception(e)
                flash('Database exception.', 'danger')
            flash('Welcome to {}! You can now login.'.format(current_app.config['AUTH_NAME']), 'success')
            return redirect(url_for('MetaView:login'))
