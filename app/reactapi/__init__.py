from flask import Blueprint

reactapi = Blueprint('reactapi', __name__)

from . import views

# Myöhäinen tuonti
#def initialize_views():
#    from . import main  # Tämä tuodaan vasta, kun sitä todella tarvitaan