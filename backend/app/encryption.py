import os

from pymongo import MongoClient
from pymongo.encryption import Algorithm, ClientEncryption
import base64


def initEncryption(connStr, dbName, colName):
    print("Initializing encryption")

    # The MongoClient used to read/write application data.
    client = MongoClient(connStr)
    coll = client[dbName][colName]

    # The MongoDB namespace (db.collection) used to store
    # the encryption data keys.
    key_vault_db_name = dbName
    key_vault_coll_name = "__keyvault"

    doc_count = client[key_vault_db_name][key_vault_coll_name].count_documents({})

    if(doc_count > 0):
        print("ENCRYPTION KEYS ALREADY SET")
    else:
        print("CREATING ENCRYPTION KEYS")

        # This must be the same master key that was used to create
        # the encryption key.
        local_master_key = base64.b64decode(bytes(os.environ.get('MASTERENCKEYASBASE64').strip(), "utf-8"))
        kms_providers = {"local": {"key": local_master_key}}

        
        # Set up the key vault (key_vault_namespace) for this example.
        key_vault = client[key_vault_db_name][key_vault_coll_name]
        # Ensure that two data keys cannot share the same keyAltName.

        key_vault.create_index(
            "keyAltNames",
            unique=True,
            partialFilterExpression={"keyAltNames": {"$exists": True}},
        )

        client_encryption = ClientEncryption(
            kms_providers,
            key_vault_namespace,
            # The MongoClient to use for reading/writing to the key vault.
            # This can be the same MongoClient used by the main application.
            client,
            # The CodecOptions class used for encrypting and decrypting.
            # This should be the same CodecOptions instance you have configured
            # on MongoClient, Database, or Collection.
            coll.codec_options,
        )

        # Create a new data key for the encryptedField.
        data_key_id = client_encryption.create_data_key(
            "local", key_alt_names=["mainencryptionkey"]
        )

        print(data_key_id)

        # Cleanup resources.
        client.close()
        client_encryption.close()

def manualEncrypt(client, plainText):
    local_master_key = base64.b64decode(bytes(os.environ.get('MASTERENCKEYASBASE64').strip(), "utf-8"))
    kms_providers = {"local": {"key": local_master_key}}
    key_vault_namespace = "faas.__keyvault"
    key_vault_db_name, key_vault_coll_name = key_vault_namespace.split(".", 1)
    key_vault = client[key_vault_db_name][key_vault_coll_name]    
    coll = client["faas"]["subscriptions"]
    client_encryption = ClientEncryption(
        kms_providers,
        key_vault_namespace,
        client,
        coll.codec_options,
    )

    data_key_id = client["faas"]["__keyvault"].find_one({"keyAltNames":"mainencryptionkey"})["_id"]

    # Explicitly encrypt a field:
    encrypted_field = client_encryption.encrypt(
        plainText,
        Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic,
        key_id=data_key_id,
    )
    return encrypted_field

def manualDecrypt(client, encValue):
    local_master_key = base64.b64decode(bytes(os.environ.get('MASTERENCKEYASBASE64').strip(), "utf-8"))
    kms_providers = {"local": {"key": local_master_key}}
    key_vault_namespace = "faas.__keyvault"
    key_vault_db_name, key_vault_coll_name = key_vault_namespace.split(".", 1)
    key_vault = client[key_vault_db_name][key_vault_coll_name]
    coll = client["faas"]["subscriptions"]
    client_encryption = ClientEncryption(
        kms_providers,
        key_vault_namespace,
        client,
        coll.codec_options,
    )
    decrypted = client_encryption.decrypt(encValue)
    return decrypted