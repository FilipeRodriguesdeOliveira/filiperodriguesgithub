import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Button } from '@/components/ui/button';
import { Plus, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function ConnectionsPage() {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newConn, setNewConn] = useState({ platform: '', apiKey: '' });

  useEffect(() => {
    fetchConnections();
  }, []);

  const fetchConnections = async () => {
    try {
      const response = await api.getConnections();
      setConnections(response.data);
    } catch (error) {
      toast.error('Erro ao carregar conexões');
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    if (!newConn.platform) {
      toast.error('Selecione uma plataforma');
      return;
    }
    
    try {
      await api.createConnection({
        platform: newConn.platform,
        credentials: { api_key: newConn.apiKey || 'demo_key' }
      });
      toast.success('Plataforma conectada com sucesso!');
      setDialogOpen(false);
      setNewConn({ platform: '', apiKey: '' });
      fetchConnections();
    } catch (error) {
      toast.error('Erro ao conectar plataforma');
    }
  };

  const platforms = [
    { value: 'meta', label: 'Meta/Instagram', desc: 'Facebook Ads e Instagram' },
    { value: 'google_ads', label: 'Google Ads', desc: 'Anúncios do Google' },
    { value: 'ga4', label: 'Google Analytics 4', desc: 'Análise de comportamento' },
    { value: 'website', label: 'Seu Website', desc: 'Integração direta' }
  ];

  return (
    <div className="p-8" data-testid="connections-page">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">Conexões</h1>
          <p className="text-gray-400">Conecte suas plataformas de marketing</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-connection-btn" className="bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full glow-primary">
              <Plus className="w-5 h-5 mr-2" />
              Adicionar Conexão
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#0f172a] border-gray-800">
            <DialogHeader>
              <DialogTitle className="text-2xl font-bold">Nova Conexão</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 mt-4">
              <div>
                <Label className="text-gray-300">Plataforma</Label>
                <Select value={newConn.platform} onValueChange={(value) => setNewConn({ ...newConn, platform: value })}>
                  <SelectTrigger data-testid="platform-select" className="mt-2 bg-[#030712] border-gray-700 text-white">
                    <SelectValue placeholder="Selecione uma plataforma" />
                  </SelectTrigger>
                  <SelectContent className="bg-[#0f172a] border-gray-700">
                    {platforms.map((p) => (
                      <SelectItem key={p.value} value={p.value} className="text-white hover:bg-gray-800">
                        {p.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-gray-300">API Key (Opcional)</Label>
                <Input
                  data-testid="api-key-input"
                  value={newConn.apiKey}
                  onChange={(e) => setNewConn({ ...newConn, apiKey: e.target.value })}
                  className="mt-2 bg-[#030712] border-gray-700 text-white"
                  placeholder="Deixe vazio para demo"
                />
              </div>
              <Button
                data-testid="connect-submit-btn"
                onClick={handleConnect}
                className="w-full bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full"
              >
                Conectar
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {platforms.map((platform) => {
          const conn = connections.find((c) => c.platform === platform.value);
          const isConnected = !!conn;

          return (
            <div
              key={platform.value}
              data-testid={`platform-${platform.value}`}
              className="glass-card p-6 rounded-2xl"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-1">{platform.label}</h3>
                  <p className="text-sm text-gray-400">{platform.desc}</p>
                </div>
                <div className="ml-4">
                  {isConnected ? (
                    <CheckCircle className="w-8 h-8 text-[#10b981]" />
                  ) : (
                    <XCircle className="w-8 h-8 text-gray-600" />
                  )}
                </div>
              </div>

              {isConnected && (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Status:</span>
                    <span className="text-[#10b981] font-medium">Conectado</span>
                  </div>
                  {conn.last_sync && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Última sinc:</span>
                      <span className="text-gray-300">{new Date(conn.last_sync).toLocaleString('pt-BR')}</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {connections.length === 0 && !loading && (
        <div className="text-center py-16">
          <p className="text-gray-400 mb-4">Nenhuma conexão ainda. Comece conectando uma plataforma!</p>
        </div>
      )}
    </div>
  );
}