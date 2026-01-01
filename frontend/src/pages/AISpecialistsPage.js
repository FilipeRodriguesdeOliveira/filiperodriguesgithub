import { useState } from 'react';
import { Brain, Users, Target, Zap, BarChart3, Layers } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { api } from '@/services/api';
import { toast } from 'sonner';

export default function AISpecialistsPage() {
  const [activeAI, setActiveAI] = useState('niche');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({});

  const specialists = [
    {
      id: 'niche',
      name: 'Análise de Nicho',
      icon: Users,
      color: '#06b6d4',
      desc: 'Identifica produto, ICP e cria personas'
    },
    {
      id: 'strategy',
      name: 'Estratégia',
      icon: Target,
      color: '#a855f7',
      desc: 'Define tipo de campanha e funil'
    },
    {
      id: 'campaign',
      name: 'Criação',
      icon: Zap,
      color: '#10b981',
      desc: 'Gera estrutura e copy de campanhas'
    },
    {
      id: 'metrics',
      name: 'Analista',
      icon: BarChart3,
      color: '#f59e0b',
      desc: 'Monitora métricas e identifica problemas'
    },
    {
      id: 'optimizer',
      name: 'Otimizadora',
      icon: Layers,
      color: '#ef4444',
      desc: 'Ajusta e escala campanhas'
    },
    {
      id: 'crm',
      name: 'CRM',
      icon: Brain,
      color: '#ec4899',
      desc: 'Classifica leads e gerencia atendimento'
    }
  ];

  const runAIAnalysis = async (type) => {
    setLoading(true);
    try {
      const response = await api.analyzeWithAI({ type });
      setResults({ ...results, [type]: response.data });
      toast.success(`Análise da IA ${specialists.find(s => s.id === type)?.name} concluída!`);
    } catch (error) {
      toast.error('Erro ao executar análise');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8" data-testid="ai-specialists-page">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">IAs Especialistas</h1>
        <p className="text-gray-400">6 especialistas trabalhando em conjunto</p>
      </div>

      <Tabs value={activeAI} onValueChange={setActiveAI} className="space-y-6">
        <TabsList className="bg-[#0f172a] p-2 rounded-xl flex-wrap h-auto gap-2">
          {specialists.map((spec) => (
            <TabsTrigger
              key={spec.id}
              value={spec.id}
              data-testid={`tab-${spec.id}`}
              className="data-[state=active]:bg-[#6366f1] rounded-lg px-6 py-3"
            >
              <spec.icon className="w-4 h-4 mr-2" />
              {spec.name}
            </TabsTrigger>
          ))}
        </TabsList>

        {specialists.map((spec) => (
          <TabsContent key={spec.id} value={spec.id} className="space-y-6">
            <div className="glass-card p-8 rounded-2xl">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div 
                    className="w-16 h-16 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: `${spec.color}20` }}
                  >
                    <spec.icon className="w-8 h-8" style={{ color: spec.color }} />
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold">{spec.name}</h2>
                    <p className="text-gray-400">{spec.desc}</p>
                  </div>
                </div>
                <Button
                  data-testid={`analyze-${spec.id}-btn`}
                  onClick={() => runAIAnalysis(spec.id)}
                  disabled={loading}
                  className="rounded-full"
                  style={{ backgroundColor: spec.color }}
                >
                  {loading ? 'Analisando...' : 'Executar'}
                </Button>
              </div>

              {results[spec.id] ? (
                <div className="space-y-6" data-testid={`result-${spec.id}`}>
                  <div>
                    <h3 className="text-xl font-bold mb-4">Análise</h3>
                    <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">
                      {results[spec.id].analysis}
                    </p>
                  </div>

                  {results[spec.id].recommendations?.length > 0 && (
                    <div>
                      <h3 className="text-xl font-bold mb-4">Recomendações</h3>
                      <ul className="space-y-3">
                        {results[spec.id].recommendations.map((rec, idx) => (
                          <li key={idx} className="flex items-start gap-3">
                            <span 
                              className="w-6 h-6 rounded-full flex items-center justify-center text-white text-sm mt-1 flex-shrink-0"
                              style={{ backgroundColor: `${spec.color}40` }}
                            >
                              {idx + 1}
                            </span>
                            <span className="text-gray-300 flex-1">
                              {rec.replace(/^[-•*]\s*/, '')}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <spec.icon className="w-16 h-16 mx-auto mb-4 opacity-50" style={{ color: spec.color }} />
                  <p className="text-gray-400">Clique em "Executar" para iniciar a análise</p>
                </div>
              )}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}