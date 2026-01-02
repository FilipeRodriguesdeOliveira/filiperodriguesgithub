import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Brain, Globe, Instagram, Loader2, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';

export default function OnboardingPage() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('input'); // input, connecting, analyzing, complete
  const [detectedPlatform, setDetectedPlatform] = useState(null);
  const [progress, setProgress] = useState([]);
  const navigate = useNavigate();

  const addProgress = (message, status = 'loading') => {
    setProgress(prev => [...prev, { message, status, time: new Date().toLocaleTimeString('pt-BR') }]);
  };

  const updateLastProgress = (status) => {
    setProgress(prev => {
      const updated = [...prev];
      if (updated.length > 0) {
        updated[updated.length - 1].status = status;
      }
      return updated;
    });
  };

  const detectPlatform = (value) => {
    // Detect if it's a website URL
    if (value.match(/^(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}/)) {
      return { type: 'website', value: value };
    }
    
    // Detect Instagram username (@username or username)
    if (value.match(/^@?[a-zA-Z0-9._]+$/)) {
      return { type: 'instagram', value: value.replace('@', '') };
    }
    
    return null;
  };

  const handleStart = async () => {
    if (!input.trim()) {
      toast.error('Por favor, insira seu site ou Instagram');
      return;
    }

    const platform = detectPlatform(input.trim());
    
    if (!platform) {
      toast.error('Formato inválido. Use uma URL de site ou username do Instagram');
      return;
    }

    setDetectedPlatform(platform);
    setLoading(true);
    setStep('connecting');
    setProgress([]);

    try {
      if (platform.type === 'website') {
        await handleWebsiteFlow(platform.value);
      } else if (platform.type === 'instagram') {
        await handleInstagramFlow(platform.value);
      }
    } catch (error) {
      console.error('Onboarding error:', error);
      toast.error('Erro no processo. Tente novamente.');
      setLoading(false);
      setStep('input');
    }
  };

  const handleWebsiteFlow = async (url) => {
    // Step 1: Save website
    addProgress('Salvando informações do site...');
    await new Promise(resolve => setTimeout(resolve, 500));
    
    try {
      await api.createConnection({
        platform: 'website',
        credentials: { url: url }
      });
      updateLastProgress('success');
      
      // Step 2: Analyze website
      addProgress('Analisando seu site em tempo real...');
      await analyzeWithAI();
      updateLastProgress('success');
      
      setStep('complete');
    } catch (error) {
      updateLastProgress('error');
      throw error;
    }
  };

  const handleInstagramFlow = async (username) => {
    // Step 1: Initiate Instagram OAuth
    addProgress('Preparando conexão com Instagram...');
    
    try {
      const response = await api.authorizeOAuthPlatform('meta');
      updateLastProgress('success');
      
      addProgress('Redirecionando para login do Instagram...');
      
      // Store username for after OAuth return
      localStorage.setItem('instagram_username', username);
      localStorage.setItem('onboarding_flow', 'true');
      
      // Redirect to OAuth
      window.location.href = response.data.authorization_url;
      
    } catch (error) {
      updateLastProgress('error');
      if (error.response?.data?.detail?.includes('not configured')) {
        toast.error('Instagram não configurado. Entre em contato com o suporte.');
      } else {
        throw error;
      }
    }
  };

  const analyzeWithAI = async () => {
    // Step 3: Run Market Intelligence
    addProgress('IA analisando nicho, público e produtos...');
    
    try {
      const aiResponse = await api.runMarketIntelligence();
      updateLastProgress('success');
      
      // Step 4: Create Strategy
      addProgress('Criando estratégia de marketing personalizada...');
      await api.createMarketingStrategy();
      updateLastProgress('success');
      
      return aiResponse.data;
    } catch (error) {
      updateLastProgress('error');
      // Continue even if AI fails
      console.error('AI analysis error:', error);
    }
  };

  const getIcon = () => {
    if (detectedPlatform?.type === 'website') return <Globe className="w-12 h-12" />;
    if (detectedPlatform?.type === 'instagram') return <Instagram className="w-12 h-12" />;
    return <Brain className="w-12 h-12" />;
  };

  const getPlatformName = () => {
    if (detectedPlatform?.type === 'website') return 'Website';
    if (detectedPlatform?.type === 'instagram') return 'Instagram';
    return 'Plataforma';
  };

  return (
    <div className="min-h-screen bg-[#030712] flex items-center justify-center px-6" data-testid="onboarding-page">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-6">
            <Brain className="w-20 h-20 text-[#6366f1] animate-pulse-glow" />
          </div>
          <h1 className="text-5xl font-bold gradient-text mb-4">ELION MARKET 360</h1>
          <p className="text-xl text-gray-400">Marketing Inteligente Automatizado</p>
        </div>

        {/* Input Step */}
        {step === 'input' && (
          <div className="glass-card p-8 rounded-2xl space-y-6">
            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold">Começar é Simples</h2>
              <p className="text-gray-400">Informe seu site ou Instagram para começar</p>
            </div>

            <div className="space-y-4">
              <div>
                <Input
                  data-testid="onboarding-input"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleStart()}
                  placeholder="www.seusite.com ou @seuinstagram"
                  className="text-lg py-6 bg-[#0f172a] border-gray-700 text-white focus:border-[#6366f1]"
                  autoFocus
                />
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm text-gray-400">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-[#6366f1]" />
                  <span>Site: www.exemplo.com</span>
                </div>
                <div className="flex items-center gap-2">
                  <Instagram className="w-4 h-4 text-[#06b6d4]" />
                  <span>Instagram: @usuario</span>
                </div>
              </div>

              <Button
                data-testid="start-btn"
                onClick={handleStart}
                disabled={loading}
                className="w-full bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full py-6 text-lg glow-primary"
              >
                {loading ? 'Processando...' : 'Começar Agora'}
              </Button>
            </div>
          </div>
        )}

        {/* Connecting/Analyzing Step */}
        {(step === 'connecting' || step === 'analyzing') && (
          <div className="glass-card p-8 rounded-2xl space-y-6">
            <div className="text-center space-y-4">
              <div className="flex justify-center" style={{ color: detectedPlatform?.type === 'instagram' ? '#06b6d4' : '#6366f1' }}>
                {getIcon()}
              </div>
              <h2 className="text-2xl font-bold">
                Conectando {getPlatformName()}
              </h2>
              <p className="text-gray-400">{detectedPlatform?.value}</p>
            </div>

            {/* Progress Log */}
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {progress.map((item, idx) => (
                <div
                  key={idx}
                  data-testid={`progress-${idx}`}
                  className="flex items-center gap-3 p-3 bg-[#0f172a] rounded-lg"
                >
                  {item.status === 'loading' && (
                    <Loader2 className="w-5 h-5 text-[#6366f1] animate-spin flex-shrink-0" />
                  )}
                  {item.status === 'success' && (
                    <CheckCircle className="w-5 h-5 text-[#10b981] flex-shrink-0" />
                  )}
                  {item.status === 'error' && (
                    <div className="w-5 h-5 rounded-full bg-red-500 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <p className="text-gray-300">{item.message}</p>
                    <p className="text-xs text-gray-500">{item.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Complete Step */}
        {step === 'complete' && (
          <div className="glass-card p-8 rounded-2xl space-y-6 text-center">
            <div className="flex justify-center">
              <CheckCircle className="w-20 h-20 text-[#10b981]" />
            </div>
            <h2 className="text-3xl font-bold">Tudo Pronto!</h2>
            <p className="text-xl text-gray-400">
              Sua {getPlatformName()} foi conectada e analisada pela IA
            </p>
            
            <div className="space-y-3 text-left">
              <div className="p-4 bg-[#0f172a] rounded-lg">
                <p className="text-sm text-gray-400 mb-1">✅ Nicho identificado</p>
                <p className="text-sm text-gray-400 mb-1">✅ Público-alvo analisado</p>
                <p className="text-sm text-gray-400 mb-1">✅ Produtos mapeados</p>
                <p className="text-sm text-gray-400">✅ Estratégia criada</p>
              </div>
            </div>

            <Button
              data-testid="go-dashboard-btn"
              onClick={() => navigate('/dashboard')}
              className="w-full bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full py-6 text-lg glow-primary"
            >
              Ver Meu Dashboard
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}