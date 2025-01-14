import os
import click
from app import create_app, db
from flask_migrate import Migrate
from app.models import User, Role


app = create_app(os.getenv('FLASK_CONFIG') or 'default')


# Debug-tilan tarkistus
print(f"Current config: {app.config['DEBUG']}")  # Tämä rivi tulostaa debug-tilan

migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    #from app.models import User, Role
    return dict(db=db, User=User, Role=Role)

@app.cli.command()
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


# Käynnistä sovelluksen konteksti
with app.app_context():
    # Suorita tietokannan kysely
    from sqlalchemy import text
    result = db.session.query(text("1")).from_statement(text("SELECT 1")).all()
    print(result)

if __name__ == '__main__':
    app.run(debug=True)
