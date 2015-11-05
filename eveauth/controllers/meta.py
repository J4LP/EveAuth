from flask import render_template, redirect, url_for, flash, session, request
from flask.ext.classy import FlaskView, route
from eveauth.forms import LoginForm, RegisterForm
from eveauth.services import sso_service
from eveauth.services.sso import InvalidSSORequestError, UnavailableSSOError

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
        session['sso_state'] = state
        return render_template('meta/register.html', sso_url=sso_url)

    @route('/register_cb', methods=['GET', 'POST'])
    def register_cb(self):
        form = RegisterForm()
        code = request.args.get('code')
        state = request.args.get('state')
        if request.method == 'GET':
            if 'sso_data' in session:
                return render_template('meta/complete_register.html', form=form)
            if state != session['sso_state']:
                flash('Bad OAuth session.', 'danger')
                return redirect(url_for('MetaView:register'))
            try:
                token = sso_service.verify_code(code)
                session['sso_data'] = sso_service.verify_account(token)
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
                return render_template('meta/complete_register.html', form=form)

        else:
            if not form.validate_on_submit():
                return render_template('meta/complete_register.html', form=form)
            flash('Registration goes here')
            return redirect(url_for('MetaView:index'))