import { User, Mail, MessageSquare, RefreshCw } from 'lucide-react';

interface Activity {
  id: string;
  user: string;
  action: string;
  target: string;
  time: string;
  icon: 'user' | 'mail' | 'chat';
}

const activities: Activity[] = [
  { id: '1', user: 'Alex M.', action: 'subscribed to', target: 'channel', time: 'Just now', icon: 'user' },
  { id: '2', user: 'Sarah K.', action: 'commented on', target: 'Shorts #42', time: '15 mins ago', icon: 'chat' },
  { id: '3', user: 'Mike R.', action: 'opened', target: 'Weekly Digest', time: '2 hours ago', icon: 'mail' },
];

export default function CdpActivityEnhanced() {
  const showEmpty = activities.length === 0;

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-bold text-gray-900">Live CDP Activity</h3>
          <p className="text-xs text-gray-500 mt-1">Real-time events</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
          </span>
          <span className="text-xs font-semibold text-green-600">Live</span>
        </div>
      </div>

      {showEmpty ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center py-8">
          <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
            <MessageSquare className="w-8 h-8 text-gray-400" />
          </div>
          <p className="text-sm font-medium text-gray-900 mb-1">No active events yet</p>
          <p className="text-xs text-gray-500 mb-4">Your CDP is waiting for the first customer interaction</p>
          <button className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-orange-600 bg-orange-50 hover:bg-orange-100 rounded-lg transition-colors border border-orange-200">
            <RefreshCw className="w-3 h-3" />
            Refresh
          </button>
        </div>
      ) : (
        <div className="space-y-6 flex-1 overflow-y-auto">
          {activities.map((item) => (
            <div key={item.id} className="flex gap-4 group">
              <div
                className={`mt-1 w-8 h-8 rounded-full flex items-center justify-center shrink-0 transition-transform group-hover:scale-110 ${
                  item.icon === 'user'
                    ? 'bg-blue-100 text-blue-600'
                    : item.icon === 'chat'
                      ? 'bg-orange-100 text-orange-600'
                      : 'bg-purple-100 text-purple-600'
                }`}
              >
                {item.icon === 'user' && <User className="w-4 h-4" />}
                {item.icon === 'chat' && <MessageSquare className="w-4 h-4" />}
                {item.icon === 'mail' && <Mail className="w-4 h-4" />}
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-900 group-hover:text-gray-700 transition-colors">
                  <span className="font-semibold text-gray-900">{item.user}</span> {item.action}{' '}
                  <span className="font-medium text-gray-700">{item.target}</span>
                </p>
                <p className="text-xs text-gray-400 mt-1 group-hover:text-gray-500 transition-colors">{item.time}</p>
              </div>
              <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                <button className="text-xs font-medium text-gray-500 hover:text-orange-600 transition-colors">View</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {!showEmpty && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <button className="text-xs font-medium text-orange-600 hover:text-orange-700 transition-colors">
            View all events
          </button>
        </div>
      )}
    </div>
  );
}
