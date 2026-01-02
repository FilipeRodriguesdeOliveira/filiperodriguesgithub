import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Brain, LayoutDashboard, Link as LinkIcon, Target, Database, Sparkles, BarChart3, LogOut, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Overview' },
    { path: '/dashboard/connections', icon: LinkIcon, label: 'Conexões' },
    { path: '/dashboard/platform-integrations', icon: Shield, label: 'Integrações OAuth' },
    { path: '/dashboard/goals', icon: Target, label: 'Objetivos' },
    { path: '/dashboard/data', icon: Database, label: 'Dados' },
    { path: '/dashboard/ai-brain', icon: Brain, label: 'IA Cérebro' },
    { path: '/dashboard/ai-specialists', icon: Sparkles, label: 'IAs Especialistas' },
    { path: '/dashboard/campaigns', icon: BarChart3, label: 'Campanhas' }
  ];

  return (
    <div className="min-h-screen bg-[#030712] flex">
      {/* Sidebar */}
      <aside className="w-64 glass-card border-r border-gray-800 flex flex-col">
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-8 h-8 text-[#6366f1]" />
            <span className="text-2xl font-bold gradient-text">ELION</span>
          </div>
          <p className="text-sm text-gray-400">{user?.name}</p>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                data-testid={`nav-${item.label.toLowerCase()}`}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-[#6366f1] text-white'
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <Button
            data-testid="logout-btn"
            onClick={handleLogout}
            variant="ghost"
            className="w-full justify-start text-gray-400 hover:text-white hover:bg-gray-800"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Sair
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}