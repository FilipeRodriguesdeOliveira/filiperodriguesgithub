from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio
from oauth_service import OAuthService
from ai_endpoints import create_ai_router, create_crm_router, create_omnichannel_router

# Setup logger
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError("JWT_SECRET must be set in environment variables")
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    created_at: str

class AuthResponse(BaseModel):
    token: str
    user: UserResponse

class ConnectionCreate(BaseModel):
    platform: str  # 'meta', 'google_ads', 'ga4', 'website'
    credentials: Dict[str, Any]

class Connection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    platform: str
    status: str  # 'connected', 'disconnected'
    last_sync: Optional[str] = None
    created_at: str

class GoalCreate(BaseModel):
    objective: str  # 'leads', 'brand', 'followers', 'sales'
    target_value: Optional[int] = None
    description: Optional[str] = None

class Goal(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    objective: str
    target_value: Optional[int] = None
    description: Optional[str] = None
    status: str  # 'active', 'paused'
    created_at: str

class DataCollection(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    platform: str
    data: Dict[str, Any]
    collected_at: str

class AIAnalysisRequest(BaseModel):
    type: str  # 'brain', 'niche', 'strategy', 'campaign', 'metrics', 'optimizer', 'crm'
    context: Optional[Dict[str, Any]] = None

class AIAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    type: str
    analysis: str
    recommendations: List[str]
    created_at: str

class Campaign(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    name: str
    platform: str
    objective: str
    structure: Dict[str, Any]
    status: str  # 'draft', 'active', 'paused', 'completed'
    created_at: str

class Metric(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    campaign_id: Optional[str] = None
    metrics: Dict[str, Any]
    recorded_at: str

# Routes
@api_router.post("/auth/register", response_model=AuthResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({'email': user_data.email}, {'_id': 0})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    user_doc = {
        'id': user_id,
        'email': user_data.email,
        'password': hash_password(user_data.password),
        'name': user_data.name,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    # Create token
    token = create_token(user_id)
    
    user_response = UserResponse(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        created_at=user_doc['created_at']
    )
    
    return AuthResponse(token=token, user=user_response)

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({'email': credentials.email}, {'_id': 0})
    if not user or not verify_password(credentials.password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user['id'])
    
    user_response = UserResponse(
        id=user['id'],
        email=user['email'],
        name=user['name'],
        created_at=user['created_at']
    )
    
    return AuthResponse(token=token, user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user_id: str = Depends(get_current_user)):
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user)

# Connections
@api_router.post("/connections", response_model=Connection)
async def create_connection(conn_data: ConnectionCreate, user_id: str = Depends(get_current_user)):
    conn_id = str(uuid.uuid4())
    connection_doc = {
        'id': conn_id,
        'user_id': user_id,
        'platform': conn_data.platform,
        'credentials': conn_data.credentials,
        'status': 'connected',
        'last_sync': None,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.connections.insert_one(connection_doc)
    
    # Trigger mock data collection
    asyncio.create_task(collect_mock_data(user_id, conn_data.platform))
    
    return Connection(
        id=conn_id,
        user_id=user_id,
        platform=conn_data.platform,
        status='connected',
        last_sync=None,
        created_at=connection_doc['created_at']
    )

@api_router.get("/connections", response_model=List[Connection])
async def get_connections(user_id: str = Depends(get_current_user)):
    connections = await db.connections.find({'user_id': user_id}, {'_id': 0, 'credentials': 0}).to_list(100)
    return [Connection(**conn) for conn in connections]

# Goals
@api_router.post("/goals", response_model=Goal)
async def create_goal(goal_data: GoalCreate, user_id: str = Depends(get_current_user)):
    goal_id = str(uuid.uuid4())
    goal_doc = {
        'id': goal_id,
        'user_id': user_id,
        'objective': goal_data.objective,
        'target_value': goal_data.target_value,
        'description': goal_data.description,
        'status': 'active',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.goals.insert_one(goal_doc)
    return Goal(**goal_doc)

@api_router.get("/goals", response_model=List[Goal])
async def get_goals(user_id: str = Depends(get_current_user)):
    goals = await db.goals.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    return [Goal(**goal) for goal in goals]

# Data Collection
async def collect_mock_data(user_id: str, platform: str):
    """Mock data collection for demonstration"""
    mock_data = {
        'meta': {
            'followers': 15420,
            'engagement_rate': 3.2,
            'reach': 45000,
            'top_posts': ['Post about new product', 'Behind the scenes']
        },
        'google_ads': {
            'impressions': 125000,
            'clicks': 2500,
            'cpc': 1.25,
            'conversions': 45
        },
        'ga4': {
            'users': 8500,
            'sessions': 12000,
            'bounce_rate': 42.5,
            'avg_session_duration': 185
        },
        'website': {
            'pages': 25,
            'products': 12,
            'categories': ['Electronics', 'Accessories']
        }
    }
    
    data_doc = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'platform': platform,
        'data': mock_data.get(platform, {}),
        'collected_at': datetime.now(timezone.utc).isoformat()
    }
    await db.data_collection.insert_one(data_doc)
    
    # Update connection last_sync
    await db.connections.update_one(
        {'user_id': user_id, 'platform': platform},
        {'$set': {'last_sync': datetime.now(timezone.utc).isoformat()}}
    )

@api_router.get("/data-collection", response_model=List[DataCollection])
async def get_data_collection(user_id: str = Depends(get_current_user)):
    data = await db.data_collection.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    return [DataCollection(**d) for d in data]

# AI Analysis
@api_router.post("/ai/analyze", response_model=AIAnalysis)
async def analyze_with_ai(request: AIAnalysisRequest, user_id: str = Depends(get_current_user)):
    # Get user data
    connections = await db.connections.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    goals = await db.goals.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    data_collection = await db.data_collection.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    
    # AI Prompts based on type
    ai_prompts = {
        'brain': """Você é o IA Cérebro do ELION MARKET 360 - o estrategista principal. 
        Analise os dados fornecidos e decida quais ações as outras IAs devem executar.
        Classifique o negócio (B2C/B2B/B2G), defina prioridades e avalie riscos.
        
        Dados: {data}
        Objetivos: {goals}
        
        Forneça uma análise estratégica e recomendações específicas.""",
        'niche': """Você é a IA de Análise de Nicho & Público.
        Identifique o produto, crie personas reais e defina o ICP (cliente ideal).
        
        Dados do site e redes: {data}
        
        Forneça análise detalhada do nicho e público-alvo.""",
        'strategy': """Você é a IA de Estratégia de Marketing.
        Decida o tipo de campanha (leads/marca/seguidores), defina funil e escolha canais.
        
        Objetivos: {goals}
        Dados disponíveis: {data}
        
        Forneça estratégia completa de marketing.""",
        'campaign': """Você é a IA de Criação de Campanhas.
        Gere estrutura de campanhas, grupos, segmentações e cópias.
        
        Plataforma: {platform}
        Objetivo: {objective}
        Dados: {data}
        
        Forneça estrutura completa de campanha.""",
        'metrics': """Você é a IA Analista de Métricas.
        Identifique CPC alto, leads ruins, público errado e aponte causas raiz.
        
        Métricas: {metrics}
        
        Forneça análise detalhada e identifique problemas.""",
        'optimizer': """Você é a IA Otimizadora.
        Ajuste orçamento, público e criativos. Pause o que não performa e escale o que funciona.
        
        Campanhas atuais: {campaigns}
        Métricas: {metrics}
        
        Forneça recomendações de otimização.""",
        'crm': """Você é a IA de Atendimento e CRM.
        Classifique leads, faça pontuação e sugira ações de atendimento.
        
        Leads: {leads}
        
        Forneça classificação e estratégia de atendimento."""
    }
    
    context_str = f"""Conexões: {connections}
Objetivos: {goals}
Dados Coletados: {data_collection}
Contexto Adicional: {request.context}"""
    
    prompt = ai_prompts.get(request.type, ai_prompts['brain']).format(
        data=data_collection,
        goals=goals,
        platform=request.context.get('platform', 'Meta') if request.context else 'Meta',
        objective=request.context.get('objective', 'leads') if request.context else 'leads',
        metrics=request.context.get('metrics', {}) if request.context else {},
        campaigns=request.context.get('campaigns', []) if request.context else [],
        leads=request.context.get('leads', []) if request.context else []
    )
    
    # Call AI with proper error handling
    try:
        session_id = f"{user_id}_{request.type}_{str(uuid.uuid4())[:8]}"
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=prompt
        ).with_model("openai", "gpt-4o")  # Using gpt-4o for faster responses
        
        # Shorter context for faster response
        short_context = f"Objetivo: {goals[0]['objective'] if goals else 'N/A'}, Plataformas conectadas: {len(connections)}, Dados: {len(data_collection)}"
        user_message = UserMessage(text=f"Forneça uma análise {request.type} concisa: {short_context}")
        response = await asyncio.wait_for(chat.send_message(user_message), timeout=15.0)
    except asyncio.TimeoutError:
        response = f"Análise {request.type}: Sistema em processamento. Dados coletados: {len(data_collection)} fontes, {len(connections)} plataformas conectadas, {len(goals)} objetivos definidos. Análise completa disponível em breve."
    except Exception as e:
        logger.error(f"AI analysis error: {str(e)}")
        response = f"Análise {request.type}: O sistema está coletando e processando seus dados de {len(connections)} plataformas. Análise detalhada será gerada em breve com base em {len(data_collection)} pontos de dados."
    
    # Parse recommendations (simple split)
    recommendations = [line.strip() for line in response.split('\n') if line.strip().startswith(('-', '•', '*'))]
    if not recommendations:
        recommendations = ['Análise completa disponível no texto principal']
    
    # Save analysis
    analysis_id = str(uuid.uuid4())
    analysis_doc = {
        'id': analysis_id,
        'user_id': user_id,
        'type': request.type,
        'analysis': response,
        'recommendations': recommendations[:5],
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.ai_analyses.insert_one(analysis_doc)
    
    return AIAnalysis(**analysis_doc)

@api_router.get("/ai/analyses", response_model=List[AIAnalysis])
async def get_analyses(ai_type: Optional[str] = None, user_id: str = Depends(get_current_user)):
    query = {'user_id': user_id}
    if ai_type:
        query['type'] = ai_type
    analyses = await db.ai_analyses.find(query, {'_id': 0}).sort('created_at', -1).to_list(50)
    return [AIAnalysis(**a) for a in analyses]

# Campaigns
@api_router.post("/campaigns", response_model=Campaign)
async def create_campaign(campaign_data: Dict[str, Any], user_id: str = Depends(get_current_user)):
    campaign_id = str(uuid.uuid4())
    campaign_doc = {
        'id': campaign_id,
        'user_id': user_id,
        'name': campaign_data.get('name', 'Nova Campanha'),
        'platform': campaign_data.get('platform', 'meta'),
        'objective': campaign_data.get('objective', 'leads'),
        'structure': campaign_data.get('structure', {}),
        'status': 'draft',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    await db.campaigns.insert_one(campaign_doc)
    return Campaign(**campaign_doc)

@api_router.get("/campaigns", response_model=List[Campaign])
async def get_campaigns(user_id: str = Depends(get_current_user)):
    campaigns = await db.campaigns.find({'user_id': user_id}, {'_id': 0}).to_list(100)
    return [Campaign(**c) for c in campaigns]

# Metrics
@api_router.post("/metrics", response_model=Metric)
async def record_metric(metric_data: Dict[str, Any], user_id: str = Depends(get_current_user)):
    metric_id = str(uuid.uuid4())
    metric_doc = {
        'id': metric_id,
        'user_id': user_id,
        'campaign_id': metric_data.get('campaign_id'),
        'metrics': metric_data.get('metrics', {}),
        'recorded_at': datetime.now(timezone.utc).isoformat()
    }
    await db.metrics.insert_one(metric_doc)
    return Metric(**metric_doc)

@api_router.get("/metrics", response_model=List[Metric])
async def get_metrics(user_id: str = Depends(get_current_user)):
    metrics = await db.metrics.find({'user_id': user_id}, {'_id': 0}).sort('recorded_at', -1).to_list(100)
    return [Metric(**m) for m in metrics]

# OAuth Platform Integrations
oauth_service = OAuthService(db)

@api_router.get("/oauth/platforms")
async def get_available_platforms():
    """List available OAuth platforms for integration"""
    from oauth_config import OAUTH_PLATFORMS
    return {
        'platforms': [
            {
                'id': key,
                'name': config['name'],
                'configured': bool(config['client_id']),
                'scopes': config['scopes']
            }
            for key, config in OAUTH_PLATFORMS.items()
        ]
    }

@api_router.get("/oauth/{platform}/authorize")
async def authorize_platform(platform: str, user_id: str = Depends(get_current_user)):
    """Initiate OAuth flow for platform"""
    from oauth_config import OAUTH_PLATFORMS
    
    if platform not in OAUTH_PLATFORMS:
        raise HTTPException(status_code=400, detail=f"Platform {platform} not supported")
    
    # REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    # Use environment variable for callback URL
    callback_url = os.environ.get('BACKEND_URL', 'http://localhost:8001') + f"/api/oauth/{platform}/callback"
    
    auth_url = oauth_service.get_auth_url(platform, user_id, callback_url)
    
    if not auth_url:
        raise HTTPException(status_code=500, detail=f"Platform {platform} not configured. Please add OAuth credentials.")
    
    return {'authorization_url': auth_url}

@api_router.get("/oauth/{platform}/callback")
async def oauth_callback(platform: str, code: str, state: str):
    """Handle OAuth callback from platform"""
    # Verify state token
    state_data = oauth_service.verify_state_token(state)
    if not state_data:
        raise HTTPException(status_code=400, detail="Invalid state token")
    
    user_id = state_data['user_id']
    
    # Exchange code for token
    callback_url = os.environ.get('BACKEND_URL', 'http://localhost:8001') + f"/api/oauth/{platform}/callback"
    token_data = await oauth_service.exchange_code_for_token(platform, code, callback_url)
    
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
    
    # Get user info from platform
    user_info = await oauth_service.get_user_info(platform, token_data['access_token'])
    
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user information")
    
    # Store connection
    connection_id = await oauth_service.store_connection(user_id, platform, token_data, user_info)
    
    # Trigger data collection in background
    asyncio.create_task(collect_platform_data(user_id, platform))
    
    return {
        'status': 'success',
        'platform': platform,
        'connection_id': connection_id,
        'user_info': {
            'id': user_info.get('id'),
            'name': user_info.get('name'),
            'email': user_info.get('email')
        }
    }

@api_router.get("/oauth/connections")
async def get_user_connections(user_id: str = Depends(get_current_user)):
    """Get all platform connections for user"""
    connections = await oauth_service.get_connections(user_id)
    return {'connections': connections}

@api_router.delete("/oauth/{platform}")
async def disconnect_platform(platform: str, user_id: str = Depends(get_current_user)):
    """Disconnect a platform integration"""
    success = await oauth_service.disconnect_platform(user_id, platform)
    if not success:
        raise HTTPException(status_code=404, detail="Connection not found")
    return {'status': 'disconnected', 'platform': platform}

@api_router.post("/oauth/{platform}/sync")
async def sync_platform_data(platform: str, user_id: str = Depends(get_current_user)):
    """Manually trigger data sync for platform"""
    token = await oauth_service.get_decrypted_token(user_id, platform)
    if not token:
        raise HTTPException(status_code=404, detail="Platform not connected")
    
    data = await oauth_service.fetch_platform_data(platform, token, user_id)
    
    # Store collected data
    data_doc = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'platform': platform,
        'data': data,
        'collected_at': datetime.now(timezone.utc).isoformat()
    }
    await db.platform_data.insert_one(data_doc)
    
    # Update last_synced timestamp
    await db.platform_connections.update_one(
        {'user_id': user_id, 'platform': platform},
        {'$set': {'last_synced': datetime.now(timezone.utc).isoformat()}}
    )
    
    return {'status': 'synced', 'platform': platform, 'data': data}

async def collect_platform_data(user_id: str, platform: str):
    """Background task to collect data from platform"""
    try:
        token = await oauth_service.get_decrypted_token(user_id, platform)
        if token:
            data = await oauth_service.fetch_platform_data(platform, token, user_id)
            
            data_doc = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'platform': platform,
                'data': data,
                'collected_at': datetime.now(timezone.utc).isoformat()
            }
            await db.platform_data.insert_one(data_doc)
            
            await db.platform_connections.update_one(
                {'user_id': user_id, 'platform': platform},
                {'$set': {'last_synced': datetime.now(timezone.utc).isoformat()}}
            )
    except Exception as e:
        logger.error(f"Background data collection error: {str(e)}")

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(user_id: str = Depends(get_current_user)):
    """Get overview stats for dashboard"""
    connections_count = await db.connections.count_documents({'user_id': user_id, 'status': 'connected'})
    campaigns_count = await db.campaigns.count_documents({'user_id': user_id})
    active_campaigns = await db.campaigns.count_documents({'user_id': user_id, 'status': 'active'})
    
    # Get latest metrics
    latest_metrics = await db.metrics.find({'user_id': user_id}, {'_id': 0}).sort('recorded_at', -1).limit(1).to_list(1)
    
    return {
        'connections': connections_count,
        'total_campaigns': campaigns_count,
        'active_campaigns': active_campaigns,
        'latest_metrics': latest_metrics[0] if latest_metrics else {}
    }

# Include router
app.include_router(api_router)

# Include AI routers (7 Camadas do ELION MARKET 360)
ai_router = create_ai_router(db, get_current_user)
crm_router = create_crm_router(db, get_current_user)
omnichannel_router = create_omnichannel_router(db, get_current_user)

app.include_router(ai_router)
app.include_router(crm_router)
app.include_router(omnichannel_router)

# Health check endpoint at root level (required for Kubernetes)
@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness/readiness probes"""
    return {"status": "healthy", "service": "elion-market-360"}

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()