from Crypto.PublicKey import RSA

# Generate a 2048-bit RSA key pair
key = RSA.generate(2048)

# Export the private key and save it to private.pem
private_key = key.export_key()
with open("private.pem", "wb") as f:
    f.write(private_key)    
    
# Export the public key and save it to public.pem
public_key = key.publickey().export_key()
with open("public.pem", "wb") as f:
    f.write(public_key)

print("RSA key pair generated. Check private.pem and public.pem in the project root.")