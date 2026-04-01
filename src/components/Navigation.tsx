import { useState } from 'react';
import { Search, Bell, HelpCircle, ChevronDown, WifiOff, Upload } from 'lucide-react';
import { SignedIn, UserButton } from "@clerk/nextjs";
import UploadModal from '@/components/UploadModal';

interface NavigationProps {
  isOffline?: boolean;
  onUploadSuccess?: (video: any) => void;
}

export default function Navigation({ isOffline, onUploadSuccess }: NavigationProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-orange-600 rounded-lg flex items-center justify-center">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2c.46-1.7.46-5.33.46-5.33a29 29 0 0 0-.46-5.33z" />
                <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02" fill="white" />
              </svg>
            </div>
            <span className="text-lg font-semibold flex items-center gap-3">
              <span className="font-bold">Unified Marketing</span>
              {isOffline && (
                <span className="flex items-center gap-1.5 px-2 py-0.5 bg-orange-100 text-orange-600 text-[10px] font-black uppercase rounded-full border border-orange-200">
                  <WifiOff className="w-3 h-3" />
                  Cloud Sync Paused
                </span>
              )}
            </span>
          </div>

          <div className="flex items-center gap-6 text-sm">
            <a href="#" className="text-gray-900 font-medium hover:text-orange-600 transition-colors">Home</a>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 px-3 py-2 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center gap-1.5">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-600"></span>
              </span>
              <span className="text-xs font-semibold text-green-700">3 Workers</span>
            </div>
          </div>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search Customer Database..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm w-64 focus:outline-none focus:ring-2 focus:ring-orange-200 focus:border-orange-300 transition-all"
            />
          </div>

          <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
            Current Month
            <ChevronDown className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsUploadModalOpen(true)}
            className="flex items-center gap-2 px-3 py-2 bg-orange-600 text-white text-sm font-bold rounded-lg hover:bg-orange-700 transition-colors shadow-lg shadow-orange-600/20"
          >
            <Upload className="w-4 h-4" />
            Upload Video
          </button>

          <button className="p-2 hover:bg-gray-50 rounded-lg relative transition-colors">
            <Bell className="w-5 h-5 text-gray-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          <button className="p-2 hover:bg-gray-50 rounded-lg transition-colors">
            <HelpCircle className="w-5 h-5 text-gray-600" />
          </button>

          <SignedIn>
            <div className="pl-2 border-l border-gray-200">
              <UserButton appearance={{ elements: { userButtonAvatarBox: "w-8 h-8" } }} />
            </div>
          </SignedIn>
        </div>
      </div>

      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadSuccess={(video) => {
          onUploadSuccess?.(video);
        }}
      />
    </nav>
  );
}
