from typing import Dict, Any, List
from emergentintegrations.llm.chat import LlmChat, UserMessage
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

class OptimizationEngine:
    """CAMADA 5: IA de Otimização Contínua (IA #4)
    
    Analisa métricas diariamente e ajusta automaticamente.
    """
    
    def __init__(self, db):
        self.db = db
        self.model = "gpt-4o"
    
    async def analyze_and_optimize(self, user_id: str, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa métricas e sugere/executa otimizações"""
        
        system_prompt = """Você é a IA de Otimização Contínua do ELION MARKET 360.
        
Função: Analisar métricas DIARIAMENTE e ajustar automaticamente.
        
Você detecta:
        - Campanhas ruins (baixo ROI, alto CPA)
        - Públicos saturados (frequência alta, queda de engajamento)
        - Criativos cansados (CTR decrescente)
        - Oportunidades de escala
        
Você ajusta automaticamente:
        - Segmentação (pausa/ativa públicos)
        - Orçamento (aumenta vencedores, reduz perdedores)
        - Frequência (evita saturação)
        - Objetivo (muda se necessário)
        
Retorne JSON:
        {
            "analise": "resumo em linguagem humana",
            "problemas_detectados": [
                {"campanha": "", "problema": "", "gravidade": "alta|media|baixa"}
            ],
            "otimizacoes_aplicadas": [
                {"campanha": "", "acao": "", "razao": "", "impacto_esperado": ""}
            ],
            "oportunidades_escala": [],
            "alertas_criticos": [],
            "proximo_passo": ""
        }"""        
        session_id = f"optimizer_{user_id}_{datetime.now(timezone.utc).timestamp()}"
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_prompt
        ).with_model("openai", self.model)
        
        try:
            message = UserMessage(text=f"""Analise estas métricas e otimize:
            
            {metrics_data}
            
            Retorne análise e otimizações em JSON.""")
            
            response = await chat.send_message(message)
            
            import json
            optimization = json.loads(response)
            
            # Salvar otimização
            await self._save_optimization(user_id, optimization)
            
            return optimization
            
        except Exception as e:
            logger.error(f"Optimization error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _save_optimization(self, user_id: str, optimization: Dict[str, Any]):
        doc = {
            'user_id': user_id,
            'type': 'optimization',
            'data': optimization,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await self.db.optimizations.insert_one(doc)


class IntelligentCRM:
    """CAMADA 6: CRM Inteligente (IA #5)
    
    CRM automático por nicho com classificação e pipeline.
    """
    
    def __init__(self, db):
        self.db = db
        self.model = "gpt-4o"
    
    async def classify_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classifica lead automaticamente"""
        
        system_prompt = """Você é o CRM Inteligente do ELION MARKET 360.
        
Função: CLASSIFICAR LEADS automaticamente.
        
Classificações:
        - FRIO: Baixo interesse, precisa nutrição
        - MORNO: Interesse moderado, precisa mais informação
        - QUENTE: Pronto para compra, acionar vendedor
        
Pipeline:
        1. Lead (novo contato)
        2. Oportunidade (mostrou interesse)
        3. Proposta (em negociação)
        4. Venda (fechou)
        5. Pós-venda (cliente ativo)
        
Retorne JSON:
        {
            "temperatura": "frio|morno|quente",
            "estagio_pipeline": "lead|oportunidade|proposta|venda|pos_venda",
            "pontuacao": 0-100,
            "proxima_acao": "descrição",
            "tempo_resposta": "imediato|24h|48h",
            "responsavel": "ia|vendedor",
            "tags": [],
            "notas": ""
        }"""        
        session_id = f"crm_{datetime.now(timezone.utc).timestamp()}"
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=system_prompt
        ).with_model("openai", self.model)
        
        try:
            message = UserMessage(text=f"""Classifique este lead:
            
            {lead_data}
            
            Retorne classificação em JSON.""")
            
            response = await chat.send_message(message)
            
            import json
            classification = json.loads(response)
            
            # Atualizar lead no CRM
            await self._update_lead(lead_data['id'], classification)
            
            return classification
            
        except Exception as e:
            logger.error(f"CRM classification error: {str(e)}")
            return {'status': 'error'}
    
    async def _update_lead(self, lead_id: str, classification: Dict[str, Any]):
        await self.db.crm_leads.update_one(
            {'id': lead_id},
            {'$set': classification}
        )


class OmnichannelAssistant:
    """CAMADA 7: Atendimento Omnichannel com IA (IA #6)
    
    Atende WhatsApp, Instagram, Messenger e e-mail com IA.
    """
    
    def __init__(self, db):
        self.db = db
        self.model = "gpt-4o"
        self.sessions = {}  # Cache de sessões ativas
    
    async def handle_message(self, channel: str, customer_id: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Processa mensagem de cliente"""
        
        # Buscar histórico de conversa
        history = await self._get_conversation_history(customer_id, channel)
        
        system_prompt = f"""Você é o Assistente Omnichannel do ELION MARKET 360.
        
Canal atual: {channel}
Nicho do negócio: {context.get('nicho', 'marketing digital')}
        
Funções:
        1. Atender com linguagem alinhada ao nicho
        2. Responder dúvidas
        3. Qualificar leads
        4. Agendar chamadas
        5. Alimentar CRM automaticamente
        
REGRAS:
        - Seja humano, não robótico
        - Use emojis com moderação
        - Escale para humano quando necessário
        - Sempre ofereça próximo passo claro
        
Sinais para escalar:
        - Reclamações sérias
        - Negociações complexas
        - Solicitação explícita de humano
        
Retorne JSON:
        {
            "resposta": "texto da resposta",
            "acao": "responder|qualificar|agendar|escalar",
            "escalar_humano": true|false,
            "razao_escalonamento": "se aplicavel",
            "dados_lead": {"campo": "valor"},
            "proxima_pergunta": "se aplicavel"
        }"""        
        session_id = f"{customer_id}_{channel}"
        
        if session_id not in self.sessions:
            self.sessions[session_id] = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=session_id,
                system_message=system_prompt
            ).with_model("openai", self.model)
        
        chat = self.sessions[session_id]
        
        try:
            user_message = UserMessage(text=f"""Cliente disse: {message}
            
            Histórico: {history[-5:] if history else 'Primeira mensagem'}
            
            Responda em JSON.""")
            
            response = await chat.send_message(user_message)
            
            import json
            ai_response = json.loads(response)
            
            # Salvar conversa
            await self._save_conversation(customer_id, channel, message, ai_response)
            
            # Atualizar CRM se dados coletados
            if ai_response.get('dados_lead'):
                await self._update_crm_from_conversation(customer_id, ai_response['dados_lead'])
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Omnichannel assistant error: {str(e)}")
            return {
                'resposta': 'Desculpe, houve um erro. Um atendente humano irá responder em breve.',
                'escalar_humano': True,
                'razao_escalonamento': 'erro_tecnico'
            }
    
    async def _get_conversation_history(self, customer_id: str, channel: str) -> List[Dict[str, Any]]:
        """Busca histórico de conversa"""
        cursor = self.db.conversations.find(
            {'customer_id': customer_id, 'channel': channel}
        ).sort('created_at', -1).limit(10)
        
        return await cursor.to_list(10)
    
    async def _save_conversation(self, customer_id: str, channel: str, message: str, response: Dict[str, Any]):
        """Salva conversa no banco"""
        doc = {
            'customer_id': customer_id,
            'channel': channel,
            'message': message,
            'response': response['resposta'],
            'action': response.get('acao'),
            'escalated': response.get('escalar_humano', False),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        await self.db.conversations.insert_one(doc)
    
    async def _update_crm_from_conversation(self, customer_id: str, lead_data: Dict[str, Any]):
        """Atualiza CRM com dados coletados na conversa"""
        await self.db.crm_leads.update_one(
            {'customer_id': customer_id},
            {'$set': lead_data},
            upsert=True
        )
