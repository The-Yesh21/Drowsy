import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { Activity, BarChart2, LogOut, User } from 'lucide-react';

const Navbar = () => {
  const { driver, logout } = useAuthStore();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-slate-800 border-b border-slate-700">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center gap-2">
              <Activity className="h-8 w-8 text-blue-500" />
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">
                SafeDrive AI
              </span>
            </div>
            <div className="hidden md:block ml-10">
              <div className="flex items-baseline space-x-4">
                <Link
                  to="/dashboard"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive('/dashboard')
                      ? 'bg-slate-900 text-white'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    Live Dashboard
                  </div>
                </Link>
                <Link
                  to="/analytics"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive('/analytics')
                      ? 'bg-slate-900 text-white'
                      : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <BarChart2 className="w-4 h-4" />
                    Analytics
                  </div>
                </Link>
              </div>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="ml-4 flex items-center md:ml-6 gap-4">
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <User className="w-4 h-4" />
                <span>{driver?.name || 'Driver'}</span>
              </div>
              <button
                onClick={logout}
                className="flex items-center gap-2 p-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-700 focus:outline-none transition-colors"
                title="Sign out"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
