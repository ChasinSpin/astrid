from PyQt5.QtGui import QValidator, QDoubleValidator, QIntValidator



class DoubleValidator(QDoubleValidator):

	def __init__(self, *__args):
		super().__init__(*__args)
		self.decimalPlaces = __args[2]
		self.lineedit = __args[3]
		self.originalValue = None


	def _acceptableChars(self, value, allowed_chars):
		""" Returns true if value only contains allowed characters """
		allowedChars = set(allowed_chars)
		valueStr = set(value)
		return valueStr.issubset(allowedChars)


	def validate(self, p_str, p_pos):
		# p_str is what we're validating (everything is a string on input)
		# p_pos is the position of the cursor

		# We store the original value the first time validate is called, which is when the form is setup
		if self.originalValue is None:
			self.originalValue = p_str

		if self.bottom() < 0 or self.top() < 0:
			minusAllowed = True
		else:
			minusAllowed = False

		focus = self.lineedit.hasFocus()

		#print('Validate: str<%s> pos:%d focus:%d originalValue:<%s>' % (p_str, p_pos, focus, self.originalValue))

		# If the field is empty, - or ., this only allow if we haven't finished
		if not p_str or p_str == '' or p_str == '.' or  (p_str == '-' and minusAllowed):
			if focus:
				return QValidator.Intermediate, p_str, p_pos
			else:
				return QValidator.Invalid, p_str, p_pos

		# Determined the allowed characters in the field, if bottom or top are below zero, allow minus too
		allowedChars = '0123456789.'
		if minusAllowed:
			allowedChars += '-'

		if not self._acceptableChars(p_str, allowedChars):
			return QValidator.Invalid, p_str, p_pos

		# If the number is malformed (2 negatives, 2 periods for example), we want to return invalid
		try:
			f = float(p_str)
		except:
			return QValidator.Invalid, p_str, p_pos	

		# A field can be exited via TAB, Return, Click on something else, or a confirmation action (e.g. save button), they behave as follows:
		# 	TAB = Acceptable (save, no fixup, focus=0)
		# 	Return = Intermediate (fixup, no save, focus = 1)
		# 	Click = Acceptable (save, no fixup, focus = 0)
		# 	Save Changes = Acceptable (save, no fixup, focus = 0)
		# Although Intermediate does not save, usuaully this is followed by a save button and will save
		if focus:
			#print('*** VALID: Intermediate')
			return QValidator.Intermediate, p_str, p_pos
		else:
			#print('*** VALID: Acceptable')
			p_str = self.fixup(p_str)
			return QValidator.Acceptable, p_str, p_pos


	def fixup(self, p_str):
		#print('Fixup: <%s> OriginalValue:<%s>' % (p_str, self.originalValue))
		if not p_str or p_str == '':
			p_str = self.originalValue

		try:
			f = float(p_str)
		except:
			p_str = self.originalValue
			f = float(p_str)

		if f < self.bottom():
			f = self.bottom()
		if f > self.top():
			f = self.top()

		strFormat = '%%0.%df' % self.decimalPlaces
		p_str = strFormat % f
	
		#print('Fixup changed to: <%s>' % p_str)
		self.originalValue = p_str
		self.lineedit.setText(p_str)

		return p_str



class IntValidator(QIntValidator):

	def __init__(self, *__args):
		super().__init__(*__args)
		self.lineedit = __args[2]
		self.originalValue = None


	def _acceptableChars(self, value, allowed_chars):
		""" Returns true if value only contains allowed characters """
		allowedChars = set(allowed_chars)
		valueStr = set(value)
		return valueStr.issubset(allowedChars)


	def validate(self, p_str, p_pos):
		# p_str is what we're validating (everything is a string on input)
		# p_pos is the position of the cursor

		# We store the original value the first time validate is called, which is when the form is setup
		if self.originalValue is None:
			self.originalValue = p_str

		if self.bottom() < 0 or self.top() < 0:
			minusAllowed = True
		else:
			minusAllowed = False

		focus = self.lineedit.hasFocus()

		#print('Validate: str<%s> pos:%d focus:%d originalValue:<%s>' % (p_str, p_pos, focus, self.originalValue))

		# If the field is empty, - or this only allow if we haven't finished
		if not p_str or p_str == '' or  (p_str == '-' and minusAllowed):
			if focus:
				return QValidator.Intermediate, p_str, p_pos
			else:
				return QValidator.Invalid, p_str, p_pos

		# Determined the allowed characters in the field, if bottom or top are below zero, allow minus too
		allowedChars = '0123456789'
		if minusAllowed:
			allowedChars += '-'

		if not self._acceptableChars(p_str, allowedChars):
			return QValidator.Invalid, p_str, p_pos

		# If the number is malformed (2 negatives for example), we want to return invalid
		try:
			i = int(p_str)
		except:
			return QValidator.Invalid, p_str, p_pos	

		# A field can be exited via TAB, Return, Click on something else, or a confirmation action (e.g. save button), they behave as follows:
		# 	TAB = Acceptable (save, no fixup, focus=0)
		# 	Return = Intermediate (fixup, no save, focus = 1)
		# 	Click = Acceptable (save, no fixup, focus = 0)
		# 	Save Changes = Acceptable (save, no fixup, focus = 0)
		# Although Intermediate does not save, usuaully this is followed by a save button and will save
		if focus:
			#print('*** VALID: Intermediate')
			return QValidator.Intermediate, p_str, p_pos
		else:
			#print('*** VALID: Acceptable')
			p_str = self.fixup(p_str)
			return QValidator.Acceptable, p_str, p_pos


	def fixup(self, p_str):
		#print('Fixup: <%s> OriginalValue:<%s>' % (p_str, self.originalValue))
		if not p_str or p_str == '':
			p_str = self.originalValue

		try:
			i = int(p_str)
		except:
			p_str = self.originalValue
			i = int(p_str)

		if i < self.bottom():
			i = self.bottom()
		if i > self.top():
			i = self.top()

		strFormat = '%d'
		p_str = '%d' % i
	
		#print('Fixup changed to: <%s>' % p_str)
		self.originalValue = p_str
		self.lineedit.setText(p_str)

		return p_str
