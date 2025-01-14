from datetime import datetime, timedelta, timezone
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager



class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    active = db.Column(db.Boolean, default=True, server_default='1')
    confirmed = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime(), default=lambda: current_app.config['GET_TIME']())
    phone = db.Column(db.String(15), nullable=True)  # Puhelinnumero, max 15 merkkiä
    apartment = db.Column(db.String(5), nullable=True) 

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            admin_email = current_app.config.get('TALOHUOLTO_ADMIN', None)
            if admin_email and self.email == admin_email:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return f'<User {self.email}>'

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt=current_app.config['SECURITY_PASSWORD_SALT'], expires=expiration)


    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'], salt=current_app.config['SECURITY_PASSWORD_SALT'])
        try:
            data = s.loads(token)
        except:
            return False
        if data['user_id'] == self.id:
            self.confirmed = True
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def generate_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'reset': self.id}, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        db.session.commit()
        return True

    def generate_email_change_token(self, new_email):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        db.session.commit()
        return True

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def can(self, perm):
        #return self.role is not None and self.role.has_permission(perm)
        return self.role is not None and (self.role.permissions & perm) == perm

    def ping(self):
        self.last_seen = current_app.config['GET_TIME']()
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}, email {self.email}>'


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class HousingCompany(db.Model):
    __tablename__ = 'housing_companies' # Taloyhtiöt
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    manager_name = db.Column(db.String(100), nullable=True)  # Ei pakollinen
    manager_phone = db.Column(db.String(20), nullable=True)
    manager_email = db.Column(db.String(100), nullable=True)
    area = db.Column(db.Integer, nullable=True)
    year_of_completion = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Lisää sopimukset
    contract_list = db.relationship('Contract', back_populates='housing_company')

    def __repr__(self):
        return f'<HousingCompany {self.name}>'

class Contract(db.Model):
    __tablename__ = 'contracts' # Taloyhtiöt
    id = db.Column(db.Integer, primary_key=True)
    contract_type = db.Column(db.String(100), nullable=False)  # Esim. "Kiinteistönhuolto"
    company_name = db.Column(db.String(255), nullable=False)  # Esim. "Seinäjoen Kiinteistöhuolto Oy"
    housing_company_id = db.Column(db.Integer, db.ForeignKey('housing_companies.id'), nullable=False)

    # Käytetään back_populates-vaihtoehtoa
    housing_company = db.relationship('HousingCompany', back_populates='contract_list')

    def __repr__(self):
        return f'<Contract {self.contract_type} - {self.company_name}>'


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.Enum('Kunnossapito', 'Hoito', 'Parannustoimi', 'Kokous'), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.Enum('Matala', 'Keskitaso', 'Korkea'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class FaultReport(db.Model):
    __tablename__ = 'fault_reports'
    id = db.Column(db.Integer, primary_key=True)
    issue = db.Column(db.String(255), nullable=False)
    reporter_name = db.Column(db.String(255), nullable=False)
    report_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    actions = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'approved', 'delegated', 'in_progress', 'resolved', 'closed', 'rejected', name='status_enum'), default='pending')
    email = db.Column(db.String(255), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)


class Talkoot(db.Model):
    __tablename__ = 'talkoot'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    equipment = db.Column(db.String(255), nullable=False)

    # Suhde TalkootParticipantsiin
    # participants = db.relationship('TalkootParticipants', back_populates='talkoo', lazy=True)

    def __repr__(self):
        return f'<Talkoot {self.id}>'

class TalkootParticipants(db.Model):
    __tablename__ = 'talkoot_participants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    talkoot_id = db.Column(db.Integer, db.ForeignKey('talkoot.id'), nullable=False)

    # Oikea suhde Talkoot-malliin
    # talkoo = db.relationship('Talkoot', back_populates='participants')

    def __repr__(self):
        return f"<Participant {self.name} for Talkoo {self.talkoo.date}>"


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    publish_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<Notifications {self.title}>'
