from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime, timezone
from ai_engines import MarketIntelligenceEngine, VirtualCMO, CampaignExecutor
from ai_advanced import OptimizationEngine, IntelligentCRM, OmnichannelAssistant

# Este arquivo cont\u00e9m os endpoints das 7 camadas do ELION MARKET 360

def create_ai_router(db, get_current_user):
    router = APIRouter(prefix="/api/ai")
    
    # Initialize AI Engines
    market_intelligence = MarketIntelligenceEngine(db)
    virtual_cmo = VirtualCMO(db)
    campaign_executor = CampaignExecutor(db)
    optimization_engine = OptimizationEngine(db)
    intelligent_crm = IntelligentCRM(db)
    omnichannel_assistant = OmnichannelAssistant(db)
    
    @router.post("/market-intelligence")
    async def run_market_intelligence(user_id: str = Depends(get_current_user)):
        """CAMADA 2: Executa an\u00e1lise completa do neg\u00f3cio"""
        connections = await db.platform_connections.find({'user_id': user_id}, {'_id': 0}).to_list(100)
        data_collection = await db.platform_data.find({'user_id': user_id}, {'_id': 0}).to_list(100)
        
        connections_data = {'connections': connections, 'data': data_collection}
        analysis = await market_intelligence.analyze_business(user_id, connections_data)
        
        return {'status': 'success', 'analysis': analysis}
    
    @router.post("/create-strategy")
    async def create_marketing_strategy(user_id: str = Depends(get_current_user)):
        """CAMADA 3: Cria estrat\u00e9gia completa de marketing"""
        analysis = await db.business_intelligence.find_one({'user_id': user_id}, {'_id': 0}, sort=[('created_at', -1)])
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Execute an\u00e1lise de mercado primeiro")
        
        strategy = await virtual_cmo.create_strategy(user_id, analysis['analysis'])
        return {'status': 'success', 'strategy': strategy}
    
    @router.post("/create-campaigns")
    async def create_ai_campaigns(user_id: str = Depends(get_current_user)):
        """CAMADA 4: Cria campanhas prontas para aprova\u00e7\u00e3o"""
        strategy_doc = await db.marketing_strategies.find_one({'user_id': user_id}, {'_id': 0}, sort=[('created_at', -1)])
        
        if not strategy_doc:
            raise HTTPException(status_code=404, detail="Crie estrat\u00e9gia primeiro")
        
        campaigns = await campaign_executor.create_campaigns(user_id, strategy_doc['strategy'])
        return {'status': 'success', 'campaigns': campaigns, 'total': len(campaigns)}
    
    @router.get("/campaigns/pending")
    async def get_pending_campaigns(user_id: str = Depends(get_current_user)):
        """Lista campanhas aguardando aprova\u00e7\u00e3o"""
        campaigns = await db.ai_campaigns.find({'user_id': user_id, 'status': 'pending_approval'}, {'_id': 0}).to_list(100)
        return {'campaigns': campaigns}
    
    @router.post("/campaigns/{campaign_id}/approve")
    async def approve_campaign(campaign_id: str, user_id: str = Depends(get_current_user)):
        """Aprova campanha para execu\u00e7\u00e3o"""
        result = await db.ai_campaigns.update_one(
            {'user_id': user_id, 'campaign.id': campaign_id},
            {'$set': {'status': 'approved', 'approved_at': datetime.now(timezone.utc).isoformat()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Campanha n\u00e3o encontrada")
        
        return {'status': 'approved', 'campaign_id': campaign_id}
    
    @router.post("/optimize")
    async def run_optimization(user_id: str = Depends(get_current_user)):
        """CAMADA 5: Executa otimiza\u00e7\u00e3o autom\u00e1tica"""
        metrics = await db.metrics.find({'user_id': user_id}, {'_id': 0}).sort('recorded_at', -1).limit(30).to_list(30)
        optimization = await optimization_engine.analyze_and_optimize(user_id, {'metrics': metrics})
        return {'status': 'success', 'optimization': optimization}
    
    return router

def create_crm_router(db, get_current_user):
    router = APIRouter(prefix="/api/crm")
    intelligent_crm = IntelligentCRM(db)
    
    @router.get("/leads")
    async def get_crm_leads(user_id: str = Depends(get_current_user)):
        """CAMADA 6: Lista leads no CRM"""
        leads = await db.crm_leads.find({'user_id': user_id}, {'_id': 0}).to_list(100)
        
        frios = [l for l in leads if l.get('temperatura') == 'frio']
        mornos = [l for l in leads if l.get('temperatura') == 'morno']
        quentes = [l for l in leads if l.get('temperatura') == 'quente']
        
        return {'total': len(leads), 'frios': frios, 'mornos': mornos, 'quentes': quentes}
    
    @router.post("/classify-lead")
    async def classify_lead(lead_data: Dict[str, Any], user_id: str = Depends(get_current_user)):
        """Classifica lead automaticamente"""
        lead_data['user_id'] = user_id
        classification = await intelligent_crm.classify_lead(lead_data)
        return {'status': 'success', 'classification': classification}
    
    return router

def create_omnichannel_router(db, get_current_user):
    router = APIRouter(prefix="/api/omnichannel")
    omnichannel_assistant = OmnichannelAssistant(db)
    
    @router.post("/message")
    async def handle_customer_message(data: Dict[str, Any], user_id: str = Depends(get_current_user)):
        """CAMADA 7: Processa mensagem de cliente"""
        channel = data.get('channel')
        customer_id = data.get('customer_id')
        message = data.get('message')
        
        context = await db.business_intelligence.find_one({'user_id': user_id}, {'_id': 0}, sort=[('created_at', -1)])
        
        response = await omnichannel_assistant.handle_message(
            channel, customer_id, message, 
            context.get('analysis', {}) if context else {}
        )
        
        return response
    
    @router.get("/conversations/{customer_id}")
    async def get_conversation_history(customer_id: str, user_id: str = Depends(get_current_user)):
        """Busca hist\u00f3rico de conversa com cliente"""
        conversations = await db.conversations.find({'customer_id': customer_id}, {'_id': 0}).sort('created_at', -1).to_list(50)
        return {'conversations': conversations}
    
    return router
