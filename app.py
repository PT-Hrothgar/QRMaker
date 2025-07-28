from django.core.validators import URLValidator, ValidationError
from flask import Flask, Response, render_template, request, session
from flask_session import Session
from io import BytesIO
from qrcode import make as make_qrcode

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create URL validator
_url_validator = URLValidator()


def is_valid_url(url):
    """Return True if the given string is a valid URL"""
    try:
        _url_validator(url)
    except ValidationError:
        return False
    else:
        return True


# Create example URL, and ensure it is valid
EXAMPLE_URL = "https://example.com"
assert is_valid_url(EXAMPLE_URL)


def save_qrcode_to_session(url):
    """
    Save the given URL and its QR code as a PNG image to session.

    The PNG data is saved in session["png_data"].
    The given URL is assumed to be valid; an error may occur if this is not the
    case.
    """
    # Get the QR code as a PIL.Image object
    img = make_qrcode(url)
    # An io.BytesIO object is writable like a file, but the data in it never
    # touches the disk
    io = BytesIO()
    # Save image to buffer
    img.save(io, format="png")
    # Save value of buffer in session
    session["png_data"] = io.getvalue()
    # Save URL to session
    session["url"] = url


@app.route("/")
def index():
    """Return the main page for this simple app"""
    return render_template(
        "index.html",
        url=session.get("url", EXAMPLE_URL),
        qr_in_navbar=request.headers.get("Host") == "turnerforever.com"
    )


@app.route("/set_url", methods=["POST"])
def set_url():
    """
    Create a QR code for the given URL and save it in the session as PNG data.

    The URL is taken from "request.form", the request's POST data. If it does
    not exist, or is invalid, return a status of 400. Otherwise, return a
    status of "201 Created".
    """
    # Ensure URL exists
    if (url := request.form.get("url")) is None:
        return Response(
            "No URL provided",
            status=400,
            mimetype="text/plain"
        )

    # Ensure URL is valid
    if not is_valid_url(url):
        return Response(
            "Invalid URL",
            status=400,
            mimetype="text/plain"
        )

    # Since URL is valid, we may save it and its QR code to session
    save_qrcode_to_session(url)

    # Return a response with a 201 Created status
    return Response(
        "Success!",
        status=201,
        mimetype="text/plain"
    )


@app.route("/img.png")
def get_png_image():
    """
    Return the request's corresponding PNG image of a QR code.

    If no such image is in session, create one for EXAMPLE_URL and
    return it.
    """
    # Get PNG data from session
    if (data := session.get("png_data")) is None:
        # Save a QR code for EXAMPLE_URL to session
        save_qrcode_to_session(EXAMPLE_URL)
        # Get the data for that code
        data = session.get("png_data")

    return Response(
        data,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Expires": "0",
            "Pragma": "no-cache",
            "X-Robots-Tag": "no-index"
        },
        mimetype="image/png"
    )

# The WSGI standard requires that the application object be called
# "application". We've created a very nice application object, but it's
# called "app", so we should make sure that "application" exists also.
application = app
