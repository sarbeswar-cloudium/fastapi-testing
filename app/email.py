from fastapi_mail import ConnectionConfig, FastMail
from starlette.responses import JSONResponse
from app import schemas

# Gmail

# conf = ConnectionConfig(
#     MAIL_USERNAME ="sarbeswar.cloudiumsoft@gmail.com",
#     MAIL_PASSWORD = "xtbgnxrrbkkdpwjo",
#     MAIL_FROM = "sarbeswar.cloudiumsoft@gmail.com",
#     MAIL_PORT = 465,
#     MAIL_SERVER = "smtp.gmail.com",
#     MAIL_STARTTLS = False,
#     MAIL_SSL_TLS = True,
#     USE_CREDENTIALS = True,
#     VALIDATE_CERTS = False
# )


# Brevo

conf = ConnectionConfig(
    MAIL_USERNAME ="8f5cf6001@smtp-brevo.com",
    MAIL_PASSWORD = "cUpFyJATNgafqK0C",
    MAIL_FROM = "sarbeswar.cloudiumsoft@gmail.com",
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp-relay.brevo.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = False
)

fastmail = FastMail(conf)

