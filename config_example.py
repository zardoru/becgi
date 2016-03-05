import os

# default recaptcha keys for testing
RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

# Flask secret key
SECRET_KEY = os.urandom(128)

# Debug. Turn off on deployment.
DEBUG = True
