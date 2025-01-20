from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (PrivateFormat, Encoding, NoEncryption)
from cryptography.x509 import CertificateBuilder, Name, NameAttribute
from cryptography.x509.oid import NameOID
from datetime import datetime, timedelta, timezone

# Luodaan yksityinen avain
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# Tallenna yksityinen avain tiedostoon
with open("key.pem", "wb") as key_file:
    key_file.write(private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=NoEncryption()
    ))

# Luodaan itse allekirjoitettu sertifikaatti
subject = issuer = Name([NameAttribute(NameOID.COMMON_NAME, u"localhost")])
cert = CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(private_key.public_key()) \
    .serial_number(1000).not_valid_before(datetime.now(timezone.utc)) \
    .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365)) \
    .sign(private_key, hashes.SHA256())

# Tallenna sertifikaatti tiedostoon
with open("cert.pem", "wb") as cert_file:
    cert_file.write(cert.public_bytes(Encoding.PEM))
