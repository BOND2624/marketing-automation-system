import { LayoutDashboard, Zap, Home, Users, Video, Settings, LogOut, Plus, Upload } from 'lucide-react';

interface SidebarProps {
  activeMenu?: string;
  onMenuClick?: (menu: string) => void;
}

export default function Sidebar({ activeMenu = 'dashboard', onMenuClick }: SidebarProps) {
  const handleMenuClick = (menu: string) => {
    if (onMenuClick) {
      onMenuClick(menu);
    }
  };

  return (
    <aside className="w-64 bg-white border-r border-gray-200 h-screen flex flex-col">
      <div className="flex-1 py-6 overflow-y-auto">
        <div className="px-4 mb-6">
          <button
            onClick={() => handleMenuClick('dashboard')}
            className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm font-medium transition-colors ${activeMenu === 'dashboard'
              ? 'bg-orange-50 text-orange-600'
              : 'text-gray-600 hover:bg-gray-50'
              }`}
          >
            <LayoutDashboard className="w-5 h-5" />
            Dashboard
          </button>
        </div>

        <div className="px-4 mb-6 pb-6 border-b border-gray-100">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Main</p>
          <div className="space-y-1">
            <button
              onClick={() => handleMenuClick('home')}
              className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm transition-colors ${activeMenu === 'home'
                ? 'bg-orange-50 text-orange-600 font-medium'
                : 'text-gray-700 hover:bg-gray-50'
                }`}
            >
              <Home className="w-4 h-4" />
              Home
            </button>

            <button
              onClick={() => handleMenuClick('customer-cdp')}
              className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm transition-colors ${activeMenu === 'customer-cdp'
                ? 'bg-orange-50 text-orange-600 font-medium'
                : 'text-gray-600 hover:bg-gray-50'
                }`}
            >
              <Users className="w-4 h-4" />
              Customer CDP
            </button>

            <button
              onClick={() => handleMenuClick('video-performance')}
              className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm transition-colors ${activeMenu === 'video-performance'
                ? 'bg-orange-50 text-orange-600 font-medium'
                : 'text-gray-600 hover:bg-gray-50'
                }`}
            >
              <Video className="w-4 h-4" />
              Video Performance
            </button>

            <button
              onClick={() => handleMenuClick('uploads')}
              className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm transition-colors ${activeMenu === 'uploads'
                ? 'bg-orange-50 text-orange-600 font-medium'
                : 'text-gray-700 hover:bg-gray-50'
                }`}
            >
              <Upload className="w-4 h-4" />
              Media Command
            </button>
          </div>
        </div>

        <div className="px-4 mb-6 pb-6 border-b border-gray-100">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Automation</p>
          <div className="space-y-1">
            <button
              onClick={() => handleMenuClick('integration')}
              className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm transition-colors ${activeMenu === 'integration'
                ? 'bg-orange-50 text-orange-600 font-medium'
                : 'text-gray-600 hover:bg-gray-50'
                }`}
            >
              <Zap className={`w-4 h-4 ${activeMenu === 'integration' ? 'text-orange-600' : 'text-orange-500'}`} />
              Integration Status
            </button>
          </div>
        </div>

        <div className="px-4 pb-6 border-b border-gray-100">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">System</p>
          <div className="space-y-1">
            <button
              onClick={() => handleMenuClick('settings')}
              className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg text-sm transition-colors ${activeMenu === 'settings'
                ? 'bg-orange-50 text-orange-600 font-medium'
                : 'text-gray-600 hover:bg-gray-50'
                }`}
            >
              <Settings className="w-4 h-4" />
              Settings
            </button>
          </div>
        </div>
      </div>

      <div className="px-4 py-4 border-t border-gray-200">
        <button
          onClick={() => handleMenuClick('logout')}
          className="flex items-center gap-3 w-full px-3 py-2 text-gray-600 hover:bg-gray-50 rounded-lg text-sm transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Log out
        </button>
      </div>
    </aside>
  );
}
