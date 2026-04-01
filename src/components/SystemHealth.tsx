import { Database, Server, Youtube, CheckCircle2, XCircle } from 'lucide-react';

export default function SystemHealth({ status }: { status: any }) {
    const getStatusInfo = (svc: string, defaultSublabel: string) => {
        const val = status?.[svc];
        if (val === undefined || val === null) return { state: 'loading', text: 'Checking...' };
        if (val === 'online' || val === 'active' || val === true || val === 'Valid') {
            return { state: 'success', text: defaultSublabel || 'Active' };
        }
        if (val === 'Disconnected') {
            return { state: 'warning', text: 'Disconnected' };
        }
        return { state: 'error', text: 'Error' };
    };

    const StatusRow = ({ icon: Icon, label, svc, sublabel }: any) => {
        const info = getStatusInfo(svc, sublabel);
        
        const dotColors = {
            success: 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]',
            warning: 'bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.6)]',
            error: 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]',
            loading: 'bg-gray-500 animate-pulse'
        };
        
        const textColors = {
            success: 'text-green-400',
            warning: 'text-orange-400',
            error: 'text-red-400',
            loading: 'text-gray-400'
        };

        return (
            <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg border border-gray-700">
                <div className="flex items-center gap-3">
                    <Icon className={`w-5 h-5 ${
                        svc === 'youtube' ? 'text-red-500' : 
                        svc === 'database' ? 'text-blue-400' : 'text-orange-400'
                    }`} />
                    <span className="text-sm font-medium">{label}</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${dotColors[info.state as keyof typeof dotColors]}`} />
                    <span className={`text-xs ${textColors[info.state as keyof typeof textColors]}`}>{info.text}</span>
                </div>
            </div>
        );
    };

    return (
        <div className="bg-gray-900 rounded-xl p-6 text-white h-full">
            <div className="mb-6">
                <h3 className="font-bold text-lg">System Health</h3>
                <p className="text-gray-400 text-sm">Real-time status checks</p>
            </div>

            <div className="space-y-4">
                <StatusRow icon={Database} label="PostgreSQL" svc="database" sublabel="Connected" />
                <StatusRow icon={Server} label="Redis Worker" svc="celery" sublabel="Active" />
                <StatusRow icon={Youtube} label="YouTube Auth" svc="youtube" sublabel="Valid" />
            </div>
        </div>
    );
}
