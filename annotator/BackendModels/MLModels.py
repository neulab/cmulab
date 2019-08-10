from .khanaga import khanaga
from .vad import vad
import requests

class MLModel:
    def __init__(self):
        self.name = "generic"
        self.trained_on_date = "March 2019"

    @property
    def trained_on(self):
        return self.trained_on_date

    def get_results(self, input):
        return


    def train_on(self, data):
        return self.train(data)



class KhanagaModel(MLModel):
    def __init__(self):
        self.name = "khanaga phone segmentation model"
        self.trained_on_date = "March 2019"
        self.output = ''

    def get_results(self, input_file):
        #results = [0,3,17,2019]
        results = khanaga.get_results(input_file) 
        self.output = ' '.join(map(str, results))

class VADModel(MLModel):
    def __init__(self):
        # Give a descriptive name to your model
        self.name = "simple VAD model" 
        # This will be useful when we have multiple versions of the same model
        self.trained_on_date = "August 2019" 
        # This will store the output of the model for a given segment
        self.output = '' 

    def get_results(self, input_file, threshold=0.2, window=0.5):
        v = vad.VoiceActivityDetector(input_file, window=window, threshold=threshold)
        raw_detection = v.detect_speech()
        speech_labels = v.convert_windows_to_readible_labels(raw_detection)    
        # This returns a list of dicts that mark the start/end of active spans
        self.output = speech_labels


class TranscriptionModel(MLModel):
    def __init__(self):
        # Give a descriptive name to your model
        self.name = "Xinjian English transcription model" 
        # This will be useful when we have multiple versions of the same model
        self.trained_on_date = "August 2019" 
        # This will store the output of the model for a given segment
        self.output = '' 

    def get_results(self, input_file):
        url = 'https://www.dictate.app/phone/english'
        files = {'file': (input_file, open(input_file, 'rb')),}
        r = requests.post(url, files=files)
        self.output = r.text










