'use client';

import { Zap, TrendingUp, AlertTriangle, CheckCircle, Video } from 'lucide-react';

interface Insight {
  type: 'success' | 'warning' | 'info';
  title: string;
  description: string;
}

interface QuickInsightsProps {
    data?: any;
}

export default function QuickInsights({ data }: QuickInsightsProps) {
  const insights: Insight[] = [
    {
      type: 'success',
      title: 'Growth Spike',
      description: 'Global reach increased by 12% across all platforms this week.',
    },
    {
      type: 'info',
      title: 'Audience Peak',
      description: 'Engagement is highest between 6 PM - 9 PM across connected channels.',
    }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Top Video Card */}
      <div className="lg:col-span-2 bg-gradient-to-br from-gray-900 to-black rounded-2xl p-6 border border-gray-800 relative overflow-hidden group shadow-2xl">
        <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
            <Video className="w-32 h-32 text-orange-500 -rotate-12" />
        </div>
        
        <div className="relative z-10 flex flex-col h-full">
            <div className="flex items-center gap-2 mb-4">
                <div className="px-2 py-0.5 bg-orange-500 rounded text-[10px] font-black uppercase text-white shadow-lg shadow-orange-500/20">
                    Highest Impact
                </div>
                <span className="text-[10px] font-black uppercase text-gray-500 tracking-widest">Live Metadata</span>
            </div>
            
            <h4 className="text-xl font-black text-white mb-2 group-hover:text-orange-400 transition-colors">
                {data?.top_video?.title || "No Video Data Available"}
            </h4>
            
            <div className="flex items-center gap-6 mt-auto">
                <div>
                    <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Views</p>
                    <p className="text-lg font-black text-white">{(data?.top_video?.views || 0).toLocaleString()}</p>
                </div>
                <div>
                    <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Engagement</p>
                    <p className="text-lg font-black text-orange-500">{data?.top_video?.engagement || "0.0%"}</p>
                </div>
                <div>
                    <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-1">Status</p>
                    <p className="text-lg font-black text-white">Active</p>
                </div>
            </div>
        </div>
      </div>

      {/* AI Insights List */}
      <div className="bg-white rounded-2xl p-6 border border-gray-100 flex flex-col">
        <div className="flex items-center gap-2 mb-6">
            < Zap className="w-4 h-4 text-orange-500 fill-orange-500" />
            <h4 className="text-sm font-black text-gray-900 uppercase tracking-tight">Channel Insights</h4>
        </div>
        
        <div className="space-y-4 flex-1">
            {insights.map((insight, i) => (
                <div key={i} className="flex gap-4 group">
                    <div className="shrink-0 mt-1">
                        {insight.type === 'success' && <CheckCircle className="w-4 h-4 text-green-500" />}
                        {insight.type === 'info' && <TrendingUp className="w-4 h-4 text-blue-500" />}
                    </div>
                    <div>
                        <p className="text-xs font-black text-gray-900 group-hover:text-orange-600 transition-colors">{insight.title}</p>
                        <p className="text-[10px] leading-relaxed text-gray-500 mt-1">{insight.description}</p>
                    </div>
                </div>
            ))}
        </div>
      </div>
    </div>
  );
}
