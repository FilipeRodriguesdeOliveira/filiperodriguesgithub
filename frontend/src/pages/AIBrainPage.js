import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Brain } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

export default function AIBrainPage() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await api.getAnalyses('brain');
      setHistory(response.data);
      if (response.data.length > 0) {
        setAnalysis(response.data[0]);
      }
    } catch (error) {
      console.error('Erro ao carregar histórico');
    }
  };

  const runAnalysis = async () => {
    setLoading(true);
    try {
      const response = await api.analyzeWithAI({ type: 'brain' });
      setAnalysis(response.data);
      toast.success('Análise concluída!');
      fetchHistory();
    } catch (error) {
      toast.error('Erro ao executar análise');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8" data-testid="ai-brain-page">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <Brain className="w-10 h-10 text-[#6366f1] animate-pulse-glow" />
            IA Cérebro
          </h1>
          <p className="text-gray-400">Análise estratégica e coordenação das IAs</p>
        </div>
        <Button
          data-testid="run-analysis-btn"
          onClick={runAnalysis}
          disabled={loading}
          className="bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full glow-primary"
        >
          {loading ? 'Analisando...' : 'Executar Análise'}
        </Button>
      </div>

      {analysis ? (
        <div className="space-y-6">
          <div className="glass-card p-8 rounded-2xl" data-testid="analysis-result">
            <h2 className="text-2xl font-bold mb-4">Análise Estratégica</h2>
            <div className="prose prose-invert max-w-none">
              <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">{analysis.analysis}</p>
            </div>
          </div>

          {analysis.recommendations && analysis.recommendations.length > 0 && (
            <div className="glass-card p-8 rounded-2xl" data-testid="recommendations">
              <h2 className="text-2xl font-bold mb-4">Recomendações</h2>
              <ul className="space-y-3">
                {analysis.recommendations.map((rec, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <span className="w-6 h-6 rounded-full bg-[#6366f1]/20 flex items-center justify-center text-[#6366f1] text-sm mt-1 flex-shrink-0">
                      {idx + 1}
                    </span>
                    <span className="text-gray-300 flex-1">{rec.replace(/^[-•*]\s*/, '')}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="text-sm text-gray-500">
            Análise realizada em {new Date(analysis.created_at).toLocaleString('pt-BR')}
          </div>
        </div>
      ) : (
        <div className="glass-card p-16 rounded-2xl text-center">
          <Brain className="w-24 h-24 text-[#6366f1] mx-auto mb-6 animate-pulse-glow" />
          <h3 className="text-2xl font-bold mb-4">Nenhuma análise ainda</h3>
          <p className="text-gray-400 mb-8">Clique em "Executar Análise" para que a IA Cérebro analise seus dados</p>
        </div>
      )}
    </div>
  );
}