import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Button } from '@/components/ui/button';
import { CheckCircle, XCircle, RefreshCw, Settings, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function PlatformIntegrationsPage() {
  const [platforms, setPlatforms] = useState([]);
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState({});

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [platformsResp, connectionsResp] = await Promise.all([
        api.getOAuthPlatforms(),
        api.getOAuthConnections()
      ]);
      setPlatforms(platformsResp.data.platforms);
      setConnections(connectionsResp.data.connections);
    } catch (error) {
      toast.error('Erro ao carregar integrações');
    } finally {
      setLoading(false);
    }
  };

  const isConnected = (platformId) => {
    return connections.some(conn => conn.platform === platformId && conn.status === 'active');
  };

  const getConnection = (platformId) => {
    return connections.find(conn => conn.platform === platformId);
  };

  const handleConnect = async (platformId) => {
    try {
      const response = await api.authorizeOAuthPlatform(platformId);
      window.location.href = response.data.authorization_url;
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao iniciar conexão');
    }
  };

  const handleDisconnect = async (platformId) => {
    try {
      await api.disconnectOAuthPlatform(platformId);
      toast.success('Plataforma desconectada');
      fetchData();
    } catch (error) {
      toast.error('Erro ao desconectar plataforma');
    }
  };

  const handleSync = async (platformId) => {
    setSyncing(prev => ({ ...prev, [platformId]: true }));
    try {
      await api.syncOAuthPlatform(platformId);
      toast.success('Dados sincronizados com sucesso!');
      fetchData();
    } catch (error) {
      toast.error('Erro ao sincronizar dados');
    } finally {
      setSyncing(prev => ({ ...prev, [platformId]: false }));
    }
  };

  const getPlatformIcon = (platformId) => {
    const icons = {
      google: '🔍',
      meta: '📘',
      linkedin: '💼',
      tiktok: '🎵'
    };
    return icons[platformId] || '🔗';
  };

  const getPlatformColor = (platformId) => {
    const colors = {
      google: '#4285F4',
      meta: '#1877F2',
      linkedin: '#0A66C2',
      tiktok: '#000000'
    };
    return colors[platformId] || '#6366f1';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#6366f1]" />
      </div>
    );
  }

  return (
    <div className="p-8" data-testid="platform-integrations-page">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Integrações de Plataformas</h1>
        <p className="text-gray-400">Conecte suas contas oficialmente via OAuth 2.0</p>
      </div>

      <Alert className="mb-8 border-[#6366f1] bg-[#6366f1]/10">
        <AlertDescription className="text-gray-300">
          🔒 <strong>Segurança:</strong> Todas as conexões utilizam OAuth 2.0 oficial. Seus tokens são criptografados e armazenados com segurança.
        </AlertDescription>
      </Alert>

      <div className="grid md:grid-cols-2 gap-6">
        {platforms.map((platform) => {
          const connected = isConnected(platform.id);
          const connection = getConnection(platform.id);
          const isSyncing = syncing[platform.id];

          return (
            <div
              key={platform.id}
              data-testid={`platform-${platform.id}`}
              className="glass-card p-6 rounded-2xl"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div
                    className="text-4xl w-16 h-16 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: `${getPlatformColor(platform.id)}20` }}
                  >
                    {getPlatformIcon(platform.id)}
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">{platform.name}</h3>
                    <p className="text-sm text-gray-400">
                      {connected ? 'Conectada' : platform.configured ? 'Disponível' : 'Não configurada'}
                    </p>
                  </div>
                </div>
                <div>
                  {connected ? (
                    <CheckCircle className="w-8 h-8 text-[#10b981]" />
                  ) : (
                    <XCircle className="w-8 h-8 text-gray-600" />
                  )}
                </div>
              </div>

              {connection && (
                <div className="space-y-2 text-sm mb-4">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Nome:</span>
                    <span className="text-gray-300">{connection.platform_name}</span>
                  </div>
                  {connection.platform_email && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Email:</span>
                      <span className="text-gray-300">{connection.platform_email}</span>
                    </div>
                  )}
                  {connection.last_synced && (
                    <div className="flex justify-between">
                      <span className="text-gray-400">Última sinc:</span>
                      <span className="text-gray-300">
                        {new Date(connection.last_synced).toLocaleString('pt-BR')}
                      </span>
                    </div>
                  )}
                </div>
              )}

              <div className="flex gap-2">
                {!connected ? (
                  <Button
                    data-testid={`connect-${platform.id}-btn`}
                    onClick={() => handleConnect(platform.id)}
                    disabled={!platform.configured}
                    className="flex-1 rounded-full"
                    style={{ backgroundColor: platform.configured ? getPlatformColor(platform.id) : '#666' }}
                  >
                    {platform.configured ? 'Conectar' : 'Não Configurada'}
                  </Button>
                ) : (
                  <>
                    <Button
                      data-testid={`sync-${platform.id}-btn`}
                      onClick={() => handleSync(platform.id)}
                      disabled={isSyncing}
                      className="flex-1 bg-[#6366f1] hover:bg-[#5558e3] rounded-full"
                    >
                      <RefreshCw className={`w-4 h-4 mr-2 ${isSyncing ? 'animate-spin' : ''}`} />
                      {isSyncing ? 'Sincronizando...' : 'Sincronizar'}
                    </Button>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button
                          data-testid={`disconnect-${platform.id}-btn`}
                          variant="outline"
                          className="border-gray-700 text-gray-300 hover:bg-gray-800 rounded-full"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="bg-[#0f172a] border-gray-800">
                        <DialogHeader>
                          <DialogTitle className="text-2xl font-bold">Desconectar {platform.name}?</DialogTitle>
                          <DialogDescription className="text-gray-400">
                            Isso removerá a conexão e impedirá a coleta automática de dados desta plataforma.
                          </DialogDescription>
                        </DialogHeader>
                        <div className="flex gap-3 mt-4">
                          <Button
                            onClick={() => handleDisconnect(platform.id)}
                            variant="destructive"
                            className="flex-1 rounded-full"
                          >
                            Sim, Desconectar
                          </Button>
                          <DialogTrigger asChild>
                            <Button variant="outline" className="flex-1 rounded-full border-gray-700">
                              Cancelar
                            </Button>
                          </DialogTrigger>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </>
                )}
              </div>

              {platform.scopes && platform.scopes.length > 0 && (
                <Dialog>
                  <DialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="mt-3 w-full text-gray-400 hover:text-white"
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Ver Permissões
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="bg-[#0f172a] border-gray-800">
                    <DialogHeader>
                      <DialogTitle className="text-2xl font-bold">Permissões - {platform.name}</DialogTitle>
                      <DialogDescription className="text-gray-400">
                        Escopos OAuth solicitados durante a conexão:
                      </DialogDescription>
                    </DialogHeader>
                    <ul className="space-y-2 mt-4">
                      {platform.scopes.map((scope, idx) => (
                        <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                          <CheckCircle className="w-4 h-4 text-[#10b981] mt-0.5 flex-shrink-0" />
                          <span>{scope}</span>
                        </li>
                      ))}
                    </ul>
                  </DialogContent>
                </Dialog>
              )}
            </div>
          );
        })}
      </div>

      {connections.length > 0 && (
        <div className="mt-8 glass-card p-6 rounded-2xl">
          <h2 className="text-2xl font-bold mb-4">Resumo de Integrações</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-[#0f172a] p-4 rounded-xl">
              <p className="text-gray-400 text-sm">Total Conectadas</p>
              <p className="text-3xl font-bold text-[#6366f1]">{connections.length}</p>
            </div>
            <div className="bg-[#0f172a] p-4 rounded-xl">
              <p className="text-gray-400 text-sm">Coleta Automática</p>
              <p className="text-3xl font-bold text-[#10b981]">Ativa</p>
            </div>
            <div className="bg-[#0f172a] p-4 rounded-xl">
              <p className="text-gray-400 text-sm">Próxima Sinc</p>
              <p className="text-lg font-bold text-gray-300">Em breve</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}