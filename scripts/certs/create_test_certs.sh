#!/bin/bash

# source: https://gist.github.com/cecilemuller/9492b848eb8fe46d462abeb26656c4f8

# create CA
openssl req -x509 -nodes -new -sha256 -days 1024 -newkey rsa:2048 -keyout localhost.ca.key -out localhost.ca.pem -subj "/C=US/CN=Example-Root-CA"

# create SANs for localhost
echo "authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names
[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1" > domains.ext

# create server cert
openssl req -new -nodes -newkey rsa:2048 -keyout localhost.key -out localhost.csr -subj "/C=US/ST=YourState/L=YourCity/O=Example-Certificates/CN=localhost.local"
openssl x509 -req -sha256 -days 1024 -in localhost.csr -CA localhost.ca.pem -CAkey localhost.ca.key -CAcreateserial -extfile domains.ext -out localhost.crt

rm -f domains.ext localhost.csr localhost.ca.srl localhost.ca.key
echo "generated localhost.ca.pem, localhost.crt, localhost.key"
