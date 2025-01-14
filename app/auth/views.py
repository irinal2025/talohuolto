import sys
from flask import render_template, redirect, current_app, request, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..decorators import admin_required
#from ..fake import users as fake_users
from ..models import User, Role
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from werkzeug.security import check_password_hash, generate_password_hash


@auth.before_app_request
def before_request():
    app = current_app._get_current_object()
    app.logger.debug('auth.before_request,endpoint %s', request.endpoint)
    app.logger.debug('auth.before_request,blueprint %s', request.blueprint)
    if current_user.is_authenticated:
        current_user.ping()   
        if not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
                return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        current_app.logger.debug(f"Form validated: {form.email.data}")
        user = User.query.filter_by(email=form.email.data.lower()).first()
        current_app.logger.debug("Entered password: %s", form.password.data)
        current_app.logger.debug("Stored password hash: %s", user.password_hash)
        current_app.logger.debug("Password match result: %s", check_password_hash(user.password_hash, form.password.data))


        if user:
            current_app.logger.debug(f"User found: {user.email}")
            if check_password_hash(user.password_hash, form.password.data):
                current_app.logger.debug("Password matched.")
                login_user(user, remember=form.remember_me.data)
                current_app.logger.debug("User logged in successfully.")
                #return redirect(request.args.get('next') or url_for('main.index'))
                # Ohjataan käyttäjä dashboard-sivulle, jos 'next' ei ole määritelty
                return redirect(request.args.get('next') or url_for('main.dashboard'))
            else:
                flash('Invalid email or password')
                current_app.logger.debug("Password did not match.")
        else:
            flash('Invalid email or password')
            current_app.logger.debug("User not found.")
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)  # Salasana muunnetaan hashiksi
        user = User(email=form.email.data.lower(),
                    username=form.username.data,
                    password_hash=hashed_password)  # Tallenna hash tietokantaan
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))


# Esimerkki loggauksen käytöstä Flask-reitillä
@auth.route('/testi')
@login_required
@admin_required
def testi():
    # sys.stdout.write("Tämä on testireitti loggerin testaamiseen (stdout).\n")
    sys.stderr.write("Tämä on testireitti loggerin testaamiseen (stderr).\n")
    current_app.logger.debug("Tämä on debug-viesti.")
    current_app.logger.info("Käyttäjä vieraili kotisivulla.")
    current_app.logger.warning("Tämä on varoitusviesti.")
    current_app.logger.error("Tämä on virheviesti.")
    current_app.logger.critical("Tämä on kriittinen virheviesti.")
    current_app.logger.exception("Tämä on exception-virheviesti.")
    return "Tervetuloa testisivulle!"



 
     
  