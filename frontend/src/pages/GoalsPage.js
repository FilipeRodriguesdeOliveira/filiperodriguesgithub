import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function GoalsPage() {
  const [goals, setGoals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newGoal, setNewGoal] = useState({ objective: '', target_value: '', description: '' });

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    try {
      const response = await api.getGoals();
      setGoals(response.data);
    } catch (error) {
      toast.error('Erro ao carregar objetivos');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!newGoal.objective) {
      toast.error('Selecione um objetivo');
      return;
    }

    try {
      await api.createGoal({
        objective: newGoal.objective,
        target_value: newGoal.target_value ? parseInt(newGoal.target_value) : null,
        description: newGoal.description
      });
      toast.success('Objetivo criado com sucesso!');
      setDialogOpen(false);
      setNewGoal({ objective: '', target_value: '', description: '' });
      fetchGoals();
    } catch (error) {
      toast.error('Erro ao criar objetivo');
    }
  };

  const objectives = [
    { value: 'leads', label: 'Gerar Leads', icon: '🎯' },
    { value: 'brand', label: 'Construir Marca', icon: '✨' },
    { value: 'followers', label: 'Aumentar Seguidores', icon: '👥' },
    { value: 'sales', label: 'Aumentar Vendas', icon: '💰' }
  ];

  return (
    <div className="p-8" data-testid="goals-page">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Objetivos</h1>
          <p className="text-gray-400">Defina seus objetivos de marketing</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-goal-btn" className="bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full glow-primary">
              <Plus className="w-5 h-5 mr-2" />
              Novo Objetivo
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#0f172a] border-gray-800">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold">Novo Objetivo</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label className="text-gray-300">Tipo de Objetivo</Label>
                <Select value={newGoal.objective} onValueChange={(value) => setNewGoal({ ...newGoal, objective: value })}>
                  <SelectTrigger data-testid="objective-select" className="mt-2 bg-[#030712] border-gray-700 text-white">
                    <SelectValue placeholder="Selecione um objetivo" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#0f172a] border-gray-700">
                    {objectives.map((obj) => (
                      <SelectItem key={obj.value} value={obj.value} className="text-white hover:bg-gray-800">
                        {obj.icon} {obj.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-gray-300">Meta Numérica (Opcional)</Label>
                <Input
                  data-testid="target-value-input"
                  type="number"
                  value={newGoal.target_value}
                  onChange={(e) => setNewGoal({ ...newGoal, target_value: e.target.value })}
                  className="mt-2 bg-[#030712] border-gray-700 text-white"
                  placeholder="Ex: 1000 leads"
                />
              </div>
              <div>
                <Label className="text-gray-300">Descrição</Label>
                <Textarea
                  data-testid="description-input"
                  value={newGoal.description}
                  onChange={(e) => setNewGoal({ ...newGoal, description: e.target.value })}
                  className="mt-2 bg-[#030712] border-gray-700 text-white"
                  placeholder="Descreva seu objetivo..."
                  rows={3}
                />
              </div>
              <Button
                data-testid="goal-submit-btn"
                onClick={handleCreate}
                className="w-full bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full"
              >
                Criar Objetivo
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {goals.map((goal) => {
          const objData = objectives.find((o) => o.value === goal.objective);
          return (
            <div key={goal.id} data-testid={`goal-${goal.id}`} className="glass-card p-6 rounded-2xl">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold mb-2">
                    {objData?.icon} {objData?.label}
                  </h3>
                  {goal.target_value && (
                    <p className="text-2xl font-bold text-[#6366f1] mb-2">{goal.target_value.toLocaleString()}</p>
                  )}
                  {goal.description && (
                    <p className="text-sm text-gray-400">{goal.description}</p>
                  )}
                </div>
                <span className="px-3 py-1 bg-[#10b981]/20 text-[#10b981] rounded-full text-sm">
                  {goal.status === 'active' ? 'Ativo' : 'Pausado'}
                </span>
              </div>
              <div className="text-xs text-gray-500">
                Criado em {new Date(goal.created_at).toLocaleDateString('pt-BR')}
              </div>
            </div>
          );
        })}
      </div>

      {goals.length === 0 && !loading && (
        <div className="text-center py-16">
          <p className="text-gray-400 mb-4">Nenhum objetivo definido ainda. Comece criando um!</p>
        </div>
      )}
    </div>
  );
}