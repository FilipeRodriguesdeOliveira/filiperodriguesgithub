import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';

export default function OAuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('processing'); // processing, success, error
  const [message, setMessage] = useState('Finalizando conexão...');
  const navigate = useNavigate();

  useEffect(() => {
    handleCallback();
  }, []);

  const handleCallback = async () => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');
    
    if (error) {
      setStatus('error');
      setMessage('Conexão cancelada ou erro de autorização');
      setTimeout(() => {
        const isOnboarding = localStorage.getItem('onboarding_flow');
        if (isOnboarding) {
          localStorage.removeItem('onboarding_flow');
          navigate('/onboarding');
        } else {
          navigate('/dashboard/platform-integrations');
        }
      }, 3000);
      return;
    }

    if (!code) {
      setStatus('error');
      setMessage('Código de autorização não encontrado');
      setTimeout(() => navigate('/dashboard'), 3000);
      return;
    }

    // OAuth callback is handled by backend automatically
    // Just show success and redirect
    setStatus('success');
    setMessage('Conexão realizada com sucesso!');
    
    setTimeout(async () => {
      const isOnboarding = localStorage.getItem('onboarding_flow');
      
      if (isOnboarding) {
        // Continue onboarding flow
        localStorage.removeItem('onboarding_flow');
        
        // Trigger AI analysis
        setMessage('Analisando com IA...');
        
        try {
          // Import api dynamically
          const { api } = await import('@/services/api');
          await api.runMarketIntelligence();
          await api.createMarketingStrategy();
        } catch (error) {
          console.error('AI analysis error:', error);
        }
        
        navigate('/dashboard');
      } else {
        navigate('/dashboard/platform-integrations');
      }
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-[#030712] flex items-center justify-center px-6">
      <div className="glass-card p-12 rounded-2xl text-center space-y-6 max-w-md">
        {status === 'processing' && (
          <>
            <Loader2 className="w-16 h-16 text-[#6366f1] animate-spin mx-auto" />
            <h2 className="text-2xl font-bold">Processando...</h2>
            <p className="text-gray-400">{message}</p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <CheckCircle className="w-16 h-16 text-[#10b981] mx-auto" />
            <h2 className="text-2xl font-bold text-[#10b981]">Sucesso!</h2>
            <p className="text-gray-400">{message}</p>
          </>
        )}
        
        {status === 'error' && (
          <>
            <XCircle className="w-16 h-16 text-red-500 mx-auto" />
            <h2 className="text-2xl font-bold text-red-500">Erro</h2>
            <p className="text-gray-400">{message}</p>
          </>
        )}
      </div>
    </div>
  );
}