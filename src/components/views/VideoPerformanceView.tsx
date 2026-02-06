'use client';

import { Eye, Activity, Zap, Users, Heart, MessageSquare, Share2 } from 'lucide-react';
import StatCard from '@/components/StatCard';
import EngagementChart from '@/components/EngagementChart';

export default function VideoPerformanceView() {
    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-gray-900 tracking-tight">Content Analytics</h1>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">High-Impact Performance Metrics</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <StatCard title="Total Views" value="1.2M" change="+8%" changeLabel="vs Previous" icon={<Eye className="w-5 h-5 text-green-600" />} iconBg="bg-green-50" />
                <StatCard title="Avg. Watch Time" value="4:32" change="+45s" changeLabel="Retention" icon={<Activity className="w-5 h-5 text-blue-600" />} iconBg="bg-blue-50" />
                <StatCard title="CTR (Click-Thru)" value="12.4%" change="+2.1%" changeLabel="CTR Trend" icon={<Zap className="w-5 h-5 text-yellow-600" />} iconBg="bg-yellow-50" />
                <StatCard title="Brand Subs" value="2.8K" change="+320" changeLabel="Conversion" icon={<Users className="w-5 h-5 text-orange-600" />} iconBg="bg-orange-50" />
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
                <div className="xl:col-span-2 h-[450px]">
                    <EngagementChart />
                </div>
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm flex flex-col h-[450px]">
                    <h3 className="text-sm font-black uppercase text-gray-900 tracking-tight mb-6">Engagement Split</h3>
                    <div className="flex-1 space-y-8 py-4">
                        {[
                            { label: 'Likes', count: '24.5K', percent: 80, color: 'bg-red-500', icon: <Heart className="w-4 h-4 text-red-500" /> },
                            { label: 'Comments', count: '8.3K', percent: 35, color: 'bg-blue-500', icon: <MessageSquare className="w-4 h-4 text-blue-500" /> },
                            { label: 'Shares', count: '3.2K', percent: 15, color: 'bg-green-500', icon: <Share2 className="w-4 h-4 text-green-500" /> }
                        ].map((stat, i) => (
                            <div key={i} className="space-y-2">
                                <div className="flex justify-between items-end">
                                    <div className="flex items-center gap-2">
                                        {stat.icon}
                                        <div>
                                            <p className="text-[10px] font-black uppercase text-gray-400 leading-none">{stat.label}</p>
                                            <p className="text-lg font-black text-gray-900 leading-tight">{stat.count}</p>
                                        </div>
                                    </div>
                                </div>
                                <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                    <div className={`h-full ${stat.color} rounded-full`} style={{ width: `${stat.percent}%` }}></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
