import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Brain, TrendingUp, Target, Zap } from 'lucide-react';
import { toast } from 'sonner';

export default function DashboardOverview() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.getDashboardStats();
      setStats(response.data);
    } catch (error) {
      toast.error('Erro ao carregar estatísticas');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-pulse-glow">
          <Brain className="w-16 h-16 text-[#6366f1]" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-8" data-testid="dashboard-overview">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
        <p className="text-gray-400">Visão geral do seu marketing automatizado</p>
      </div>

      {/* Stats Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="glass-card p-6 rounded-2xl" data-testid="stat-connections">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-lg bg-[#6366f1]/20 flex items-center justify-center">
              <Zap className="w-6 h-6 text-[#6366f1]" />
            </div>
          </div>
          <p className="text-3xl font-bold mb-1">{stats?.connections || 0}</p>
          <p className="text-gray-400">Conexões Ativas</p>
        </div>

        <div className="glass-card p-6 rounded-2xl" data-testid="stat-campaigns">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-lg bg-[#06b6d4]/20 flex items-center justify-center">
              <Target className="w-6 h-6 text-[#06b6d4]" />
            </div>
          </div>
          <p className="text-3xl font-bold mb-1">{stats?.total_campaigns || 0}</p>
          <p className="text-gray-400">Campanhas Totais</p>
        </div>

        <div className="glass-card p-6 rounded-2xl" data-testid="stat-active-campaigns">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-lg bg-[#10b981]/20 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-[#10b981]" />
            </div>
          </div>
          <p className="text-3xl font-bold mb-1">{stats?.active_campaigns || 0}</p>
          <p className="text-gray-400">Campanhas Ativas</p>
        </div>

        <div className="glass-card p-6 rounded-2xl" data-testid="stat-ai-status">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-lg bg-[#a855f7]/20 flex items-center justify-center">
              <Brain className="w-6 h-6 text-[#a855f7] animate-pulse-glow" />
            </div>
          </div>
          <p className="text-3xl font-bold mb-1 text-[#10b981]">Ativo</p>
          <p className="text-gray-400">Status da IA</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="glass-card p-8 rounded-2xl mb-8">
        <h2 className="text-2xl font-bold mb-6">Ações Rápidas</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <a
            href="/dashboard/connections"
            data-testid="quick-action-connect"
            className="p-6 bg-[#0f172a] rounded-xl hover:bg-[#1e293b] transition-colors border border-gray-800"
          >
            <Zap className="w-8 h-8 text-[#6366f1] mb-3" />
            <h3 className="font-bold mb-2">Conectar Plataforma</h3>
            <p className="text-sm text-gray-400">Adicione Meta, Google Ads ou GA4</p>
          </a>

          <a
            href="/dashboard/goals"
            data-testid="quick-action-goal"
            className="p-6 bg-[#0f172a] rounded-xl hover:bg-[#1e293b] transition-colors border border-gray-800"
          >
            <Target className="w-8 h-8 text-[#06b6d4] mb-3" />
            <h3 className="font-bold mb-2">Definir Objetivo</h3>
            <p className="text-sm text-gray-400">Leads, marca, seguidores ou vendas</p>
          </a>

          <a
            href="/dashboard/ai-brain"
            data-testid="quick-action-ai"
            className="p-6 bg-[#0f172a] rounded-xl hover:bg-[#1e293b] transition-colors border border-gray-800"
          >
            <Brain className="w-8 h-8 text-[#a855f7] mb-3" />
            <h3 className="font-bold mb-2">Consultar IA Cérebro</h3>
            <p className="text-sm text-gray-400">Análise estratégica automática</p>
          </a>
        </div>
      </div>

      {/* AI Status */}
      <div className="glass-card p-8 rounded-2xl">
        <h2 className="text-2xl font-bold mb-6">Status das IAs</h2>
        <div className="space-y-4">
          {[
            { name: 'IA Cérebro', status: 'Ativo', color: '#6366f1' },
            { name: 'Análise de Nicho', status: 'Ativo', color: '#06b6d4' },
            { name: 'Estratégia', status: 'Ativo', color: '#a855f7' },
            { name: 'Criação de Campanhas', status: 'Ativo', color: '#10b981' },
            { name: 'Analista de Métricas', status: 'Ativo', color: '#f59e0b' },
            { name: 'Otimizadora', status: 'Ativo', color: '#ef4444' }
          ].map((ai, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-[#0f172a] rounded-lg" data-testid={`ai-status-${idx}`}>
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full animate-pulse-glow" style={{ backgroundColor: ai.color }} />
                <span className="font-medium">{ai.name}</span>
              </div>
              <span className="text-sm text-[#10b981]">{ai.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}