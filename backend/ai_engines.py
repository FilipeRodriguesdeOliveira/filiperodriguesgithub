from typing import Dict, Any, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

class MarketIntelligenceEngine:
    """CAMADA 2: Motor de Inteligência de Mercado (IA #1)
    
    Entende o negócio melhor que o próprio dono.
    Analisa automaticamente e corrige percepções incorretas.
    """
    
    def __init__(self, db):
        self.db = db
        self.model = "gpt-4o"
    
    async def analyze_business(self, user_id: str, connections_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise completa do negócio baseada em dados reais"""
        
        system_prompt = """Você é o Motor de Inteligência de Mercado do ELION MARKET 360.
        
Sua função: ENTENDER O NEGÓCIO MELHOR QUE O PRÓPRIO DONO.
        
Você analisa dados de múltiplas fontes e identifica:
        1. Nicho REAL (não o que o usuário acha que é)
        2. Público comprador (comportamento real, não suposição)
        3. Proposta de valor verdadeira
        4. Produtos principais e secundários
        5. Estágio do negócio (inicial/escala/maturidade)
        
IMPORTANTE:
        - Seja direto e honesto
        - Corrija percepções erradas
        - Use dados, não achismos
        - Identifique oportunidades não exploradas
        
Retorne análise em formato JSON estruturado com:
        {
            "nicho_real": "descrição precisa",
            "publico_primario": {"demografia": "", "psicografia": "", "comportamento": ""},
            "publico_secundario": {...},
            "proposta_valor": "o que realmente vende",
            "produtos": {"principal": "", "secundarios": []},
            "estagio_negocio": "inicial|escala|maturidade",
            "dores_principais": [],
            "desejos_principais": [],
            "objecoes_comuns": [],
            "canais_ideais": [],
            "objetivo_correto": "leads|vendas|branding|autoridade",
            "insights_criticos": [],
            "correcoes_estrategicas": []
        }"""
        
        # Preparar contexto com dados reais
        context = self._prepare_context(connections_data)
        
        session_id = f"market_intel_{user_id}_{datetime.now(timezone.utc).timestamp()}"
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_prompt
        ).with_model("openai", self.model)
        
        try:
            message = UserMessage(text=f"""Analise este negócio:
            
            DADOS COLETADOS:
            {context}
            
            Forneça análise completa em JSON.""")
            
            response = await chat.send_message(message)
            
            # Parse JSON response
            import json
            analysis = json.loads(response)
            
            # Salvar análise
            await self._save_analysis(user_id, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Market intelligence analysis error: {str(e)}")
            return self._get_fallback_analysis()
    
    def _prepare_context(self, connections_data: Dict[str, Any]) -> str:
        """Prepara contexto estruturado dos dados coletados"""
        context_parts = []
        
        # Website data
        if 'website' in connections_data:
            context_parts.append(f"WEBSITE: {connections_data['website']}")
        
        # Social media data
        for platform in ['meta', 'instagram', 'linkedin', 'tiktok']:
            if platform in connections_data:
                data = connections_data[platform]
                context_parts.append(f"{platform.upper()}: {data}")
        
        # Ads data
        if 'google_ads' in connections_data or 'meta_ads' in connections_data:
            context_parts.append(f"CAMPANHAS: {connections_data.get('ads_data', {})}")
        
        return "\n\n".join(context_parts)
    
    async def _save_analysis(self, user_id: str, analysis: Dict[str, Any]):
        """Salva análise no banco"""
        doc = {
            'user_id': user_id,
            'type': 'market_intelligence',
            'analysis': analysis,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await self.db.business_intelligence.insert_one(doc)
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Análise de fallback em caso de erro"""
        return {
            'nicho_real': 'Análise em processamento',
            'status': 'pending',
            'message': 'Dados insuficientes. Conecte mais plataformas para análise completa.'
        }


class VirtualCMO:
    """CAMADA 3: CMO Virtual (IA #2 - Estratégia)
    
    A mente do ELION. Define estratégia completa de marketing.
    """
    
    def __init__(self, db):
        self.db = db
        self.model = "gpt-4o"
    
    async def create_strategy(self, user_id: str, market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Cria estratégia completa de marketing"""
        
        system_prompt = """Você é o CMO Virtual do ELION MARKET 360.
        
Função: Definir ESTRATÉGIA COMPLETA de marketing baseada em análise real.
        
Você decide:
        1. Tipos de campanhas (aquisição, branding, crescimento, remarketing)
        2. Orçamento por canal
        3. Prioridade curto vs longo prazo
        4. Estrutura de funil completo (topo, meio, fundo)
        
Retorne estratégia em JSON:
        {
            "estrategia_principal": "descrição",
            "campanhas": [
                {
                    "tipo": "aquisicao|branding|crescimento|remarketing",
                    "canal": "meta|google|linkedin|tiktok",
                    "objetivo": "específico",
                    "orcamento_sugerido": "valor",
                    "prioridade": "alta|media|baixa",
                    "prazo": "curto|medio|longo"
                }
            ],
            "funil": {
                "topo": {"objetivo": "", "metricas": [], "acoes": []},
                "meio": {"objetivo": "", "metricas": [], "acoes": []},
                "fundo": {"objetivo": "", "metricas": [], "acoes": []}
            },
            "kpis_principais": [],
            "timeline_execucao": "90 dias",
            "riscos_identificados": [],
            "oportunidades_rapidas": []
        }"""
        
        session_id = f"cmo_{user_id}_{datetime.now(timezone.utc).timestamp()}"
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_prompt
        ).with_model("openai", self.model)
        
        try:
            message = UserMessage(text=f"""Crie estratégia completa baseada nesta análise:
            
            {market_analysis}
            
            Retorne estratégia em JSON.""")
            
            response = await chat.send_message(message)
            
            import json
            strategy = json.loads(response)
            
            # Salvar estratégia
            await self._save_strategy(user_id, strategy)
            
            return strategy
            
        except Exception as e:
            logger.error(f"CMO strategy creation error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _save_strategy(self, user_id: str, strategy: Dict[str, Any]):
        """Salva estratégia no banco"""
        doc = {
            'user_id': user_id,
            'type': 'marketing_strategy',
            'strategy': strategy,
            'status': 'active',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await self.db.marketing_strategies.insert_one(doc)


class CampaignExecutor:
    """CAMADA 4: Executor de Campanhas (IA #3)
    
    Cria campanhas prontas para aprovação com 1 clique.
    """
    
    def __init__(self, db):
        self.db = db
        self.model = "gpt-4o"
    
    async def create_campaigns(self, user_id: str, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Cria campanhas completas prontas para execução"""
        
        system_prompt = """Você é o Executor de Campanhas do ELION MARKET 360.
        
Função: Criar CAMPANHAS PRONTAS para Meta Ads, Google Ads, LinkedIn e TikTok.
        
Para cada campanha, gere:
        1. Estrutura completa
        2. Criativos sugeridos (textos, conceitos visuais)
        3. Copies otimizados
        4. Segmentações precisas
        5. Configurações técnicas
        
Organize por:
        - Objetivo
        - Público
        - Canal
        - Estágio do funil
        
Retorne array de campanhas em JSON:
        [
            {
                "nome": "nome_descritivo",
                "plataforma": "meta|google|linkedin|tiktok",
                "objetivo": "conversoes|trafego|engajamento|visualizacoes",
                "estrutura": {
                    "conjuntos_anuncios": [],
                    "anuncios": []
                },
                "criativos": {
                    "textos": [],
                    "conceitos_visuais": [],
                    "ctas": []
                },
                "segmentacao": {
                    "idade": "range",
                    "genero": "todos|especifico",
                    "localizacao": [],
                    "interesses": [],
                    "comportamentos": []
                },
                "orcamento_diario": "valor",
                "duracao_dias": 30,
                "status": "draft",
                "aprovacao_necessaria": true
            }
        ]
        
        IMPORTANTE: NÃO publique sem aprovação. Apenas prepare."""        
        session_id = f"campaign_exec_{user_id}_{datetime.now(timezone.utc).timestamp()}"
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_prompt
        ).with_model("openai", self.model)
        
        try:
            message = UserMessage(text=f"""Crie campanhas baseadas nesta estratégia:
            
            {strategy}
            
            Retorne array de campanhas em JSON.""")
            
            response = await chat.send_message(message)
            
            import json
            campaigns = json.loads(response)
            
            # Salvar campanhas
            for campaign in campaigns:
                await self._save_campaign(user_id, campaign)
            
            return campaigns
            
        except Exception as e:
            logger.error(f"Campaign creation error: {str(e)}")
            return []
    
    async def _save_campaign(self, user_id: str, campaign: Dict[str, Any]):
        """Salva campanha no banco"""
        doc = {
            'user_id': user_id,
            'type': 'ai_generated_campaign',
            'campaign': campaign,
            'status': 'pending_approval',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await self.db.ai_campaigns.insert_one(doc)
