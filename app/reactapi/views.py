from flask import render_template,request, \
     flash,redirect,url_for,jsonify,current_app, \
     send_from_directory, make_response
from flask_login import (
    login_user,logout_user, 
    login_required, current_user )
from ..decorators import admin_required,debuggeri
from ..models import User
from ..auth.forms import LoginForm, RegistrationForm
from ..email import send_email
from app import db
from . import reactapi
from sqlalchemy import text
import os
import sys
from werkzeug.utils import secure_filename
from flask_babel import _
import json
import time
from flask_cors import cross_origin
from flask_wtf.csrf import CSRFProtect, generate_csrf, CSRFError

csrf = CSRFProtect()

def createResponse(message, status_code=200):
    # Sallitut alkuperät (lisää luotettavat osoitteet tähän listaan)
    allowed_origins = ['http://localhost:5173', 'http://127.0.0.1:5173']

    # Hae pyyntöön liittyvä Origin-header
    request_origin = request.headers.get('Origin')

    # Tarkista, onko alkuperä sallittu
    if request_origin in allowed_origins:
        origin = request_origin
    else:
        origin = None  # Älä salli CORS-pyyntöä tuntemattomasta alkuperästä
    
    # Luo vastaus
    response = make_response(jsonify(message))
    response.status_code = status_code

    # Lisää CORS-headerit vain, jos alkuperä on sallittu
    #if origin:
        #response.headers.set('Access-Control-Allow-Origin', origin)
        #response.headers.set('Access-Control-Allow-Credentials', 'true')  # Tämän pitää olla merkkijono 'true'
    
    return response


@reactapi.app_errorhandler(401)
@cross_origin(supports_credentials=True)
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
@cross_origin(supports_credentials=True)
def handle_csrf_error(e):
    message = {'virhe':f'csrf-token puuttuu ({e.description}), headers:{str(request.headers)}'}
    sys.stderr.write(f"\nreactapi CSFRError,headers:{str(request.headers)}\n")
    return createResponse(message, status_code=400)


@reactapi.route('/getcsrf', methods=['GET'])
@cross_origin(supports_credentials=True)  # Salli CORS tälle reitille
def getcsrf():
    token = generate_csrf()
    #response = jsonify({"detail": "CSRF cookie set"})
    response = jsonify({'message': 'CSRF-token lähetetty'})
    response.set_cookie('csrf_token', token, samesite='None', secure=True)  # Lähetä CSRF-tunnus evästeenä
    response.headers.set("X-CSRFToken", token)
    response.headers.set("Access-Control-Expose-Headers", "X-CSRFToken")
    return response

@reactapi.route('/signin', methods=['POST'])
@cross_origin(supports_credentials=True)
def signin():
    print("reactapi,views.py,LOGIN")

    # Testaa lomakevirheitä ja käyttäjän vastauksia
    #return jsonify({"status": 200, "reason": "toiminnallisuus sallittu!"})

    # Flask CSRF-tarkistus
    csrf_token = request.cookies.get('csrf_token')  # Otetaan CSRF-tunniste
    if not csrf_token:
        return jsonify({"success": False, "message": "Missing CSRF token"}), 400

    # Verifioi CSRF-token Flaskin CSRF-suojauksella
    if not current_app.csrf.validate_csrf(csrf_token):
        return jsonify({"success": False, "message": "Invalid CSRF token"}), 400

    sys.stderr.write(f"\nReceived data: {request.data}\n")
    sys.stderr.write(f"\nReceived JSON: {request.get_json()}\n")
    
    try:
        data = request.get_json()  # Lue JSON-data pyynnöstä
        if not data:
            sys.stderr.write("No JSON data received!\n")
            return jsonify({"success": False, "message": "No data received"}), 400

        email = data.get('email')
        password = data.get('password')
        #remember_me = data.get('remember_me', False)
        
        sys.stderr.write(f"\nreactapi,views.py,LOGIN data: {email}, {password}\n")
        
        # Jos puuttuu dataa
        if not email or not password:
            response = jsonify({
                "success": False,
                "message": "Sähköposti tai salasana puuttuu"
            })
            response.status_code = 400
            return response
        
        form = LoginForm(email=email, password=password)  # Käytetään suoraan dataa
        
        if form.validate_on_submit():
            user = User.query.filter_by(email=email.lower()).first()
            if user is not None and user.verify_password(password):
                #login_user(user, remember_me)
                login_user(user)
                admin = user.is_administrator()
                next = request.args.get('next')
                
                response = jsonify({
                    'success': True,
                    'confirmed': user.confirmed,
                    'admin': admin
                })
                response.status_code = 200
                return response
            else:
                response = jsonify({
                    'success': False,
                    'message': "Väärät tunnukset"
                })
                response.status_code = 401
                return response
        else:
            response = jsonify({
                "success": False,
                "message": "Tiedot on annettu väärin.",
                "errors": form.errors
            })
            response.status_code = 400
            return response
    except Exception as e:
        current_app.logger.error(f"Error during login: {e}")
        response = jsonify({
            "success": False,
            "message": "Virhe kirjautumisessa"
        })
        response.status_code = 500
        return response
    

@reactapi.route('/signup', methods=['GET', 'POST'])
# Määritetään CORS-alustuksessa
@cross_origin(supports_credentials=True)
def signup():
    form = RegistrationForm()
    #form = LoginForm()
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
@cross_origin(supports_credentials=True)
def logout():
    logout_user()
    response = jsonify({'success':True})
    response.status_code=200
    return response


@reactapi.route('/confirm/<token>', methods=['GET'])
@cross_origin(supports_credentials=True)
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
@cross_origin(supports_credentials=True)
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    app = current_app._get_current_object()
    app.logger.debug('/confirm: %s',current_user.email)
    send_email(current_user.email, 'Confirm Your Account',
               'reactapi/email/confirm', user=current_user, token=token)
    message = 'A new confirmation email has been sent to you by email.'
    return jsonify({'success':True,'message':message})

@reactapi.route('/csrf-debug')
@cross_origin(supports_credentials=True)
def csrf_debug():
    return jsonify({"csrf_token": generate_csrf()})