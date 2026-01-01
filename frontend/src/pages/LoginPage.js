import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Brain } from 'lucide-react';
import { toast } from 'sonner';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Login realizado com sucesso!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erro ao fazer login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#030712] flex items-center justify-center px-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Brain className="w-16 h-16 text-[#6366f1]" />
          </div>
          <h1 className="text-4xl font-bold gradient-text mb-2">ELION</h1>
          <p className="text-gray-400">Entre na sua conta</p>
        </div>

        <div className="glass-card p-8 rounded-2xl">
          <form onSubmit={handleSubmit} className="space-y-6" data-testid="login-form">
            <div>
              <Label htmlFor="email" className="text-gray-300">Email</Label>
              <Input
                id="email"
                type="email"
                data-testid="login-email-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-2 bg-[#0f172a] border-gray-700 text-white focus:border-[#6366f1]"
                placeholder="seu@email.com"
                required
              />
            </div>

            <div>
              <Label htmlFor="password" className="text-gray-300">Senha</Label>
              <Input
                id="password"
                type="password"
                data-testid="login-password-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-2 bg-[#0f172a] border-gray-700 text-white focus:border-[#6366f1]"
                placeholder="********"
                required
              />
            </div>

            <Button
              type="submit"
              data-testid="login-submit-btn"
              disabled={loading}
              className="w-full bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full py-6 glow-primary"
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Não tem uma conta?{' '}
              <Link to="/register" className="text-[#6366f1] hover:text-[#5558e3]">
                Registre-se
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}