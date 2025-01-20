import os
import click
from app import create_app, db
from flask_migrate import Migrate
from app.models import User, Role
from flask_cors import CORS
import ssl

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Määritä CORS, jotta React-sovellus voi tehdä pyyntöjä
#CORS(app, resources={r"/reactapi/*": {"origins": "https://localhost:5173"}}, supports_credentials=True)
CORS(app, resources={r"/reactapi/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)


# Debug-tilan tarkistus
print(f"Current config: {app.config['DEBUG']}")  # Tämä rivi tulostaa debug-tilan

migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    #from app.models import User, Role
    return dict(db=db, User=User, Role=Role)

@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


# Käynnistä sovelluksen konteksti
#with app.app_context():
    # Suorita tietokannan kysely
#    from sqlalchemy import text
#    result = db.session.query(text("1")).from_statement(text("SELECT 1")).all()
#    print(result)

# Testaa tietokantayhteys
with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")

def generate_self_signed_cert(cert_file, key_file):
    """
    Luo itse allekirjoitetut sertifikaatit, jos niitä ei ole olemassa.
    """
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("Sertifikaatteja ei löytynyt. Luodaan itse allekirjoitetut sertifikaatit...")
        os.system(f'openssl req -x509 -newkey rsa:4096 -keyout {key_file} -out {cert_file} -days 365 -nodes')
    else:
        print("Sertifikaatit löytyvät valmiina.")

if __name__ == '__main__':
    # Sertifikaattien sijainnit
    CERT_FILE = 'cert.pem'
    KEY_FILE = 'key.pem'

    # Luo sertifikaatit, jos niitä ei ole
    generate_self_signed_cert(CERT_FILE, KEY_FILE)

    # Käynnistä Flask-sovellus SSL-tuen kanssa
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=(CERT_FILE, KEY_FILE))

