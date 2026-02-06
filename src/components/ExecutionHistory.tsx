import { Play, CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react';

interface Campaign {
  id: string;
  name: string;
  status: 'completed' | 'failed' | 'running' | 'pending';
  time: string;
  priority?: 'high' | 'normal';
}

const campaigns: Campaign[] = [
  { id: '1', name: 'Q4 Campaign Launch', status: 'completed', time: '2 mins ago' },
  { id: '2', name: 'Email Sequence #12', status: 'running', time: '15 mins ago', priority: 'high' },
  { id: '3', name: 'Weekly Digest Send', status: 'completed', time: '1 hour ago' },
  { id: '4', name: 'Failed Sync Retry', status: 'failed', time: '2 hours ago', priority: 'high' },
  { id: '5', name: 'Audience Segment Update', status: 'pending', time: '3 hours ago' },
];

export default function ExecutionHistoryEnhanced() {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'running':
        return <Play className="w-5 h-5 text-blue-600 animate-pulse" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50';
      case 'running':
        return 'bg-blue-50 border-blue-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100 flex flex-col h-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-bold text-gray-900">Recent Executions</h3>
          <p className="text-xs text-gray-500 mt-1">Live Status</p>
        </div>
        <button className="text-xs text-gray-500 hover:text-gray-700 font-medium transition-colors">See All</button>
      </div>

      <div className="space-y-2 flex-1 overflow-y-auto">
        {campaigns.map((campaign) => (
          <div
            key={campaign.id}
            className={`flex items-center gap-3 p-3 rounded-lg border transition-all group hover:shadow-sm ${getStatusColor(
              campaign.status,
            )}`}
          >
            <div className="shrink-0">{getStatusIcon(campaign.status)}</div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{campaign.name}</p>
              <div className="flex items-center gap-2 mt-0.5">
                <p className="text-xs text-gray-500">{campaign.time}</p>
                {campaign.priority === 'high' && (
                  <div className="flex items-center gap-1 px-1.5 py-0.5 bg-red-100 rounded-full">
                    <AlertCircle className="w-2.5 h-2.5 text-red-600" />
                    <span className="text-xs font-semibold text-red-600">Urgent</span>
                  </div>
                )}
              </div>
            </div>

            <button className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-xs font-medium text-gray-500 hover:text-orange-600 px-2 py-1 rounded-lg hover:bg-gray-100">
              Details
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
