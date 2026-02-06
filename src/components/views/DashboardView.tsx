'use client';

import { Users, Eye, PlayCircle, Activity } from 'lucide-react';
import StatCard from '@/components/StatCard';
import ExecutionHistory from '@/components/ExecutionHistory';
import EngagementChart from '@/components/EngagementChart';
import UploadQueue from '@/components/UploadQueue';
import QuotaMonitor from '@/components/QuotaMonitor';
import CdpActivity from '@/components/CdpActivity';
import SystemHealth from '@/components/SystemHealth';

interface DashboardViewProps {
    stats: any;
    systemStatus: any;
}

export default function DashboardView({ stats, systemStatus }: DashboardViewProps) {
    return (
        <div className="animate-in fade-in duration-700">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-black text-gray-900 tracking-tight">
                        Unified Marketing Command
                    </h1>
                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">
                        System Hub & Automation Control
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg shadow-sm flex items-center gap-2">
                        <Activity className="w-4 h-4 text-orange-500" />
                        <span className="text-[10px] font-black uppercase text-gray-600">v2.4.0 Active</span>
                    </div>
                </div>
            </div>

            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <StatCard
                    title="Audience Reach"
                    value={stats?.subscriber_count?.toLocaleString() || '---'}
                    change="+12.4%"
                    changeLabel="Growth Trend"
                    icon={<Users className="w-6 h-6 text-orange-600" />}
                    iconBg="bg-orange-50"
                />
                <StatCard
                    title="Visual Impact"
                    value={stats?.view_count?.toLocaleString() || '---'}
                    change="+8.2%"
                    changeLabel="Global Views"
                    icon={<Eye className="w-6 h-6 text-green-600" />}
                    iconBg="bg-green-50"
                />
                <StatCard
                    title="Campaign Velocity"
                    value="12"
                    change="24h"
                    changeLabel="Active Loops"
                    icon={<PlayCircle className="w-6 h-6 text-blue-600" />}
                    iconBg="bg-blue-50"
                />
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
                <div className="flex flex-col h-full">
                    <ExecutionHistory />
                </div>
                <div className="flex flex-col h-full">
                    <EngagementChart />
                </div>
            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pb-8">
                <QuotaMonitor />
                <CdpActivity />
                <SystemHealth status={systemStatus} />
            </div>
        </div>
    );
}
