from datas.Dataset import Dataset

class ValidationSet(Dataset):

	def __init__(self, **kwargs):
		Dataset.__init__(self, **kwargs)
		#self.preprocess()
		self.preprocess_harmony()