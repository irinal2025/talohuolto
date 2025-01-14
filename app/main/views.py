from flask import render_template, session, redirect, url_for, abort, flash, request, current_app, make_response, jsonify, send_from_directory, jsonify
from flask_login import login_required, current_user
#from flask_sqlalchemy import get_debug_queries
from . import main
from sqlalchemy import text
from sqlalchemy.sql import text
#from .forms import NameForm, EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, TaskForm, TaskUpdateForm, FaultReportForm, TalkootForm, TalkootHallintaForm, NotificationsForm, FaultReportUpdateForm, UpdateUserForm, HousingCompanyUpdateForm, ContractForm, ResidentForm, ResidentDeleteForm
from .. import db
#from ..models import Permission, Role, User, Post, Comment
from ..models import Permission, Role, User, Task, FaultReport, Talkoot, TalkootParticipants, Notifications, HousingCompany, Contract
from ..decorators import admin_required, permission_required, debuggeri
from datetime import datetime, date
import os
import calendar
from flask_wtf.csrf import generate_csrf,CSRFError


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # ...
        return redirect(url_for('.index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False), current_time=datetime.utcnow())

@main.route('/hello')
def hello():
    print("Reitti /hello kutsuttiin!")
    return "Hello, Flask!"

@main.route('/test_db')  # Reitti on 'test_db'
def test_db():
    try:
        result = db.session.execute(text('SELECT 1'))
        return 'Yhteys toimii: ' + str(result.all())
    except Exception as e:
        return 'Virhe tietokannassa: ' + str(e)

@main.route('/tips')
def tips():
    print("Hello function called")
    return render_template('tips.html')

@main.route('/terms')
def terms():
    return render_template('terms.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        # Lomakkeen tiedot voidaan käsitellä täällä, kuten tallentaminen tai sähköpostin lähettäminen
        return render_template('contact.html', thank_you=True)
    return render_template('contact.html', thank_you=False)


# Mock data for the dashboard
huoltotiedot = {
    "avoimet_tehtavat": 5,
    "seuraavat_aikataulut": [
        {"tehtava": "Ilmanvaihtohuolto", "pvm": "2024-12-05"},
        {"tehtava": "Sähkötarkastus", "pvm": "2024-12-10"},
    ],
    "energiankulutus": {
        "current_usage": 150,  # kWh
        "previous_usage": 130,  # kWh
    }
}

@main.route('/dashboard')
@login_required
def dashboard():
    # Hae nykyinen päivämäärä ja kellonaika
    nykyinen_aika = datetime.now()

    tasks = Task.query.all()

    # Laske tulevien tehtävien määrä
    upcoming_tasks_count = Task.query.filter(Task.start_date > datetime.now()).count()

    # Laske tulevien tehtävien määrä (kategoria ei ole "Kokous")
    upcoming_tasks_count2 = Task.query.filter(Task.start_date > datetime.now(), Task.category != 'Kokous').count()



    # Hae seuraavat kolme huoltotyötä `start_date`-kriteerin perusteella
    seuraavat_huoltotyot = (
        Task.query.filter(Task.start_date >= nykyinen_aika)  # Suodata tulevat tehtävät
        .order_by(Task.start_date.asc())  # Järjestä nousevassa aikajärjestyksessä
        .limit(3)  # Rajaa kolmeen
        .all()
    )

    # Hae kolme seuraavaa kokousta (category: Kokous)
    tulevat_kokoukset = (
        Task.query.filter(Task.category == "Kokous", Task.start_date >= nykyinen_aika)
        .order_by(Task.start_date.asc())
        .limit(3)
        .all()
    )

    fault_reports = FaultReport.query.all()

    # Hae kolme uusinta FaultReport-tietuetta järjestettynä julkaisuajankohdan mukaan
    fault_reports = FaultReport.query.order_by(FaultReport.report_date.desc()).limit(3).all()

    #open_fault_reports_count = FaultReport.query.filter_by(status='pending').count() 
    open_fault_reports_count = FaultReport.query.filter(FaultReport.status.in_(['pending', 'in_progress', 'delegated'])).count()


    talkoot = Talkoot.query.all()  # Hae kaikki tiedotteet

    # Hae kolme uusinta FaultReport-tietuetta järjestettynä julkaisuajankohdan mukaan
    talkoot = Talkoot.query.order_by(Talkoot.date.desc()).limit(3).all()

    notifications = Notifications.query.all()  # Hae kaikki tiedotteet

    # Hae kolme uusinta Notifications-tietuetta järjestettynä julkaisuajankohdan mukaan
    notifications = Notifications.query.order_by(Notifications.publish_date.desc()).limit(3).all()

    for notification in notifications:
        if notification.publish_date:
            notification.publish_date = notification.publish_date.strftime('%d.%m.%Y')

    return render_template('dashboard.html', huoltotiedot=huoltotiedot, tasks=tasks, notifications=notifications, fault_reports=fault_reports, seuraavat_huoltotyot=seuraavat_huoltotyot, tulevat_kokoukset=tulevat_kokoukset, talkoot=talkoot, open_fault_reports_count=open_fault_reports_count, upcoming_tasks_count=upcoming_tasks_count, upcoming_tasks_count2=upcoming_tasks_count2)

@main.route('/dashboard/vastike')
@login_required
def manage_fees():
    return render_template('/dashboard/fees.html')

@main.route('/dashboard/tasks', methods=['GET', 'POST'])
@login_required
def manage_tasks():
    form = TaskForm()
    if form.validate_on_submit():
        # Tallenna lomakkeen tiedot tietokantaan
        task = Task(
            task_name=form.task_name.data,
            category=form.category.data,
            start_date = form.start_date.data,
            end_date = form.end_date.data,
            priority=form.priority.data
        )

        # Määritetään prioriteetille luokka
        if task.priority == 'Matala':
            task.priority_class = 'low-priority'
        elif task.priority == 'Keskitaso':
            task.priority_class = 'medium-priority'
        elif task.priority == 'Korkea':
            task.priority_class = 'high-priority'
        else:
            task.priority_class = 'default-priority'

        db.session.add(task)
        db.session.commit()
        return redirect(url_for('main.manage_tasks'))
    tasks = Task.query.all()
    return render_template('/dashboard/tasks.html', form=form, tasks=tasks)
 

@main.route('/dashboard/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)  # Haetaan tehtävä ID:n perusteella
    form = TaskUpdateForm(obj=task)  # Täytetään lomake nykyisillä tehtävän tiedoilla
    
    if form.validate_on_submit():
        # Päivitetään tehtävän tiedot lomakkeen avulla
        task.task_name = form.task_name.data
        task.category = form.category.data
        task.start_date = form.start_date.data
        task.end_date = form.end_date.data
        task.priority = form.priority.data
        
        # Tallennetaan muutokset tietokantaan
        db.session.commit()
        
        # Ohjataan takaisin tehtävälistalle
        return redirect(url_for('main.manage_tasks'))
    
    # Näytetään lomake, jossa voi muokata tehtävää
    return render_template('dashboard/tasks_edit.html', form=form, task=task)


@main.route('/dashboard/reports')
@login_required
def manage_reports():
    return render_template('/dashboard/reports.html')

@main.route('/dashboard/tiedotteet', methods=['GET', 'POST'])
@login_required
def manage_notifications():
    form = NotificationsForm()  # Luo lomake
    notifications = Notifications.query.all()  # Haetaan kaikki tiedotteet tietokannasta

    if form.validate_on_submit():
        # Luodaan uusi tiedote lomakkeen tiedoilla
        new_notification = Notifications(
            title=form.title.data,
            content=form.content.data,
            publish_date=form.publish_date.data
        )
        db.session.add(new_notification)
        db.session.commit()  # Tallennetaan uusi tiedote tietokantaan
        return redirect(url_for('main.manage_notifications'))

    return render_template('dashboard/notifications.html', form=form, notifications=notifications)



@main.route('/dashboard/huoltokalenteri')
@login_required
def manage_calendar():
    # Luo kalenteri tälle kuukaudelle
    today = date.today()

    tasks = Task.query.all()  # Hae kaikki tehtävät

    # Muokkaa päivämäärät oikeaan muotoon Pythonissa ennen malliin lähettämistä
    for task in tasks:
        task.start_date = task.start_date.strftime('%d.%m.%Y')  # Muuntaa paivamaara oikeaan muotoon


    # for task in tasks:
    #    print(f"Paivamaara: {task.start_date}, Tyyppi: {type(task.start_date)}")  # Tulostaa päivämäärän ja tyypin


    # Hae tulevat huoltotyöt (Kunnossapito, Hoito ja Parannustoimi)
    tulevat_huoltotyot = Task.query.filter(Task.start_date >= today, Task.category.in_(['Kunnossapito', 'Hoito', 'Parannustoimi'])).order_by(Task.start_date).all()

    # Hae menneet huoltotyöt (Kunnossapito, Hoito ja Parannustoimi)
    menneet_huoltotyot = Task.query.filter(Task.start_date < today, Task.category.in_(['Kunnossapito', 'Hoito', 'Parannustoimi'])).order_by(Task.start_date.desc()).all()

    # Hae tulevat kokoukset (Parannustoimi)
    tulevat_kokoukset = Task.query.filter(Task.start_date >= today, Task.category == 'Kokous').order_by(Task.start_date).all()

    # Hae menneet kokoukset (Parannustoimi)
    menneet_kokoukset = Task.query.filter(Task.start_date < today, Task.category == 'Kokous').order_by(Task.start_date.desc()).all()
    
    cal = calendar.HTMLCalendar().formatmonth(today.year, today.month)
    return render_template('/dashboard/calendar.html', calendar=cal, tulevat_huoltotyot=tulevat_huoltotyot, menneet_huoltotyot=menneet_huoltotyot, tulevat_kokoukset=tulevat_kokoukset, menneet_kokoukset=menneet_kokoukset)


# Mock data (tätä voi myöhemmin korvata tietokannalla tai API-kutsulla)
energiankulutus_data = [
    {"kuukausi": "Tammikuu", "sahko_kwh": 1200, "vesi_m3": 80, "energiakustannukset": 150},
    {"kuukausi": "Helmikuu", "sahko_kwh": 1150, "vesi_m3": 75, "energiakustannukset": 145},
    {"kuukausi": "Maaliskuu", "sahko_kwh": 1300, "vesi_m3": 90, "energiakustannukset": 160},
]
@main.route('/dashboard/energiatehokkuus')
@login_required
def manage_energy():
    return render_template('/dashboard/energy.html', energiankulutus_data=energiankulutus_data)


@main.route('/dashboard/vikailmoitukset', methods=['GET', 'POST'])
@login_required
def manage_faultreport():
    form = FaultReportForm()
    # Haetaan kaikki vikailmoitukset
    fault_reports = FaultReport.query.all()

    # Lisätään uusi vikailmoitus
    if request.method == 'POST' and 'add_fault' in request.form:
        issue = request.form['issue']
        reporter_name = request.form['reporter_name']
        actions = request.form['actions']
        email = request.form['email']
        issue_description = request.form['issue_description']

        new_report = FaultReport(
            issue=issue,
            reporter_name=reporter_name,
            actions=actions,
            email=email,
            issue_description=issue_description
        )

        try:
            db.session.add(new_report)
            db.session.commit()
            return redirect(url_for('fault_reports'))  # Päivitetään sivu
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return "Error while adding fault report"

    # Päivitetään vikailmoituksen status
    if request.method == 'POST' and 'update_fault' in request.form:
        report_id = request.form['report_id']
        status = request.form['status']
        actions = request.form['actions']

        fault_report = FaultReport.query.get(report_id)
        if fault_report:
            fault_report.status = status
            fault_report.actions = actions
            try:
                db.session.commit()
                return redirect(url_for('fault_reports'))  # Päivitetään sivu
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
                return "Error while updating fault report"

    return render_template('/dashboard/fault_report.html', fault_reports=fault_reports)
    # return render_template('/dashboard/fault_report.html', kiitos=False, vikailmoitukset=vikailmoitukset)
    # Pass the list of fault reports to the template
    #return render_template('/dashboard/fault_report.html', vikailmoitukset=vikailmoitukset)


@main.route('/dashboard/vikailmoitukset/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_fault_report(task_id):
    # Haetaan vikailmoitus ID:n perusteella
    fault_report = FaultReport.query.get_or_404(task_id)
    form = FaultReportUpdateForm(obj=fault_report)  # Täytetään lomake nykyisillä tiedoilla
    
    if form.validate_on_submit():
        # Päivitetään vikailmoituksen tiedot lomakkeen avulla
        fault_report.issue = form.issue.data
        fault_report.reporter_name = form.reporter_name.data
        fault_report.email = form.email.data
        fault_report.issue_description = form.issue_description.data
        fault_report.actions = form.actions.data
        fault_report.status = form.status.data
        
        try:
            # Tallennetaan muutokset tietokantaan
            db.session.commit()
            return redirect(url_for('main.manage_faultreport'))  # Ohjataan takaisin vikailmoitusten hallintaan
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return "Error while updating fault report"

    # Jos lomaketta ei ole vielä lähetetty, näytetään se täytettynä
    return render_template('/dashboard/fault_report_edit.html', form=form, fault_report=fault_report)



#Raportit ja dokumentit
@main.route('/dashboard/dokumentit')
@login_required
def manage_documents():
    return render_template('/dashboard/documents.html')


@main.route('/dashboard/talkoot', methods=['GET', 'POST'])
@login_required
def manage_talkoot():
    form = TalkootForm()
    if form.validate_on_submit():
        # Luo uusi talkoo
        talkoo = Talkoot(
            date=form.date.data,
            equipment=form.equipment.data
        )
        db.session.add(talkoo)
        db.session.commit()

        # Lisää kirjautunut käyttäjä osallistujaksi talkoisiin
        participant = TalkootParticipants(
            talkoot_id=talkoo.id,
            name=current_user.username  # Käyttäjän nimi
        )
        db.session.add(participant)
        db.session.commit()

        return redirect(url_for('main.manage_talkoot'))

    # Hae kaikki talkoot ja osallistujat
    talkoot = Talkoot.query.all()
    return render_template('dashboard/talkoot.html', form=form, talkoot=talkoot)


# Talkoiden hallinta
@main.route('/dashboard/talkoot/hallinta', methods=['GET', 'POST'])
@login_required
def manage_talkoot_hallinta():
    form = TalkootHallintaForm()
    if form.validate_on_submit():
        # Tulostetaan lomakkeen tiedot debuggausta varten
        print(f"Adding talkoo with date: {form.date.data}, equipment: {form.equipment.data}")

        # Luo uusi talkoo ilman osallistujia
        talkoo = Talkoot(
            date=form.date.data,
            equipment=form.equipment.data
        )
        try:
            db.session.add(talkoo)
            db.session.commit()  # Tallennetaan talkoo tietokantaan
            flash('Talkoo lisätty onnistuneesti!', 'success')
        except Exception as e:
            db.session.rollback()  # Palautetaan mahdolliset virheet
            flash(f'Virhe tallennettaessa talkoota: {str(e)}', 'danger')
        
        return redirect(url_for('main.manage_talkoot_hallinta'))

    # Hae kaikki talkoot
    talkoot = Talkoot.query.all()
    return render_template('dashboard/talkoot_hallinta.html', form=form, talkoot=talkoot)



#@main.route('/dashboard/taloyhtio')
#@login_required
#def manage_taloyhtio():
#    return render_template('/dashboard/taloyhtio.html')

@main.route('/dashboard/taloyhtio', methods=['GET'])
@login_required
def housing_company():
    company = db.session.query(HousingCompany).first()  # Haetaan vain yksi taloyhtiö
    if not company:
        return "Tietoja ei löytynyt", 404
    return render_template('dashboard/housing_company.html', company=company)



@main.route('/dashboard/taloyhtio/hallinta', methods=['GET', 'POST'])
@login_required
def housing_company_edit():
    company = HousingCompany.query.first() or HousingCompany()
    form = HousingCompanyUpdateForm(obj=company)

    if form.validate_on_submit():
        form.populate_obj(company)
        db.session.add(company)
        db.session.commit()
        flash('Taloyhtiön tiedot päivitettiin onnistuneesti', 'success')
        return redirect(url_for('main.housing_company'))

    return render_template('dashboard/housing_company_edit.html', form=form)



@main.route('/dashboard/taloyhtio/sopimukset', methods=['GET', 'POST'])
@login_required
def housing_company_contracts():
    form = ContractForm()
    if form.validate_on_submit():
        new_contract = Contract(
            contract_type=form.contract_type.data,
            company_name=form.company_name.data,
            housing_company_id=1  # Esimerkki taloyhtiön ID:stä
        )
        db.session.add(new_contract)
        db.session.commit()
        flash('Sopimus lisätty onnistuneesti!', 'success')
        return redirect(url_for('main.housing_company_contracts'))  # Päivitetään sivu
    contracts = Contract.query.filter_by(housing_company_id=1).all()
    return render_template('dashboard/housing_company_contract.html', contracts=contracts, form=form)

#Sopimuksen poistaminen
@main.route('/dashboard/taloyhtio/sopimukset/<int:contract_id>/delete', methods=['POST'])
@login_required
def delete_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    db.session.delete(contract)
    db.session.commit()
    flash('Sopimus poistettu onnistuneesti!', 'success')
    return redirect(url_for('main.housing_company_contracts')) 


#Asukkaiden hallinta
@main.route('/dashboard/asukkaiden_hallinta', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_residents():
    form = ResidentDeleteForm()
    # Hae kaikki asukkaat users-taulusta
    asukkaat = User.query.all()
    for asukas in asukkaat:
        print(f"Asukas: {asukas.username}") 

    return render_template('/dashboard/residents.html', asukkaat=asukkaat, form=form)

@main.route('/dashboard/asukkaiden_hallinta/poista/<int:asukas_id>', methods=['POST'])
@login_required
@admin_required
def manage_residents_delete(asukas_id):
    # Poistetaan asukas tietokannasta
    asukas = User.query.get_or_404(asukas_id)
    
    db.session.delete(asukas)
    db.session.commit()
    
    flash('Asukas poistettu onnistuneesti.', 'success')
    return redirect(url_for('main.manage_residents'))

@main.route('/dashboard/asukkaiden_hallinta/muokkaa/<int:asukas_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_residents_edit(asukas_id):
    # Haetaan asukas tietokannasta
    asukas = User.query.get_or_404(asukas_id)
    form = ResidentForm(obj=asukas)

    if form.validate_on_submit():
        # Päivitä asukkaan tiedot lomakkeen kenttien perusteella
        asukas.email = form.email.data
        asukas.username = form.username.data
        asukas.role_id = form.role_id.data
        asukas.active = form.active.data
        asukas.confirmed = form.confirmed.data
        asukas.phone = form.phone.data
        asukas.apartment = form.apartment.data
        
        try:
            db.session.commit()  # Tallenna muutokset tietokantaan
            flash('Asukkaan tiedot päivitettiin onnistuneesti', 'success')
            return redirect(url_for('main.manage_residents'))  # Siirry listaan
        except Exception as e:
            main.logger.error(f'Virhe asukkaan päivityksessä: {e}')
            flash('Päivityksessä tapahtui virhe', 'error')
        return redirect(url_for('main.manage_residents'))
    
    # Jos GET-pyyntö, renderöidään muokkauslomake asukkaan tiedoilla
    return render_template('dashboard/residents_edit.html', form=form, asukas=asukas)


@main.route('/user2', methods=['GET'])
@login_required
def user2(): 
    #kuva = tee_kuvanimi(current_user.id,current_user.img) if current_user.img else ''
    return render_template('user.html',user=current_user,API_KEY=current_app.config.get('GOOGLE_API_KEY'))


from flask import request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

@main.route('/user', methods=['GET', 'POST'])
@login_required
def user(): 
    form = UpdateUserForm()

    if form.validate_on_submit():  # Käytä lomakkeen validoimista
        # Päivitetään käyttäjän tiedot lomakkeesta
        if form.phone.data:
            current_user.phone = form.phone.data
        if form.apartment.data:
            current_user.apartment = form.apartment.data
        
        # Jos uusi salasana on asetettu, päivitetään se
        if form.new_password.data:
            current_user.password = generate_password_hash(form.new_password.data)
        
        # Tallenna muutokset tietokantaan
        db.session.commit()
        flash('Yhteystiedot päivitettiin onnistuneesti', 'success')
        return redirect(url_for('main.user'))

    # Esitäytetään lomake nykyisillä käyttäjän tiedoilla
    form.username.data = current_user.username
    form.phone.data = current_user.phone
    form.apartment.data = current_user.apartment

    return render_template('user.html', form=form, user=current_user, API_KEY=current_app.config.get('GOOGLE_API_KEY'))



@main.route('/poista', methods=['GET', 'POST'])
@login_required
@admin_required
def poista():
    # print("POISTA:"+request.form.get('id'))
    user = User.query.get(request.form.get('id'))
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        flash(f"Käyttäjä {user.name} on poistettu")
        return jsonify(OK="käyttäjä on poistettu.")
    else:
        return jsonify(virhe="käyttäjää ei löydy.")


@main.route('/api/events', methods=['GET'])
def get_events():
    tasks = Task.query.all()
    events = []
    for task in tasks:
        event = {
            "id": task.id,
            "title": task.task_name,
            "start": task.start_date.isoformat(),  # Muunna päivämäärä ISO 8601 -muotoon
            "end": task.end_date.isoformat(),  # Muunna päivämäärä ISO 8601 -muotoon
        }
        if task.end_date:  # Lisää päättymispäivä, jos se on olemassa
            event["end"] = task.end_date.isoformat()
        events.append(event)
    return jsonify(events)

