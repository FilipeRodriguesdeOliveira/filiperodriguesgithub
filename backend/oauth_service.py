from typing import Dict, Any, Optional, List
import httpx
import secrets
import hashlib
import base64
from datetime import datetime, timezone
from oauth_config import OAUTH_PLATFORMS, encrypt_token, decrypt_token
import logging

logger = logging.getLogger(__name__)

class OAuthService:
    """Service for handling OAuth 2.0 flows with multiple platforms"""
    
    def __init__(self, db):
        self.db = db
    
    def generate_state_token(self, user_id: str, platform: str) -> str:
        """Generate secure state token for CSRF protection"""
        state = secrets.token_urlsafe(32)
        state_data = f"{user_id}:{platform}:{state}"
        return base64.urlsafe_b64encode(state_data.encode()).decode()
    
    def verify_state_token(self, state: str) -> Optional[Dict[str, str]]:
        """Verify and decode state token"""
        try:
            decoded = base64.urlsafe_b64decode(state.encode()).decode()
            parts = decoded.split(':')
            if len(parts) == 3:
                return {
                    'user_id': parts[0],
                    'platform': parts[1],
                    'token': parts[2]
                }
        except Exception as e:
            logger.error(f"State token verification failed: {str(e)}")
        return None
    
    def get_auth_url(self, platform: str, user_id: str, redirect_uri: str) -> Optional[str]:
        """Generate OAuth authorization URL for specified platform"""
        config = OAUTH_PLATFORMS.get(platform)
        if not config or not config['client_id']:
            logger.error(f"Platform {platform} not configured")
            return None
        
        state = self.generate_state_token(user_id, platform)
        scope = ' '.join(config['scopes'])
        
        params = {
            'client_id': config['client_id'],
            'redirect_uri': redirect_uri,
            'scope': scope,
            'state': state,
            'response_type': 'code'
        }
        
        # Platform-specific additions
        if platform == 'google':
            params['access_type'] = 'offline'
            params['prompt'] = 'consent'
        elif platform == 'linkedin':
            params['response_type'] = 'code'
        
        param_str = '&'.join([f"{k}={httpx.URL(v).raw[2]}" for k, v in params.items()])
        auth_url = f"{config['auth_url']}?{param_str}"
        
        return auth_url
    
    async def exchange_code_for_token(self, platform: str, code: str, redirect_uri: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token"""
        config = OAUTH_PLATFORMS.get(platform)
        if not config:
            return None
        
        async with httpx.AsyncClient() as client:
            try:
                data = {
                    'client_id': config['client_id'],
                    'client_secret': config['client_secret'],
                    'code': code,
                    'redirect_uri': redirect_uri,
                    'grant_type': 'authorization_code'
                }
                
                response = await client.post(config['token_url'], data=data)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Token exchange failed: {response.text}")
                    return None
            except Exception as e:
                logger.error(f"Token exchange error: {str(e)}")
                return None
    
    async def get_user_info(self, platform: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Fetch user information from platform"""
        config = OAUTH_PLATFORMS.get(platform)
        if not config:
            return None
        
        async with httpx.AsyncClient() as client:
            try:
                headers = {'Authorization': f'Bearer {access_token}'}
                
                # Meta requires token as param instead of header
                if platform == 'meta':
                    url = f"{config['user_info_url']}?access_token={access_token}&fields=id,name,email"
                    response = await client.get(url)
                else:
                    response = await client.get(config['user_info_url'], headers=headers)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"User info fetch failed: {response.text}")
                    return None
            except Exception as e:
                logger.error(f"User info fetch error: {str(e)}")
                return None
    
    async def fetch_platform_data(self, platform: str, access_token: str, user_id: str) -> Dict[str, Any]:
        """Fetch marketing data from connected platform"""
        data = {
            'platform': platform,
            'collected_at': datetime.now(timezone.utc).isoformat(),
            'status': 'success'
        }
        
        try:
            if platform == 'meta':
                data['meta_data'] = await self._fetch_meta_data(access_token)
            elif platform == 'google':
                data['google_data'] = await self._fetch_google_data(access_token)
            elif platform == 'linkedin':
                data['linkedin_data'] = await self._fetch_linkedin_data(access_token)
            elif platform == 'tiktok':
                data['tiktok_data'] = await self._fetch_tiktok_data(access_token)
        except Exception as e:
            logger.error(f"Data fetch error for {platform}: {str(e)}")
            data['status'] = 'error'
            data['error'] = str(e)
        
        return data
    
    async def _fetch_meta_data(self, access_token: str) -> Dict[str, Any]:
        """Fetch data from Meta (Facebook/Instagram)"""
        async with httpx.AsyncClient() as client:
            # Fetch pages
            pages_url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={access_token}&fields=id,name,followers_count,fan_count"
            pages_resp = await client.get(pages_url)
            pages = pages_resp.json().get('data', []) if pages_resp.status_code == 200 else []
            
            # Fetch Instagram accounts
            instagram_accounts = []
            for page in pages:
                ig_url = f"https://graph.facebook.com/v20.0/{page['id']}?access_token={access_token}&fields=instagram_business_account"
                ig_resp = await client.get(ig_url)
                if ig_resp.status_code == 200:
                    ig_data = ig_resp.json()
                    if 'instagram_business_account' in ig_data:
                        ig_id = ig_data['instagram_business_account']['id']
                        ig_info_url = f"https://graph.facebook.com/v20.0/{ig_id}?access_token={access_token}&fields=id,username,name,followers_count,media_count"
                        ig_info_resp = await client.get(ig_info_url)
                        if ig_info_resp.status_code == 200:
                            instagram_accounts.append(ig_info_resp.json())
            
            return {
                'pages': pages,
                'instagram_accounts': instagram_accounts,
                'total_pages': len(pages),
                'total_instagram': len(instagram_accounts)
            }
    
    async def _fetch_google_data(self, access_token: str) -> Dict[str, Any]:
        """Fetch data from Google (Ads, Analytics)"""
        # Placeholder - implement Google API calls
        return {
            'ads_accounts': [],
            'analytics_properties': [],
            'status': 'configured'
        }
    
    async def _fetch_linkedin_data(self, access_token: str) -> Dict[str, Any]:
        """Fetch data from LinkedIn"""
        # Placeholder - implement LinkedIn API calls
        return {
            'organizations': [],
            'ad_accounts': [],
            'status': 'configured'
        }
    
    async def _fetch_tiktok_data(self, access_token: str) -> Dict[str, Any]:
        """Fetch data from TikTok"""
        # Placeholder - implement TikTok API calls
        return {
            'user_info': {},
            'videos': [],
            'status': 'configured'
        }
    
    async def store_connection(self, user_id: str, platform: str, token_data: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """Store encrypted connection tokens in database"""
        connection_doc = {
            'user_id': user_id,
            'platform': platform,
            'platform_user_id': user_info.get('id', ''),
            'platform_email': user_info.get('email', ''),
            'platform_name': user_info.get('name', ''),
            'access_token': encrypt_token(token_data['access_token']),
            'refresh_token': encrypt_token(token_data.get('refresh_token', '')) if token_data.get('refresh_token') else None,
            'token_type': token_data.get('token_type', 'Bearer'),
            'expires_in': token_data.get('expires_in'),
            'scopes': token_data.get('scope', '').split(' '),
            'status': 'active',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'last_synced': None
        }
        
        result = await self.db.platform_connections.insert_one(connection_doc)
        return str(result.inserted_id)
    
    async def get_connections(self, user_id: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user's platform connections"""
        query = {'user_id': user_id}
        if platform:
            query['platform'] = platform
        
        connections = await self.db.platform_connections.find(query, {'_id': 0, 'access_token': 0, 'refresh_token': 0}).to_list(100)
        return connections
    
    async def disconnect_platform(self, user_id: str, platform: str) -> bool:
        """Disconnect a platform integration"""
        result = await self.db.platform_connections.delete_one({
            'user_id': user_id,
            'platform': platform
        })
        return result.deleted_count > 0
    
    async def get_decrypted_token(self, user_id: str, platform: str) -> Optional[str]:
        """Get decrypted access token for API calls"""
        connection = await self.db.platform_connections.find_one({
            'user_id': user_id,
            'platform': platform,
            'status': 'active'
        })
        
        if connection and connection.get('access_token'):
            return decrypt_token(connection['access_token'])
        return None
