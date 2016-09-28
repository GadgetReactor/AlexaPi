import time 
import RPi.GPIO as GPIO

from baseplatform import BasePlatform
from alexapi.bcolors import bcolors


class RaspberrypiPlatform(BasePlatform):

	def __init__(self, config):
		super(RaspberrypiPlatform, self).__init__(config)

		self.__config = config
		self.__pconfig = config['platforms']['raspberrypi']
		self.__pconfig['lights'] = [self.__pconfig['rec_light'], self.__pconfig['plb_light']]

		self.button_pressed = False

	def setup(self):
		GPIO.setwarnings(False)
		GPIO.cleanup()
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.__pconfig['button'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.__pconfig['lights'], GPIO.OUT)
		GPIO.output(self.__pconfig['lights'], GPIO.LOW)

	def indicate_setup_failure(self):
		while True:
			for x in range(0, 5):
				time.sleep(.1)
				GPIO.output(self.__pconfig['rec_light'], GPIO.HIGH)
				time.sleep(.1)
				GPIO.output(self.__pconfig['rec_light'], GPIO.LOW)

	def indicate_setup_success(self):
		for x in range(0, 5):
			time.sleep(.1)
			GPIO.output(self.__pconfig['plb_light'], GPIO.HIGH)
			time.sleep(.1)
			GPIO.output(self.__pconfig['plb_light'], GPIO.LOW)

	def after_setup(self):
		# threaded detection of button press
		GPIO.add_event_detect(self.__pconfig['button'], GPIO.FALLING, callback=self.detect_button, bouncetime=100)

	def indicate_recording(self, state=True):
		GPIO.output(self.__pconfig['rec_light'], GPIO.HIGH if state == True else GPIO.LOW)

	def indicate_playback(self, state=True):
		GPIO.output(self.__pconfig['plb_light'], GPIO.HIGH if state == True else GPIO.LOW)

	def detect_button(self, channel):
		buttonPress = time.time()
		self.button_pressed = True

		if self.__config['debug']: print("{}Button Pressed! Recording...{}".format(bcolors.OKBLUE, bcolors.ENDC))

		time.sleep(.5)  # time for the button input to settle down
		while (GPIO.input(self.__pconfig['button']) == 0):
			time.sleep(.1)
			# if time.time() - buttonPress > 10:  # pressing button for 10 seconds triggers a system halt
			# 	play_audio(resources_path + 'alexahalt.mp3')
			# 	if self.__config['debug']:
			# 		print("{} -- 10 second putton press.  Shutting down. -- {}".format(bcolors.WARNING, bcolors.ENDC))
			# 	os.system("halt")

		if self.__config['debug']: print("{}Recording Finished.{}".format(bcolors.OKBLUE, bcolors.ENDC))

		self.button_pressed = False

		time.sleep(.5)  # more time for the button to settle down

	# def wait_for_trigger(self):
	# 	# we wait for the button to be pressed
	# 	GPIO.wait_for_edge(self.__pconfig['button'], GPIO.FALLING)

	def should_record(self):
		return self.button_pressed

	def cleanup(self):
		GPIO.remove_event_detect(self.__pconfig['button'])

		GPIO.output(self.__pconfig['rec_light'], GPIO.LOW)
		GPIO.output(self.__pconfig['plb_light'], GPIO.LOW)