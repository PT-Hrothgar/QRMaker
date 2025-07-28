# QRMaker
Simple Flask app for generating QR codes.

This app is very simple to use: to generate a QR code for any URL, once you have gone to wherever it is hosted (maybe [turnerforever.com](http://turnerforever.com)?), all you have to do is clear the text input area of the URL it already contains (`https://example.com`) and enter your own URL in. The QR code will automatically be generated and displayed below with an option to download it as a PNG image.

### How It Works
In this app, there is only one page actually meant for the user to view: the file [index.html](templates/index.html), which is rendered for the path `/`. Its focus point is an HTML `<input>` element for a URL which contains `https://example.com` by default, and is monitored by JavaScript. The file [qr_app.js](static/qr_app.js) adds an `input` event listener to it so that upon input, it does the following:
- First it ensures the inputted URL starts with "http://" or "https://"
- If it does, then it submits a POST request to the path `/set_url` containing the URL.
- Back on the server, `app.py` uses Django's URL validator to ensure that the URL is actually valid, and if it is not, it returns a status of 400. In this case, an "Invalid URL" message will be displayed for the user.
- If the URL is valid, `app.py` uses the Python module `qrcode` to create a `PIL.Image` representation of a QR code for the URL, and saves the data to the request's `session` in the PNG format. Then the `/set_url` path returns a status of 201 Created.
- Upon a returned status of 201, the JavaScript in `qr_app.js` renders an image of the QR code underneath the `<input>` element. The image always has an `href` of "img.png", but the JavaScript suffixes a random piece of GET data to it (and to the `href` of the download link) to ensure that the image will be reloaded.
- The path `/img.png` is routed to a view that simply reads the PNG data from `session`, and returns it with the appropriate `Content-Type`. It uses HTTP headers to ensure that the image will not be cached.
