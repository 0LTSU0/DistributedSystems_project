import rsa

# Create key pair (copy public.pem manually to server)
pub_key, private_key = rsa.newkeys(1024)
with open("private.pem", "wb") as f:
    f.write(private_key.save_pkcs1("PEM"))
with open("public.pem", "wb") as f:
    f.write(pub_key.save_pkcs1("PEM"))