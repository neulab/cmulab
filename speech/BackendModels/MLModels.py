
from .khanaga import khanaga


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
		results = khanaga.get_results(input_file) 
		self.output = ' '.join(map(str, results))








