# docapi

Requirements:
* python 3.6+
* django 2.1
* djangorestframework
* coreapi
* pyyaml
* django-filter
* markdown
* httpie

Install the requirements
~~~~
pip install django djangorestframework coreapi pyyaml django-filter markdown httpie
~~~~

Starting up the server:

~~~~
# Set up
python manage.py makemigrations speech
python manage.py sqlmigrate speech
python manage.py migrate


# Start the server
python manage.py runserver
~~~~

If everything runs smoothly, the server will be available through `http://localhost:8000/speech/`.
