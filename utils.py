from kavenegar import *
import pyotp


def generate_otp():
    code = pyotp.TOTP(pyotp.random_base32(),interval=300)
    return code.now()


def send_otp(phone_number, code):
	try:
		api = KavenegarAPI('482B764F6B3876696654796774384B2B4D5543727944547270746659574B7A4E765432624177586678706B3D')
		params = {
			'sender': '',
			'receptor': phone_number,
			'message': f'{code} کد تایید شما '
		}
		response = api.sms_send(params)
		print(response)
	except APIException as e:
		print(e)
	except HTTPException as e:
		print(e)