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
python manage.py migrate
~~~~

These should print basically write the necessary migrations and create a database `db.sqlite3`, initialize its database schema:
~~~~
Migrations for 'speech':
  speech/migrations/0001_initial.py
    - Create model Annotation
    - Create model Corpus
    - Create model Mlmodel
    - Create model Segment
    - Create model AudioAnnotation
    - Create model SpanTextAnnotation
    - Create model TextAnnotation
    - Add field segment to annotation

Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, speech
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying sessions.0001_initial... OK
  Applying speech.0001_initial... OK
~~~~

Now we can start the server
~~~~
# Start the server
python manage.py runserver
~~~~

If everything runs smoothly, the root of the api will be available through `http://localhost:8000/speech/`.
If you follow the localhost link for "users", you'll see no users are registered. 

So let's create a super user. I'll use username = 'antonis' and password = 'password123'.
In another terminal do the following and provide the necessary info:
~~~~
python manage.py createsuperuser
~~~~
Now, using the `login` button on the top right corner of the browsable API you can login as yourself.

Now refreshing the localhost page will list a user with some attributes (note e.g. that the password is not visible).
You can see how the "corpus" is empty, as there are no corpora owned by this user yet. The SQL database is empty.
The script `populate.py` adds a couple of entries in the database: models, corpora, and segments with annotations.
With the server running, go the other terminal and run:
~~~~
python manage.py shell < populate.py 
~~~~

Refrshing the users page again, there should be a couple of corpora associated with this user.
You can follow each corpus' link, or you can list all corpora by navigating to `http://localhost:8000/speech/corpus/`.

The same for listing all models (`http://localhost:8000/speech/model/`) or all segments (`http://localhost:8000/speech/segment/`) or all annotations (`http://localhost:8000/speech/annotation/`).

Let's go back to the list of all models (`http://localhost:8000/speech/model/`). On the up right corner there another button named `filter`.
This means that the models are searchable by some pre-defined filters (in this case `status` and `tags`) and submitting this filter also shows
the necessary URL: e.g. for selecting the models with 'ready' status, the query should be `GET /speech/model/?status=ready`

One can also filter the segments (based on the corpus they belong to) or the annotations (based on the segment they belong to) in the same way, using the filters.

Alternatively, one can access the segments of a specific corpus with a query using the corpus. For example, navigating to `http://localhost:8000/speech/corpus/2/segments/`
will list the three segments that belong to corpus 2.

The same thing can happen between segments and their annotations, e.g. navigate to `http://localhost:8000/speech/segment/2/annotations/` to see all the annotations
associated with segment 2.

`Annotation` is a generic class. In fact, annotations are realized with three more specific subclasses: `AudioAnnotation`, `TextAnnotation`, and `SpanTextAnnotation`.
You can list all the annotations of a specific subclass by going to the appropriate URL e.g. `http://localhost:8000/speech/spantextannotation/`.
Notice how (and you can confirm this in the `populate.py` script) only 2 of the 4 annotations belong to `SpanTextAnnotation`, but `Annotation` lists all of them.
The different subclasses are serialized differently: e.g. `SpanTextAnnotation` includes `start` and `end` fields, while `AudioAnnotation` includes an `audio_file_format` field.

TODO(aanastas): Provide info about the type of the annotation in a way other than the subclass name.

The different Annotations can be filtered using the predefined filters, based on their status (todo(aanastas): talk to Graham) and based on the segment they belong to.

We can use the API's forms (at the bottom) to create new entries. e.g. in the bottom of `http://localhost:8000/speech/segment/` you can add a name for a new segment (e.g. 's5')
and click POST.
Or even better, let's use a mock client (with httpie) to move things around. We will again create a couple new segments, without specifying the corpus that they belong to.
In the other terminal (with the server still running) run (this shows the two formats you can pass information to the api):
```
 http -a antonis:password123 --form POST http://127.0.0.1:8000/speech/segment/ name="s6"
 http -a antonis:password123 --json POST http://127.0.0.1:8000/speech/segment/ {"name"="s7",}
 ```

These segments are not tied to a particular corpus. We can tie them with the following PUT calls (notice how this can be done over multiple segments):
```
http -a antonis:password123 --json PUT http://localhost:8000/speech/corpus/1/addsegments/5/
http -a antonis:password123 --json PUT http://localhost:8000/speech/corpus/2/addsegments/6,7/
```
You should receive a successfull 202_ACCEPTED status.

Similarly, you can remove segments from a corpus (this will not delete them, there's a separate call for that). This will set segment 6's corpus to null:
~~~~
http -a antonis:password123 --json PUT http://localhost:8000/speech/corpus/2/removesegments/6/
~~~~

TODO(aanastas): Implement the same things for moving annotations between segments, and segments between corpora

Let's say we want to create a new text annotation about the speaker. Then we can do:
~~~~
http -a antonis:password123 --json POST http://127.0.0.1:8000/speech/textannotation/ {"field_name"="speaker","text"="Maria"}
~~~~

In order to train a model, one could make a call like the following:
~~~~
http -a antonis:password123 --json POST http://127.0.0.1:8000/speech/model/1/train
~~~~
TODO(aanastas,graham): figure out how training specs look and how these trainModel functions should be implemented (terminal calls?)

Finally, the automatically generated API schema can be found in `http://localhost:8000/schema/`, from where you can choose the format and download it.
Or, you could run in order to generate the schema that is also available in this repository.
~~~~
python manage.py generateschema > schema.yaml
~~~~

TODO(aanastas): Figure out how to include the function calls (and not just APIviews in the schema).
TODO(aanastas): Figure out how to properly set the {format} fields in the schema -- doesn't seem to be iportant though.



