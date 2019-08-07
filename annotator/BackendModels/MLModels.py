from .khanaga import khanaga
from .silence import silence

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


class SilenceModel(MLModel):
    def __init__(self):
        # Give a descriptive name to your model
        self.name = "simple VAD model" 
        # This will be useful when we have multiple versions of the same model
        self.trained_on_date = "August 2019" 
        # This will store the output of the model for a given segment
        self.output = '' 

    def get_results(self, input_file, threshold=0.02):
        results = silence.get_silence(input_file, threshold)
        self.output = ' '.join(map(str, results))










