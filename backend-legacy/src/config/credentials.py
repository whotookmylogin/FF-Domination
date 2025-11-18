import os
import json
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet

class CredentialManager:
    """
    Secure credential management service.
    Handles encryption, storage, and retrieval of sensitive authentication data.
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize credential manager.
        
        Args:
            encryption_key (str, optional): Encryption key for credential encryption.
                                           If not provided, will be loaded from environment.
        """
        self.encryption_key = encryption_key or os.getenv('CREDENTIAL_ENCRYPTION_KEY')
        if not self.encryption_key:
            raise ValueError("Encryption key must be provided or set in environment variables")
            
        self.cipher_suite = Fernet(self.encryption_key.encode())
        self.credentials_file = os.getenv('CREDENTIALS_FILE', 'credentials.json')
        
    def encrypt_credential(self, credential: str) -> str:
        """
        Encrypt a credential string.
        
        Args:
            credential (str): Credential to encrypt
            
        Returns:
            str: Encrypted credential
        """
        encrypted = self.cipher_suite.encrypt(credential.encode())
        return encrypted.decode()
    
    def decrypt_credential(self, encrypted_credential: str) -> str:
        """
        Decrypt a credential string.
        
        Args:
            encrypted_credential (str): Encrypted credential to decrypt
            
        Returns:
            str: Decrypted credential
        """
        decrypted = self.cipher_suite.decrypt(encrypted_credential.encode())
        return decrypted.decode()
    
    def store_credential(self, platform: str, credential_type: str, credential: str) -> bool:
        """
        Store a credential for a specific platform.
        
        Args:
            platform (str): Platform name (e.g., 'espn', 'sleeper')
            credential_type (str): Type of credential (e.g., 'cookie', 'token')
            credential (str): Credential value to store
            
        Returns:
            bool: Success status
        """
        try:
            # Load existing credentials
            credentials = self._load_credentials()
            
            # Encrypt the credential
            encrypted_credential = self.encrypt_credential(credential)
            
            # Store credential
            if platform not in credentials:
                credentials[platform] = {}
                
            credentials[platform][credential_type] = encrypted_credential
            
            # Save credentials
            self._save_credentials(credentials)
            
            logging.info(f"Successfully stored credential for {platform}")
            return True
        except Exception as e:
            logging.error(f"Failed to store credential for {platform}: {str(e)}")
            return False
    
    def retrieve_credential(self, platform: str, credential_type: str) -> Optional[str]:
        """
        Retrieve a credential for a specific platform.
        
        Args:
            platform (str): Platform name (e.g., 'espn', 'sleeper')
            credential_type (str): Type of credential (e.g., 'cookie', 'token')
            
        Returns:
            str: Decrypted credential value, or None if not found
        """
        try:
            # Load existing credentials
            credentials = self._load_credentials()
            
            # Retrieve encrypted credential
            encrypted_credential = credentials.get(platform, {}).get(credential_type)
            if not encrypted_credential:
                logging.warning(f"Credential not found for {platform}:{credential_type}")
                return None
                
            # Decrypt and return
            decrypted_credential = self.decrypt_credential(encrypted_credential)
            return decrypted_credential
        except Exception as e:
            logging.error(f"Failed to retrieve credential for {platform}:{credential_type}: {str(e)}")
            return None
    
    def _load_credentials(self) -> Dict[str, Dict[str, str]]:
        """
        Load credentials from file.
        
        Returns:
            dict: Credentials dictionary
        """
        if not os.path.exists(self.credentials_file):
            return {}
            
        try:
            with open(self.credentials_file, 'r') as f:
                credentials = json.load(f)
            return credentials
        except Exception as e:
            logging.error(f"Failed to load credentials from {self.credentials_file}: {str(e)}")
            return {}
    
    def _save_credentials(self, credentials: Dict[str, Dict[str, str]]) -> None:
        """
        Save credentials to file.
        
        Args:
            credentials (dict): Credentials dictionary to save
        """
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f, indent=2)
    
    @staticmethod
    def generate_encryption_key() -> str:
        """
        Generate a new encryption key for credential storage.
        
        Returns:
            str: New encryption key
        """
        key = Fernet.generate_key()
        return key.decode()

# Example usage:
# # Generate encryption key (should be done once and stored securely)
# encryption_key = CredentialManager.generate_encryption_key()
# print(f"Encryption key: {encryption_key}")
# 
# # Store in environment variable
# # export CREDENTIAL_ENCRYPTION_KEY="your_generated_key_here"
# 
# # Initialize credential manager
# cred_manager = CredentialManager()
# 
# # Store credentials
# cred_manager.store_credential("espn", "swid", "your_espn_swid_cookie")
# cred_manager.store_credential("espn", "espn_s2", "your_espn_s2_cookie")
# cred_manager.store_credential("sleeper", "token", "your_sleeper_api_token")
# 
# # Retrieve credentials
# espn_swid = cred_manager.retrieve_credential("espn", "swid")
# sleeper_token = cred_manager.retrieve_credential("sleeper", "token")
