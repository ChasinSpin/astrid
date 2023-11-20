from PyQt5.QtGui import QValidator, QDoubleValidator, QIntValidator



class DoubleValidator(QDoubleValidator):

	def __init__(self, *__args):
		super().__init__(*__args)
		self.decimalPlaces = __args[2]


	def validate(self, p_str, p_int):
		if not p_str:
			return QValidator.Intermediate, p_str, p_int

		if p_str == '-' and self.bottom() < 0.0:
			return QValidator.Intermediate, p_str, p_int

		try:
			f = float(p_str)
		except:
			return QValidator.Invalid, p_str, p_int	

		if f < self.bottom():
			if self.bottom() < 0:
				return QValidator.Invalid, p_str, p_int	
			else:
				return QValidator.Intermediate, p_str, p_int
		elif f > self.top():
			if self.top() > 0:
				return QValidator.Invalid, p_str, p_int	
			else:
				return QValidator.Intermediate, p_str, p_int	
		else:
			return QValidator.Intermediate, p_str, p_int


	def fixup(self, input):
		print('Fixup')
		f = float(input)
		strFormat = '%%0.%df' % self.decimalPlaces
		if f < self.bottom():
			input = strFormat % self.bottom()
			print('1')
		elif f > self.top():
			input = strFormat % self.top()
			print('2')
		else:
			#input = strFormat % f
			#input += 't'
			#input.resize(0)
			input = strFormat % f
			print('3:', input)
			return strFormat % f
		return input



class IntValidator(QIntValidator):

	def __init__(self, *__args):
		super().__init__(*__args)


	def validate(self, p_str, p_int):
		if not p_str:
			return QValidator.Intermediate, p_str, p_int

		if p_str == '-' and self.bottom() < 0.0:
			return QValidator.Intermediate, p_str, p_int

		try:
			i = int(p_str)
		except:
			return QValidator.Invalid, p_str, p_int	

		if i < self.bottom():
			if self.bottom() < 0:
				return QValidator.Invalid, p_str, p_int	
			else:
				return QValidator.Intermediate, p_str, p_int
		elif i > self.top():
			if self.top() > 0:
				return QValidator.Invalid, p_str, p_int	
			else:
				return QValidator.Intermediate, p_str, p_int	
		else:
			return QValidator.Acceptable, p_str, p_int


	def fixup(self, input):
		i = int(input)
		if i < self.bottom():
			input = str(self.bottom())
		elif i > self.top():
			input = str(self.top())
		return input
