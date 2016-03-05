import os

# default recaptcha keys for testing
RECAPTCHA_PUBLIC_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
RECAPTCHA_PRIVATE_KEY = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

# application root
# APPLICATION_ROOT = '/'
# If, for instance you're not running at root, and it's something more among the lines of
# example.com/becgi
# set APPLICATION_ROOT to '/becgi/'

# Flask secret key
SECRET_KEY = os.urandom(128)

# Debug. Turn off on deployment.
DEBUG = True
