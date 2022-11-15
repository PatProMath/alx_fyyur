from enum import Enum

class Genre(Enum):
	ALTERNATIVE='Alternative' #Should be named as constants. Not sure if this is true.
	BLUES='Blues'
	CLASSICAL='Classical'
	COUNTRY='Country'
	ELECTRONIC='Electronic'
	FOLK='Folk'
	FUNK='Funk'
	HIPHOP='Hip-Hop' #Python variables cannot be separated by space or hypens in naming!
	HEAVYMETAL='Heavy Metal'
	INSTRUMENTAL='Instrumental'
	JAZZ='Jazz'
	MUSICALTHEATRE='Musical Theatre'
	POP='Pop'
	PUNK='Punk'
	RB='R&B'
	REGGAE='Reggae'
	ROCK='Rock n Roll'
	SOUL='Soul'
	OTHER='Other'

	@classmethod
	def choices(cls):
		""" Methods decorated with @classmethod can be called statically without having an instance of the class."""
		return [(choice.value, choice.value) for choice in cls]
		# To explain replacing (choice.name, choice.value) with (choice.name, choice.value), it was in short the only way to define constants and still maintain the previous genres choices.


class State(Enum):
	AL='AL'
	AK='AK'
	AZ='AZ'
	AR='AR'
	CA='CA'
	CO='CO'
	CT='CT'
	DE='DE'
	DC='DC'
	FL='FL'
	GA='GA'
	HI='HI'
	ID='ID'
	IL='IL'
	IN='IN'
	IA='IA'
	KS='KS'
	KY='KY'
	LA='LA'
	ME='ME'
	MT='MT'
	MD='MD'
	MA='MA'
	MI='MI'
	MN='MN'
	MS='MS'
	MO='MO'
	NE='NE'
	NV='NV'
	NH='NH'
	NJ='NJ'
	NM='NM'
	NY='NY'
	NC='NC'
	ND='ND'
	OH='OH'
	OK='OK'
	OR='OR'
	PA='PA'
	RI='RI'
	SC='SC'
	SD='SD'
	TN='TN'
	TX='TX'
	UT='UT'
	VT='VT'
	VA='VA'
	WA='WA'
	WV='WV'
	WI='WI'
	WY='WY'

	@classmethod
	def choices(cls):
		return [(choice.name, choice.value) for choice in cls]


# value=[(choice.name, choice.value) for choice in State]
# print(value)