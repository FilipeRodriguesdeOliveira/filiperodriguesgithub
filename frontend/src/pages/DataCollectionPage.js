import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Database } from 'lucide-react';
import { toast } from 'sonner';

export default function DataCollectionPage() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await api.getDataCollection();
      setData(response.data);
    } catch (error) {
      toast.error('Erro ao carregar dados');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8" data-testid="data-collection-page">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Coleta de Dados</h1>
        <p className="text-gray-400">Dados coletados automaticamente das plataformas</p>
      </div>

      {data.length > 0 ? (
        <div className="grid gap-6">
          {data.map((item) => (
            <div key={item.id} data-testid={`data-${item.id}`} className="glass-card p-6 rounded-2xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold capitalize">{item.platform}</h3>
                <span className="text-sm text-gray-400">
                  {new Date(item.collected_at).toLocaleString('pt-BR')}
                </span>
              </div>

              <div className="bg-[#0f172a] p-4 rounded-lg">
                <pre className="text-sm text-gray-300 overflow-x-auto">
                  {JSON.stringify(item.data, null, 2)}
                </pre>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-card p-16 rounded-2xl text-center">
          <Database className="w-24 h-24 text-[#6366f1] mx-auto mb-6 opacity-50" />
          <h3 className="text-2xl font-bold mb-4">Nenhum dado coletado ainda</h3>
          <p className="text-gray-400">
            Conecte suas plataformas para começar a coletar dados automaticamente
          </p>
        </div>
      )}
    </div>
  );
}