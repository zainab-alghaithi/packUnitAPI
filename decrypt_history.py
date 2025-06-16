import json
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def decrypt_history(filename="history.json.enc", private_key_path="private.pem"):
    """
    Decrypts the encrypted history file using the provided private key and returns the JSON data.
    """
    try:
        with open(filename, "rb") as f:
            encrypted_data = f.read()
        with open(private_key_path, "rb") as key_file:
            private_key = RSA.import_key(key_file.read())
        cipher = PKCS1_OAEP.new(private_key)
        decrypted = cipher.decrypt(encrypted_data)
        data = json.loads(decrypted.decode("utf-8"))
        return data
    except Exception as e:
        print(f"Error during decryption: {e}")
        return None

if __name__ == "__main__":
    data = decrypt_history()
    if data:
        print("Decrypted History:")
        print(json.dumps(data, indent=4))
    else:
        print("Failed to decrypt history.")