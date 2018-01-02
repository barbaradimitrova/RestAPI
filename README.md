# Run python app.py
To sign up:
curl -i -X POST -H "Content-Type: application/json" -d '{"email":"barbaradimm@yahoo.de","password":"python"}' http://127.0.0.1:5000/api/users/signup

    HTTP/1.0 200 OK
    Content-Type: application/json
    Set-Cookie: session=.eJyrVopPy0kszkgtVrKKrlZSKIFQSUpWSsnGYVmRRmFVyeW2tkq1OlDRwGCnrCQj09zECK-SyIiggiQjk_SocMOMxPDy9ER3typPd6-cqHCT9GSjsNIUZxOgzlggBACESiDQ.DS1ARg.icRfRzxIEQ_eWxTqx8VGBDOEGfs; HttpOnly; Path=/
    Content-Length: 84
    Server: Werkzeug/0.12.2 Python/2.7.13
    Date: Tue, 02 Jan 2018 16:09:42 GMT

    {
      "Info": "Please check you email to confirm registration:barbaradimm@yahoo.de"
    }


if same request is done (and the user was confirmed):
curl -i -X POST -H "Content-Type: application/json" -d '{"email":"barbaradimm@yahoo.ca","password":"python"}' http://127.0.0.1:5000/api/users/signup
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 58
    Server: Werkzeug/0.12.2 Python/2.7.13
    Date: Tue, 02 Jan 2018 16:09:31 GMT

    {
      "Error": "User already exists:barbaradimm@yahoo.ca"
    }

if: wrong json input:
curl -i -X POST -H "Content-Type: application/json" -d '{"username":"barbaradimm@yahoo.de","password":"python"}' http://127.0.0.1:5000/api/users/signup
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 51
    Server: Werkzeug/0.12.2 Python/2.7.13
    Date: Tue, 02 Jan 2018 16:10:58 GMT

    {
      "Error": "Please provide email and password"
    }

To sign in:
curl -i -X POST -H "Content-Type: application/json" -d '{"email":"barbaradimm@yahoo.de","password":"python"}' http://127.0.0.1:5000/api/users/login
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 51
    Server: Werkzeug/0.12.2 Python/2.7.13
    Date: Tue, 02 Jan 2018 16:11:57 GMT

    {
      "Data": "Hello, barbara.dimitrova@gmail.com"
    }