# CMU Linguistic Annotation Backend  -- How to add a new BackEnd Model

In this example we will add a new back-end model.
We will use the VAD model `silence` (which, if you notice, is not readily available).

The first step is to create a subdirectory under `annotator/BackendModels` where the model's code will be stored:
~~~~
mkdir -p annotator/BackendModels/silence
# add your code here -- (if you cloned the repo you should already have the code here)
# Make sure to add an __init__.py file
touch annotator/BackendModels/silence/__init__.py
~~~~

With the code all set up and ready to be used, go to `annotator/BackendModels/MLModels.py` and create a model class for your new model:
~~~~
class SilenceModel(MLModel):
    def __init__(self):
    	# Give a descriptive name to your model
        self.name = "simple VAD model" 
        # This will be useful when we have multiple versions of the same model
        self.trained_on_date = "August 2019" 
        # This will store the output of the model for a given segment
        self.output = '' 

    def get_results(self, input_file):
    	# You'll have to implement this
    	# Make sure to store the output in self.output
    	<your code here>
    	self.output = 
~~~~
We provide the simple implementation of this in `annotator/BackendModels/MLModels-silence_added.py`

With this implemented (do `cp annotator/BackendModels/MLModels-silence_added.py annotator/BackendModels/MLModels.py`) you can programmatically call it through a client.
For example, take a look at `example-clients/cmulab_elan-silence_added.py` which uses the added VAD model.

e.g. running the following should produce two new .eaf files under `example-clients/output`, which should have a new `VAD` tier. 
~~~~
cd example-clients
python cmulab_elan-silence_added.py --input_dir Chatino/ --input_tiers en --output_dir output --output_tier VAD --model_name vad
~~~~


You can also add an entry for this model in the `populate.py` script, e.g. by adding
~~~~
model4=Mlmodel(name="VAD_model", modelTrainingSpec="silence", status='ready', tags=Mlmodel.VAD)
model4.save()
~~~~


