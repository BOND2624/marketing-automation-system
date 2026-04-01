import React from 'react';
import { Lock } from 'lucide-react';

interface ApiGapOverlayProps {
    children: React.ReactNode;
}

export default function ApiGapOverlay({ children }: ApiGapOverlayProps) {
    return (
        <div className="relative group overflow-hidden rounded-xl">
            <div className="opacity-50 blur-[2px] transition-all duration-300 group-hover:blur-[4px] select-none pointer-events-none">
                {children}
            </div>
            <div className="absolute inset-0 z-10 flex items-center justify-center bg-gray-50/10 backdrop-blur-[1px] group-hover:bg-gray-50/20 transition-all">
                <div className="bg-white/90 shadow-sm border border-gray-200 px-3 py-1.5 rounded-full flex items-center gap-2 transform translate-y-1 group-hover:translate-y-0 transition-transform">
                    <Lock className="w-3 h-3 text-gray-500" />
                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-600">
                        Analytics API Required
                    </span>
                </div>
            </div>
        </div>
    );
}
