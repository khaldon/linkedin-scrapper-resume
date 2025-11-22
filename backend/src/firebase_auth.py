"""
Firebase Authentication with OAuth2 (Google & LinkedIn)
Cost-effective solution using Firebase free tier + SQLite
"""

from typing import Optional, Dict
import os
import json
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class FirebaseAuthManager:
    """Manage Firebase Authentication for OAuth2"""

    def __init__(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            firebase_admin.get_app()
        except ValueError:
            # Initialize Firebase

            # 1. Try JSON content from environment variable (Best for Hugging Face Spaces)
            service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

            # 2. Try file path from environment variable (Good for local dev)
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

            if service_account_json:
                try:
                    cred_dict = json.loads(service_account_json)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    logger.info(
                        "✅ Firebase initialized with service account JSON from env"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON: {e}"
                    )
                    # Fallback to default
                    try:
                        firebase_admin.initialize_app()
                    except Exception:
                        pass
            elif cred_path and os.path.exists(cred_path):
                try:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    logger.info(
                        f"✅ Firebase initialized with service account file: {cred_path}"
                    )
                except Exception as e:
                    logger.error(f"❌ Failed to load credentials from {cred_path}: {e}")
            else:
                # 3. Use default credentials (works on GCP)
                try:
                    firebase_admin.initialize_app()
                    logger.info(
                        "✅ Firebase initialized with Application Default Credentials"
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Firebase not initialized: {e}")
                    logger.warning(
                        "Auth verification may fail. Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_CREDENTIALS_PATH."
                    )

    def verify_id_token(self, id_token: str) -> Optional[Dict]:
        """
        Verify Firebase ID token from OAuth2 login

        Args:
            id_token: Firebase ID token from client

        Returns:
            Decoded token with user info, or None if invalid
        """
        try:
            decoded_token = firebase_auth.verify_id_token(id_token)
            return {
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
                "provider": decoded_token.get("firebase", {}).get("sign_in_provider"),
            }
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def get_user(self, uid: str) -> Optional[Dict]:
        """Get user information from Firebase"""
        try:
            user = firebase_auth.get_user(uid)
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "photo_url": user.photo_url,
                "email_verified": user.email_verified,
                "disabled": user.disabled,
            }
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None

    def create_custom_token(self, uid: str, additional_claims: Dict = None) -> str:
        """Create a custom token for a user"""
        try:
            return firebase_auth.create_custom_token(uid, additional_claims)
        except Exception as e:
            logger.error(f"Failed to create custom token: {e}")
            raise HTTPException(status_code=500, detail="Failed to create token")

    def revoke_refresh_tokens(self, uid: str):
        """Revoke all refresh tokens for a user (logout)"""
        try:
            firebase_auth.revoke_refresh_tokens(uid)
        except Exception as e:
            logger.error(f"Failed to revoke tokens: {e}")


# Global instance
firebase_auth_manager = FirebaseAuthManager()


def verify_firebase_token(id_token: str) -> Dict:
    """
    Convenience function to verify Firebase token

    Args:
        id_token: Firebase ID token

    Returns:
        User information

    Raises:
        HTTPException if token is invalid
    """
    user_info = firebase_auth_manager.verify_id_token(id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return user_info
