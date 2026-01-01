import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Rocket } from 'lucide-react';
import { toast } from 'sonner';

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const response = await api.getCampaigns();
      setCampaigns(response.data);
    } catch (error) {
      toast.error('Erro ao carregar campanhas');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      draft: '#6b7280',
      active: '#10b981',
      paused: '#f59e0b',
      completed: '#6366f1'
    };
    return colors[status] || colors.draft;
  };

  const getStatusLabel = (status) => {
    const labels = {
      draft: 'Rascunho',
      active: 'Ativa',
      paused: 'Pausada',
      completed: 'Concluída'
    };
    return labels[status] || status;
  };

  return (
    <div className="p-8" data-testid="campaigns-page">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Campanhas</h1>
        <p className="text-gray-400">Campanhas criadas e gerenciadas pela IA</p>
      </div>

      {campaigns.length > 0 ? (
        <div className="grid gap-6">
          {campaigns.map((campaign) => (
            <div key={campaign.id} data-testid={`campaign-${campaign.id}`} className="glass-card p-6 rounded-2xl">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-2xl font-bold mb-2">{campaign.name}</h3>
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    <span>Plataforma: <span className="text-white">{campaign.platform}</span></span>
                    <span>Objetivo: <span className="text-white">{campaign.objective}</span></span>
                  </div>
                </div>
                <span 
                  className="px-4 py-2 rounded-full text-sm font-medium"
                  style={{ 
                    backgroundColor: `${getStatusColor(campaign.status)}20`,
                    color: getStatusColor(campaign.status)
                  }}
                >
                  {getStatusLabel(campaign.status)}
                </span>
              </div>

              {campaign.structure && Object.keys(campaign.structure).length > 0 && (
                <div className="bg-[#0f172a] p-4 rounded-lg">
                  <p className="text-sm text-gray-400 mb-2">Estrutura da Campanha:</p>
                  <pre className="text-xs text-gray-300 overflow-x-auto">
                    {JSON.stringify(campaign.structure, null, 2)}
                  </pre>
                </div>
              )}

              <div className="mt-4 text-xs text-gray-500">
                Criada em {new Date(campaign.created_at).toLocaleString('pt-BR')}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-card p-16 rounded-2xl text-center">
          <Rocket className="w-24 h-24 text-[#6366f1] mx-auto mb-6 opacity-50" />
          <h3 className="text-2xl font-bold mb-4">Nenhuma campanha ainda</h3>
          <p className="text-gray-400 mb-8">
            As IAs criarão campanhas automaticamente baseadas em seus objetivos e dados coletados
          </p>
        </div>
      )}
    </div>
  );
}