import sys
import json
import logging
import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from typing import List
from converter import convert_measurement_string
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Package Measurement Conversion API", version="1.0")

# Globals for history management, using the encrypted JSON file "history.json.enc"
HISTORY_FILENAME = "history.json.enc"
history_data = []  # In-memory history

def load_history():
    """
    Loads and decrypts the history from the encrypted JSON file into RAM.
    Uses private.pem to decrypt.
    """
    global history_data
    try:
        with open(HISTORY_FILENAME, "rb") as f:
            encrypted_data = f.read()
        with open("private.pem", "rb") as key_file:
            private_key = RSA.import_key(key_file.read())
        cipher = PKCS1_OAEP.new(private_key)
        decrypted = cipher.decrypt(encrypted_data)
        history_data = json.loads(decrypted.decode("utf-8"))
        logger.info("History loaded and decrypted successfully from history.json.enc")
    except FileNotFoundError:
        logger.warning("No encrypted history file found, starting with empty history.")
        history_data = []
    except Exception as e:
        logger.error(f"Error loading history: {e}")
        history_data = []

def save_history():
    """
    Encrypts and saves the in-memory history data to the encrypted JSON file.
    Uses public.pem for encryption.
    """
    try:
        json_data = json.dumps(history_data).encode("utf-8")
        with open("public.pem", "rb") as key_file:
            public_key = RSA.import_key(key_file.read())
        cipher = PKCS1_OAEP.new(public_key)
        encrypted_data = cipher.encrypt(json_data)
        with open(HISTORY_FILENAME, "wb") as f:
            f.write(encrypted_data)
        logger.info("History encrypted and saved successfully to history.json.enc")
    except Exception as e:
        logger.error(f"Error saving history: {e}")

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup: Loading history.")
    load_history()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown: Saving history.")
    save_history()

@app.get("/convert")
def convert_api(input_str: str = Query(..., alias="convert-measurements", description="The measurement input string to convert")):
    """
    GET endpoint to convert a measurement input string into a list of package sums.
    """
    logger.info(f"Received conversion request for input: {input_str}")
    result = convert_measurement_string(input_str)
    logger.debug(f"Conversion result: {result}")
    
    # Append request and response to history
    history_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "request": input_str,
        "response": result
    }
    history_data.append(history_entry)
    logger.info(f"History entry appended. Total history entries: {len(history_data)}")
    
    return {"package_measurements": result}

@app.get("/history")
def get_history():
    """
    Endpoint to retrieve conversion history.
    """
    logger.info("History retrieval requested.")
    return {"history": history_data}

@app.get("/decrypt_history")
def decrypt_history_endpoint():
    """
    Endpoint to decrypt the encrypted history file and store the decrypted JSON 
    in 'history_decrypted.json'. Also returns the decrypted history as part of the response.
    """
    try:
        with open(HISTORY_FILENAME, "rb") as f:
            encrypted_data = f.read()
        with open("private.pem", "rb") as key_file:
            private_key = RSA.import_key(key_file.read())
        cipher = PKCS1_OAEP.new(private_key)
        decrypted = cipher.decrypt(encrypted_data)
        data = json.loads(decrypted.decode("utf-8"))
        
        # Write decrypted history to file
        with open("history_decrypted.json", "w", encoding="utf-8") as out_file:
            json.dump(data, out_file, indent=4)
        logger.info("Decrypted history stored successfully in 'history_decrypted.json'")
        return {"message": "Decrypted history stored", "decrypted_history": data}
    except Exception as e:
        logger.error(f"Error decrypting history: {e}")
        raise HTTPException(status_code=500, detail="Error decrypting history")

if __name__ == "__main__":
    port = 8888
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.warning(f"Invalid port provided '{sys.argv[1]}'. Falling back to default port {port}.")
    logger.info(f"Starting application on port {port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)