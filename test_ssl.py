import ssl

try:
    # Luo SSL-konteksti
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # Lataa sertifikaatit
    ssl_context.load_cert_chain(certfile='cert.pem', keyfile='key.pem')
    print("Sertifikaatit ladattu onnistuneesti")
except Exception as e:
    print(f"Sertifikaattien lataaminen epäonnistui: {e}")
