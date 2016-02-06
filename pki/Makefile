# Simple SSL CA makefile for generating certificates
# Gyorgy Demarcsek, 2016

SSL := $(shell which openssl)

default: certs

certs: cacert.pem servercert.pem cakey.pem serverkey.pem index.txt serial.txt chain.pem

cacert.pem:
	$(SSL) req -x509 -config ca.cnf -newkey rsa:4096 -sha256 -nodes -out cacert.pem -outform PEM

index.txt:
	touch index.txt

serial.txt:
	echo "01" > serial.txt


servercert.pem: index.txt serial.txt
	$(SSL) req -config service-endpoint.cnf -newkey rsa:2048 -sha256 -nodes -out servercert.csr -outform PEM
	$(SSL) ca -config ca.cnf -policy signing_policy -extensions signing_req -out servercert.pem -infiles servercert.csr

chain.pem: cacert.pem servercert.pem
	cat servercert.pem  cacert.pem > chain.pem

clean:
	rm -f *.pem
	rm -f serial.txt
	rm -f *.old
	rm -f index.txt
	rm -f *.csr
	rm -f *.attr


%.pki: certs
	cp chain.pem ../$*/pki/certs/$*.crt
	cp serverkey.pem ../$*/pki/certs/$*.key
	#cp chain.pem ../$*/pki/certs/private_pki_chain.crt
	cp cacert.pem ../$*/pki/certs/private_pki_ca.crt

%.pki-clean: %.pki
	rm ../$*/pki/certs/*.crt
	rm ../$*/pki/certs/*.key

.PHONY: clean
