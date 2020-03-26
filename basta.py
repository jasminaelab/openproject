#!/usr/bin/python
#importovanje potrebnih biblioteka
from subprocess import call
import time 
import urllib 
import RPi.GPIO as GPIO
#postavljanje pinova 
GPIO.setmode(GPIO.BCM) 
GPIO.cleanup() 
GPIO.setwarnings(True) 
GPIO.setup(17,GPIO.IN) #senzor za vlaznost zemljista
GPIO.setup(27,GPIO.OUT)  #zelena LED dioda
GPIO.setup(22,GPIO.OUT)  #crvena LED dioda
GPIO.setup (23, GPIO.OUT) #trigger
GPIO.setup (18,GPIO.IN) #echo
GPIO.output(22,GPIO.LOW) #crvena LED dioda OFF
GPIO.output(27,GPIO.HIGH) #zelena LED dioda ON
status = None 
while True:
	print "Provera kanistera"
	GPIO.output (23,GPIO.LOW) 
	GPIO.output(23,GPIO.HIGH) #slanje kratkog signala preko triggera
	time.sleep(0.00001)
	GPIO.output(23,GPIO.LOW) 
	while GPIO.input (18) == 0: #racunanje proteklog vremena 
		pass
	start = time.time()
	while GPIO.input (18) == 1:
		pass
	stop = time.time()
	voda = round(((30-((stop-start) * 17000))/20)*100,2) #formula za racunanje % kolicine vode u kanisteru
	print voda

	url= 'http://www.halotaxi.rs/test/testupisivodu.php?voda={0}'.format(voda) #slanje nivoa vode
	urllib.urlopen(url)

	print "Ocitavam vlaznost zemljista" 
	citac = GPIO.input(17) #citanje vlaznosti zemljista
	print citac 
	if citac==0: 
		GPIO.output(22,GPIO.LOW) 
		GPIO.output(27,GPIO.HIGH)  
		if status == 1: 
			print "Poslato je da je vlaznost zemljista normalna!!"
		else: 
			print "Vlaznost zemljista je normalna!" 
			urllib.urlopen('http://www.halotaxi.rs/test/testupisibastu.php?vlaznost=0') #obavestenje o vlaznosti
			status=1
	else: 
		GPIO.output(22,GPIO.HIGH) 
		GPIO.output(27,GPIO.LOW)
		call(["python", "relejon.py"]) #pokretanje eksternog python fajla koji ukljucuje relej tj. pumpu za vodu
		print "Pokrecem pumpu..."
		print "Zalivam cvece"
		time.sleep(10)
		call(["python", "relejoff.py"]) #pokretanje eksternog python fajla koji iskljucuje relej tj. pumpu za vodu
		print "Cekam da zemljiste upije vodu"
		time.sleep(30) #cekanje od 30 sekundi da zemlja upije vodu
		call(["python", "relejon.py"])
		print "Pokrecem pumpu..."
		print "Zalivam cvece"
		time.sleep(10)
		call(["python", "relejoff.py"])
		print "Zalivanje zavrseno"
		if status==0: 
			print "Poslato je da treba zalivanje!"
		else: 
			print "PAZNJA: Vlaznost zemljista ispod normale, potrebno zalivanje!!!"
			urllib.urlopen('http://www.halotaxi.rs/test/testupisibastu.php?vlaznost=1') #obavestenje o vlaznosti
			status=0 
	time.sleep(1)