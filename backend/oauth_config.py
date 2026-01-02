from cryptography.fernet import Fernet
import os
import base64

# Encryption for tokens
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # Generate one for dev - MUST be set in production
    ENCRYPTION_KEY = base64.urlsafe_b64encode(os.urandom(32)).decode()

cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_token(token: str) -> str:
    """Encrypt sensitive tokens before storing"""
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt tokens when needed"""
    return cipher_suite.decrypt(encrypted_token.encode()).decode()

# OAuth Platform Configurations
OAUTH_PLATFORMS = {
    'google': {
        'name': 'Google',
        'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
        'auth_url': 'https://accounts.google.com/o/oauth2/v2/auth',
        'token_url': 'https://oauth2.googleapis.com/token',
        'user_info_url': 'https://www.googleapis.com/oauth2/v2/userinfo',
        'scopes': [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/adwords',
            'https://www.googleapis.com/auth/analytics.readonly'
        ]
    },
    'meta': {
        'name': 'Meta (Facebook/Instagram)',
        'client_id': os.environ.get('META_APP_ID', ''),
        'client_secret': os.environ.get('META_APP_SECRET', ''),
        'auth_url': 'https://www.facebook.com/v20.0/dialog/oauth',
        'token_url': 'https://graph.facebook.com/v20.0/oauth/access_token',
        'user_info_url': 'https://graph.facebook.com/v20.0/me',
        'scopes': [
            'public_profile',
            'email',
            'pages_read_engagement',
            'pages_manage_posts',
            'pages_show_list',
            'instagram_basic',
            'instagram_content_publish',
            'ads_read',
            'ads_management'
        ]
    },
    'linkedin': {
        'name': 'LinkedIn',
        'client_id': os.environ.get('LINKEDIN_CLIENT_ID', ''),
        'client_secret': os.environ.get('LINKEDIN_CLIENT_SECRET', ''),
        'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
        'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
        'user_info_url': 'https://api.linkedin.com/v2/userinfo',
        'scopes': [
            'openid',
            'profile',
            'email',
            'w_member_social',
            'r_ads',
            'rw_ads'
        ]
    },
    'tiktok': {
        'name': 'TikTok',
        'client_id': os.environ.get('TIKTOK_CLIENT_KEY', ''),
        'client_secret': os.environ.get('TIKTOK_CLIENT_SECRET', ''),
        'auth_url': 'https://www.tiktok.com/v2/auth/authorize/',
        'token_url': 'https://open.tiktokapis.com/v2/oauth/token/',
        'user_info_url': 'https://open.tiktokapis.com/v2/user/info/',
        'scopes': [
            'user.info.basic',
            'video.list',
            'video.publish',
            'user.insights'
        ]
    }
}