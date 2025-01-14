from flask import render_template, session, redirect, url_for, abort, flash, request, current_app, make_response, jsonify, send_from_directory, Blueprint
from flask_login import login_user,logout_user, login_required, current_user
#from flask_sqlalchemy import get_debug_queries
from ..auth.forms import LoginForm, SignupForm
from ..email import send_email
from . import main
from sqlalchemy import text
#from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..auth.forms import LoginForm
from .. import db
#from ..models import Permission, Role, User, Post, Comment
from ..models import Permission, Role, User
from ..decorators import admin_required, permission_required, debuggeri
from datetime import datetime, date
import os
import sys
import calendar
from flask_wtf.csrf import generate_csrf,CSRFError

reactapi = Blueprint('reactapi', __name__)

@reactapi.route('/')
def index():
    return "Hello, World!"

@reactapi.route('/csrf', methods=['GET'])
def get_csrf():
    token = generate_csrf()
    response = jsonify({"detail": "CSRF token generated"})
    response.headers.set('X-CSRFToken', token)
    return response

def createResponse(message, status_code=200):
    # CORS:n vaatimat Headerit
    default_origin = 'http://localhost:5176'
    default_origin = current_app.config.get('DEFAULT_ORIGIN',default_origin)
    origin = request.headers.get('Origin',default_origin)
    response = make_response(jsonify(message))
    # Access-Control-Allow-Credentials
    # response.headers.set('Access-Control-Allow-Credentials',True)
    response.headers.set('Access-Control-Allow-Origin',origin)
    response.status_code = status_code
    return response


@reactapi.app_errorhandler(401)
def page_not_allowed(e):
    app = current_app._get_current_object()
    app.logger.debug('reactapi.app_errorhandler 401,endpoint %s', request.endpoint)
    app.logger.debug('reactapi.app_errorhandler 401,path %s', request.path)
    if request.endpoint == 'reactapi.confirm':
        # Vrt. vastaava Flask route:
        # login_url = url_for('login', confirm_token=confirm_token, _external=True)
        redirect_url = app.config['REACT_LOGIN'] + "?next=" + request.path
        return redirect(redirect_url)
    message = {'virhe':'Kirjautuminen puuttuu.'}
    return createResponse(message)


@reactapi.app_errorhandler(CSRFError)
def handle_csrf_error(e):
    message = {'virhe':f'csrf-token puuttuu ({e.description}), headers:{str(request.headers)}'}
    sys.stderr.write(f"\nreactapi CSFRError,headers:{str(request.headers)}\n")
    return createResponse(message, status_code=400)

@reactapi.route('/getcsrf', methods=['GET'])
def getcsrf():
    token = generate_csrf()
    response = jsonify({"detail": "CSRF cookie set"})
    response.headers.set("X-CSRFToken", token)
    return response

@reactapi.route('/signin', methods=['GET','POST'])
def signin():
    print("reactapi,views.py,LOGIN")
    form = LoginForm()
    sys.stderr.write(f"\nreactapi,views.py,LOGIN data:{form.email.data}\n")
    if form.validate_on_submit():
        sys.stderr.write(f"\nreactapi, views.py,LOGIN, validate_on_submit OK\n")
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            admin = user.is_administrator()
            sys.stderr.write(f"\nviews.py,LOGIN, request.args:{request.args}\n")
            next = request.args.get('next')
            sys.stderr.write(f"\nviews.py,LOGIN:OK, next:{next}, confirmed:{user.confirmed}\n")
            # if next is None or not next.startswith('/'):
            response = jsonify({'success':True,'confirmed':user.confirmed,'admin':admin})
            response.status_code=200
            return response
            # Huom. Uudelleen reititys tapahtuu selaimen kautta
  
        else:
            response = jsonify({'success':False,'message':"Väärät tunnukset"})
            response.status_code = 401
            return response
    else:
        response = jsonify({
            "success": False,
            "message": "Tiedot on annettu väärin.",
            "errors": form.errors })
        response.status_code=400
        return response
    

@reactapi.route('/signup', methods=['GET', 'POST'])
# Määritetään CORS-alustuksessa
# @cross_origin(supports_credentials=True)
def signup():
    form = SignupForm()
    sys.stderr.write('\nviews.py,SIGNUP,email:'+form.email.data+'\n')
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'reactapi/email/confirm', user=user, token=token)
        # Huom. ilmoitus sähköpostivahvistuksesta tarvitaan käyttöliittymään
        # flash('A confirmation email has been sent to you by email.')
        response = jsonify({'success':True,'confirming':True})
        response.status_code = 200
        return response
    else:
        sys.stderr.write("validointivirheet:"+str(form.errors))
        # return "Virhe lomakkeessa:"+str(form.errors)
        response = jsonify({'success':False,
                           'message':'Tiedot väärin.',
                           'confirming':True,
                           'errors':form.errors})
        response.status_code = 200
        return response


@reactapi.route('/logout', methods=['GET'])
def logout():
    logout_user()
    response = jsonify({'success':True})
    response.status_code=200
    return response


@reactapi.route('/confirm/<token>', methods=['GET'])
@login_required
def confirm(token):
    app = current_app._get_current_object()
    app.logger.debug('/confirm,current_user: %s',current_user.email)
    app.logger.debug('/confirm,confirmed: %s',current_user.confirmed)
    # app.logger.debug('/confirm,headers:' + str(request.headers))
    if current_user.confirmed:
        app.logger.debug('/confirm,REACT_CONFIRMED:' + app.config['REACT_CONFIRMED'])
        return redirect(app.config['REACT_CONFIRMED'] + '?confirmed=1')
    if current_user.confirm(token):
        app.logger.debug('/confirm:confirmed')
        db.session.commit()
        response = jsonify({'success':True,
                            'message':'Tunnus on vahvistettu',
                            'confirmed':True
                            })
        response.status_code = 200
        return response
    else:
        response = jsonify({'success':False,
                            'message':'Vahvistus epäonnistui',
                            'confirmed':False})   
        response.status_code = 200
        return response


@reactapi.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    app = current_app._get_current_object()
    app.logger.debug('/confirm: %s',current_user.email)
    send_email(current_user.email, 'Confirm Your Account',
               'reactapi/email/confirm', user=current_user, token=token)
    message = 'A new confirmation email has been sent to you by email.'
    return jsonify({'success':True,'message':message})