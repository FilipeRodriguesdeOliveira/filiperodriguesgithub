import { Brain, Zap, BarChart3, Users, Target, Layers } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#030712]">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1764263996452-d8498c9b0ce8?crop=entropy&cs=srgb&fm=jpg&q=85')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#030712]" />
        
        <div className="relative z-10 container mx-auto px-6 py-24">
          <nav className="flex justify-between items-center mb-24">
            <div className="flex items-center gap-2">
              <Brain className="w-8 h-8 text-[#6366f1]" />
              <span className="text-2xl font-bold gradient-text">ELION</span>
            </div>
            <div className="flex gap-4">
              <Link to="/login">
                <Button data-testid="nav-login-btn" variant="ghost" className="text-gray-300 hover:text-white">
                  Login
                </Button>
              </Link>
              <Link to="/register">
                <Button data-testid="nav-register-btn" className="bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full px-8 glow-primary">
                  Começar Grátis
                </Button>
              </Link>
            </div>
          </nav>

          <div className="max-w-5xl mx-auto text-center space-y-8">
            <h1 className="text-5xl md:text-7xl font-bold leading-tight">
              Marketing com IA que
              <span className="gradient-text"> Funciona Sozinho</span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto">
              6 IAs especializadas trabalham 24/7 otimizando suas campanhas, analisando dados e gerando resultados reais. Sem intervenção manual.
            </p>
            <div className="flex gap-4 justify-center pt-8">
              <Link to="/register">
                <Button data-testid="hero-cta-btn" className="bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full px-12 py-6 text-lg glow-primary">
                  Começar Agora
                </Button>
              </Link>
              <Button data-testid="watch-demo-btn" variant="outline" className="border-gray-700 text-gray-300 hover:bg-gray-800 rounded-full px-12 py-6 text-lg">
                Ver Demo
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-6 py-24">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 gradient-text">
          6 IAs Especializadas
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[
            {
              icon: Brain,
              title: 'IA Cérebro',
              desc: 'Decide estratégias e coordena todas as outras IAs',
              color: '#6366f1'
            },
            {
              icon: Users,
              title: 'Análise de Nicho',
              desc: 'Identifica seu público ideal e cria personas reais',
              color: '#06b6d4'
            },
            {
              icon: Target,
              title: 'Estratégia',
              desc: 'Define campanhas, funil e canais automaticamente',
              color: '#a855f7'
            },
            {
              icon: Zap,
              title: 'Criação',
              desc: 'Gera campanhas completas com copy e segmentações',
              color: '#10b981'
            },
            {
              icon: BarChart3,
              title: 'Analista',
              desc: 'Monitora métricas e identifica problemas 24/7',
              color: '#f59e0b'
            },
            {
              icon: Layers,
              title: 'Otimizadora',
              desc: 'Ajusta orçamento e escala o que funciona',
              color: '#ef4444'
            }
          ].map((feature, idx) => (
            <div 
              key={idx}
              data-testid={`feature-card-${idx}`}
              className="glass-card p-8 rounded-2xl hover:-translate-y-2 transition-transform duration-300"
            >
              <feature.icon className="w-12 h-12 mb-4" style={{ color: feature.color }} />
              <h3 className="text-2xl font-bold mb-3">{feature.title}</h3>
              <p className="text-gray-400">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Integrations Section */}
      <div className="container mx-auto px-6 py-24">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-16">
          Conecta com suas
          <span className="gradient-text"> Plataformas</span>
        </h2>
        <div className="grid md:grid-cols-4 gap-8 max-w-4xl mx-auto">
          {['Meta/Instagram', 'Google Ads', 'Google Analytics', 'Seu Website'].map((platform, idx) => (
            <div 
              key={idx}
              data-testid={`integration-${idx}`}
              className="glass-card p-6 rounded-xl text-center hover:scale-105 transition-transform"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-[#6366f1] to-[#06b6d4] rounded-lg mx-auto mb-4" />
              <p className="font-medium text-gray-300">{platform}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-6 py-24">
        <div className="glass-card p-12 rounded-3xl text-center space-y-6">
          <h2 className="text-4xl md:text-5xl font-bold">
            Pronto para Marketing
            <span className="gradient-text"> Automático?</span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Junte-se a centenas de empresas que já automatizaram seu marketing com IA
          </p>
          <Link to="/register">
            <Button data-testid="bottom-cta-btn" className="bg-[#6366f1] hover:bg-[#5558e3] text-white rounded-full px-12 py-6 text-lg glow-primary mt-8">
              Começar Gratuitamente
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-12">
        <div className="container mx-auto px-6 text-center text-gray-500">
          <p>&copy; 2025 ELION Market 360. Powered by AI.</p>
        </div>
      </footer>
    </div>
  );
}