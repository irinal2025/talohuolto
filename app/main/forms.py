from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, DateField, EmailField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Optional
from ..models import Role

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(0, 64)])
    about_me = TextAreaField('About me', validators=[Length(0, 256)])
    submit = SubmitField('Submit')

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]

class UpdateUserForm(FlaskForm):
    username = StringField('Nimi', validators=[DataRequired()])
    phone = StringField('Puhelinnumero (valinnainen)', validators=[Optional(), Length(max=15)])
    apartment = StringField('Huoneisto (valinnainen)', validators=[Optional(), Length(max=5)])
    new_password = PasswordField('Uusi salasana (valinnainen)', validators=[Optional()])
    submit = SubmitField('Päivitä tiedot')

class TaskForm(FlaskForm):
    task_name = StringField('Tehtävän nimi', validators=[DataRequired()])
    category = SelectField('Kategoria', choices=[('Kunnossapito', 'Kunnossapito'), ('Hoito', 'Hoito'), ('Parannustoimi', 'Parannustoimi'), ('Kokous', 'Kokous')])
    start_date = DateField('Aloituspäivämäärä', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Päättymispäivämäärä', format='%Y-%m-%d', validators=[DataRequired()])
    priority = SelectField('Prioriteetti', choices=[('Matala', 'Matala'), ('Keskitaso', 'Keskitaso'), ('Korkea', 'Korkea')])
    submit = SubmitField('Lisää tehtävä')

class TaskUpdateForm(FlaskForm):
    task_name = StringField('Tehtävän nimi', validators=[DataRequired()])
    category = SelectField('Kategoria', choices=[('Kunnossapito', 'Kunnossapito'), ('Hoito', 'Hoito'), ('Parannustoimi', 'Parannustoimi'), ('Kokous', 'Kokous')])
    start_date = DateField('Aloituspäivämäärä', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Päättymispäivämäärä', format='%Y-%m-%d', validators=[DataRequired()])
    priority = SelectField('Prioriteetti', choices=[('Matala', 'Matala'), ('Keskitaso', 'Keskitaso'), ('Korkea', 'Korkea')])
    submit = SubmitField('Päivitä tehtävä')


class FaultReportForm(FlaskForm):
    issue = StringField('Vian nimi', validators=[DataRequired()])
    reporter_name = StringField('Ilmoittajan nimi', validators=[DataRequired()])
    email = EmailField('Sähköposti', validators=[DataRequired(), Email()])
    issue_description = TextAreaField('Vian kuvaus', validators=[DataRequired()])
    actions = StringField('Toimenpiteet')  # Voidaan jättää tyhjäksi
    status = SelectField('Tila', choices=[
        ('pending', 'Odottaa'),
        ('approved', 'Hyväksytty'),
        ('delegated', 'Delegoitava'),
        ('in_progress', 'Käynnissä'),
        ('resolved', 'Ratkaistu'),
        ('closed', 'Suljettu'),
        ('rejected', 'Hylätty')
    ])
    submit = SubmitField('Ilmoita vika')

class FaultReportUpdateForm(FlaskForm):
    issue = StringField('Vian nimi', validators=[DataRequired()])
    reporter_name = StringField('Ilmoittajan nimi', validators=[DataRequired()])
    email = EmailField('Sähköposti', validators=[DataRequired(), Email()])
    issue_description = TextAreaField('Vian kuvaus', validators=[DataRequired()])
    actions = StringField('Toimenpiteet')  # Voidaan jättää tyhjäksi
    status = SelectField('Tila', choices=[
        ('pending', 'Odottaa'),
        ('approved', 'Hyväksytty'),
        ('delegated', 'Delegoitava'),
        ('in_progress', 'Käynnissä'),
        ('resolved', 'Ratkaistu'),
        ('closed', 'Suljettu'),
        ('rejected', 'Hylätty')
    ])
    submit = SubmitField('Päivitä')

class TalkootForm(FlaskForm):
    # Päivämäärä kenttä, joka vaatii päivämäärän syöttämistä
    date = DateField('Päivämäärä', format='%Y-%m-%d', validators=[DataRequired()])

    # Varusteet kenttä, joka vaatii varusteiden syöttämistä
    equipment = StringField('Varusteet', validators=[DataRequired()])
    


class TalkootHallintaForm(FlaskForm):
    date = DateField('Päivämäärä', validators=[DataRequired()])
    equipment = StringField('Varusteet', validators=[DataRequired()])
    submit = SubmitField('Lisää Talkoo')

class NotificationsForm(FlaskForm):
    title = StringField('Otsikko', validators=[DataRequired()])
    content = TextAreaField('Sisältö', validators=[DataRequired()])
    publish_date = DateField('Julkaisupäivä', validators=[DataRequired()])
    submit = SubmitField('Tallenne')


class HousingCompanyUpdateForm(FlaskForm):
    name = StringField('Nimi', validators=[DataRequired()])
    address = StringField('Osoite', validators=[DataRequired()])
    city = StringField('Kaupunki', validators=[DataRequired()])
    postal_code = StringField('Postinumero', validators=[DataRequired()])
    year_of_completion = StringField('Valmistusvuosi', validators=[Optional()])
    area = StringField('Pinta-ala', validators=[Optional()])
    manager_name = StringField('Isännöitsijän nimi', validators=[DataRequired()])
    manager_phone = StringField('Puhelin', validators=[Optional()])
    manager_email = StringField('Sähköposti', validators=[Optional(), Email()])
    submit = SubmitField('Tallenna')

class ContractForm(FlaskForm):
    contract_type = StringField('Sopimuksen tyyppi', validators=[DataRequired()])
    company_name = StringField('Yrityksen nimi', validators=[DataRequired()])
    submit = SubmitField('Lisää sopimus')

class ResidentForm(FlaskForm):
    email = StringField('Sähköposti', validators=[DataRequired(), Email(), Length(max=64)])
    username = StringField('Käyttäjätunnus', validators=[DataRequired(), Length(min=4, max=64)])
    role_id = StringField('Rooli ID', validators=[Optional(), Length(max=10)])
    active = BooleanField('Aktiivinen', default=True)
    confirmed = BooleanField('Vahvistettu', default=False)
    phone = StringField('Puhelin', validators=[Optional(), Length(max=15)])
    apartment = StringField('Asunto', validators=[Optional(), Length(max=5)])
    submit = SubmitField('Päivitä')

class ResidentDeleteForm(FlaskForm):
    submit = SubmitField('Poista')