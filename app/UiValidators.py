from PyQt5.QtGui import QValidator, QDoubleValidator, QIntValidator


class DoubleValidator(QDoubleValidator):
	def __init__(self, *__args):
		super().__init__(*__args)

	def validate(self, p_str, p_int):
		if not p_str:
			return QValidator.Intermediate, p_str, p_int

		try:
			f = float(p_str)
		except:
			if p_str == '-' and self.bottom() < 0.0:
				return QValidator.Acceptable, p_str, p_int
			else:
				return QValidator.Invalid, p_str, p_int	

		if self.bottom() <= f <= self.top():
			return QValidator.Acceptable, p_str, p_int
		else:
			return QValidator.Invalid, p_str, p_int


class IntValidator(QIntValidator):
	def __init__(self, *__args):
		super().__init__(*__args)

	def validate(self, p_str, p_int):
		if not p_str:
			return QValidator.Intermediate, p_str, p_int

		try:
			i = int(p_str)
		except:
			if p_str == '-' and self.bottom() < 0.0:
				return QValidator.Acceptable, p_str, p_int
			else:
				return QValidator.Invalid, p_str, p_int	

		if self.bottom() <= i <= self.top():
			return QValidator.Acceptable, p_str, p_int
		else:
			return QValidator.Invalid, p_str, p_int
