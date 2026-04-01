import { useState, useEffect, useRef } from 'react';
import { Play, CheckCircle, UploadCloud, Eye, Trash2, AlertCircle, X, Loader2 } from 'lucide-react';
import { uploadsApi, youtubeApi } from '@/services/api';
import MetadataEditor from './MetadataEditor';

interface VideoItem {
  filename: string;
  size_mb: number;
  status: 'ready' | 'uploading' | 'publishing' | 'done' | 'failed';
  progress?: number;
  task_id?: string;
  error?: string;
  thumbnail?: string;
}

interface UploadQueueProps {
  videos: VideoItem[];
  setVideos: React.Dispatch<React.SetStateAction<VideoItem[]>>;
  ytAuthValid: boolean | null;
}

export default function UploadQueue({ videos, setVideos, ytAuthValid }: UploadQueueProps) {
  const [selectedVideos, setSelectedVideos] = useState<string[]>([]);
  const [showMetadataEditor, setShowMetadataEditor] = useState(false);
  const [editingVideo, setEditingVideo] = useState<VideoItem | null>(null);
  const [currentMetadata, setCurrentMetadata] = useState<any>(null);
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' } | null>(null);
  const [isBatchMode, setIsBatchMode] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const updateVideoStatus = (filename: string, updates: Partial<VideoItem>) => {
    setVideos(prev => prev.map(v => v.filename === filename ? { ...v, ...updates } : v));
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validation
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['mp4', 'mov'].includes(ext || '')) {
      showToast('Only .mp4 and .mov formats are supported', 'error');
      return;
    }

    // Optimistic UI
    const newVideo: VideoItem = {
      filename: file.name,
      size_mb: Math.round(file.size / (1024 * 1024)),
      status: 'uploading',
      progress: 0,
      thumbnail: URL.createObjectURL(file) // Local preview
    };
    setVideos(prev => [newVideo, ...prev]);

    try {
      await uploadsApi.upload(file, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total || file.size));
        updateVideoStatus(file.name, { progress: percent });
      });
      updateVideoStatus(file.name, { status: 'ready', progress: undefined });
      showToast('File uploaded successfully', 'success');
    } catch (error) {
      console.error('Upload failed:', error);
      updateVideoStatus(file.name, { status: 'failed', error: 'Server upload failed' });
      showToast('Upload failed', 'error');
    }
  };

  const handlePublishClick = (video: VideoItem) => {
    if (!ytAuthValid) {
      showToast('Action Required: Connect YouTube channel in Settings', 'error');
      return;
    }
    setEditingVideo(video);
    setCurrentMetadata({
      title: video.filename.replace(/\.[^/.]+$/, ""),
      description: "Uploaded via Unified Marketing Command",
      visibility: 'public'
    });
    setShowMetadataEditor(true);
  };

  const handleApplyMetadata = (data: any) => {
    setCurrentMetadata(data);
    if (!editingVideo) return;
    startPublishing(editingVideo.filename, data);
    setShowMetadataEditor(false);
  };

  const startPublishing = async (filename: string, metadata: any) => {
    updateVideoStatus(filename, { status: 'publishing' });

    try {
      const res = await uploadsApi.publish(filename, {
        ...metadata,
        upload_type: metadata.isShort ? 'short' : 'video'
      });
      updateVideoStatus(filename, { task_id: res.data.task_id });
    } catch (error: any) {
      updateVideoStatus(filename, { status: 'failed', error: error.response?.data?.detail || 'Publishing failed' });
    }
  };

  const handleBatchPublish = async () => {
    if (selectedVideos.length === 0) return;
    
    setToast({ message: `Publishing ${selectedVideos.length} videos...`, type: 'success' });
    
    const batchData = selectedVideos.map(filename => ({
        filename,
        metadata: {
            title: filename.replace(/\.[^/.]+$/, ""),
            description: "Batch Upload via Unified Marketing Command",
            visibility: 'public'
        }
    }));

    try {
        const res = await uploadsApi.publishBatch(batchData);
        res.data.tasks.forEach((t: any) => {
            updateVideoStatus(t.filename, { status: 'publishing', task_id: t.task_id });
        });
        setSelectedVideos([]);
        setIsBatchMode(false);
    } catch (err) {
        showToast('Batch publish failed', 'error');
    }
  };

  const showToast = (message: string, type: 'error' | 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const toggleSelect = (id: string) => {
    setSelectedVideos(prev =>
      prev.includes(id) ? prev.filter(v => v !== id) : [...prev, id]
    );
  };

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100 flex flex-col h-full min-h-[500px] shadow-sm relative">
      {/* Toast Notification */}
      {toast && (
        <div className={`absolute top-4 right-4 z-50 animate-in fade-in slide-in-from-top-4 px-4 py-3 rounded-lg shadow-xl flex items-center gap-3 border ${toast.type === 'error' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-green-50 border-green-200 text-green-700'
          }`}>
          {toast.type === 'error' ? <AlertCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
          <span className="text-sm font-bold">{toast.message}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-bold text-gray-900 border-l-4 border-orange-500 pl-3 uppercase tracking-tighter">Upload Queue</h3>
          <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mt-1 ml-3">
            {videos.length} Identified Assets
          </p>
        </div>
        <div className="flex gap-2">
          {selectedVideos.length > 0 ? (
            <button
                onClick={handleBatchPublish}
                className="px-4 py-2 text-xs font-black bg-orange-600 text-white rounded-xl hover:bg-orange-700 transition-all shadow-lg shadow-orange-500/20 flex items-center gap-2 animate-in slide-in-from-right-2"
            >
                <Play className="w-3.5 h-3.5 fill-white" />
                Publish Selected ({selectedVideos.length})
            </button>
          ) : (
            <button
                onClick={() => setIsBatchMode(!isBatchMode)}
                className={`px-4 py-2 text-xs font-black rounded-xl transition-all border flex items-center gap-2 ${
                    isBatchMode ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                }`}
            >
                {isBatchMode ? 'Cancel Selection' : 'Batch mode'}
            </button>
          )}

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".mp4,.mov"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2 text-xs font-bold bg-gray-50 text-gray-900 border border-gray-200 rounded-xl hover:bg-gray-100 transition-all shadow-sm flex items-center gap-2"
          >
            <UploadCloud className="w-4 h-4" />
            Upload
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 gap-4 flex-1 overflow-y-auto pr-1">
        {videos.map((video) => (
          <div
            key={video.filename}
            onClick={() => isBatchMode && toggleSelect(video.filename)}
            className={`group relative overflow-hidden rounded-2xl border transition-all duration-300 ${
                video.status === 'uploading' ? 'opacity-70' : ''
            } ${
                selectedVideos.includes(video.filename) 
                ? 'border-orange-500 ring-2 ring-orange-500/20 shadow-lg' 
                : 'border-gray-100 hover:border-orange-200 hover:shadow-md'
            } ${isBatchMode ? 'cursor-pointer' : ''}`}
          >
            <div className="relative aspect-video bg-gray-100 overflow-hidden">
               {isBatchMode && (
                <div className={`absolute top-3 left-3 z-20 w-5 h-5 rounded-md border-2 transition-all flex items-center justify-center ${
                    selectedVideos.includes(video.filename) ? 'bg-orange-500 border-orange-500' : 'bg-white/50 border-white shadow-sm'
                }`}>
                    {selectedVideos.includes(video.filename) && <CheckCircle className="w-4 h-4 text-white" />}
                </div>
               )}

              <img
                src={video.thumbnail || 'https://images.pexels.com/photos/3568520/pexels-photo-3568520.jpeg?auto=compress&cs=tinysrgb&w=200'}
                alt={video.filename}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
              />

              {/* Progress/Status Overlays */}
              <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors" />

              {video.status === 'uploading' && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 backdrop-blur-sm px-6">
                  <div className="w-full bg-white/20 h-1.5 rounded-full overflow-hidden mb-3">
                    <div
                      className="bg-orange-500 h-full transition-all duration-300"
                      style={{ width: `${video.progress}%` }}
                    />
                  </div>
                  <span className="text-white text-[10px] font-black uppercase tracking-widest">{video.progress}% Uploading</span>
                </div>
              )}

              {video.status === 'publishing' && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-orange-600/60 backdrop-blur-sm animate-pulse">
                  <Loader2 className="w-8 h-8 text-white animate-spin mb-2" />
                  <span className="text-white text-[10px] font-black uppercase tracking-widest">In Queue</span>
                </div>
              )}

              {video.status === 'done' && (
                <div className="absolute top-3 right-3 z-10">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center shadow-lg border-2 border-white">
                    <CheckCircle className="w-5 h-5 text-white" />
                  </div>
                </div>
              )}

              {video.status === 'failed' && (
                <div className="absolute top-3 right-3 z-10" title={video.error}>
                  <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center shadow-lg border-2 border-white">
                    <AlertCircle className="w-5 h-5 text-white" />
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 bg-white">
              <h4 className="text-[13px] font-bold text-gray-900 truncate">
                {video.filename}
              </h4>
              <div className="flex items-center justify-between mt-3">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-tight">{video.size_mb} MB</p>
                <div className="flex items-center gap-1">
                  {video.status === 'done' ? (
                    <span className="text-[10px] font-black uppercase text-green-600 bg-green-50 px-2 py-0.5 rounded-md border border-green-100">
                      Published
                    </span>
                  ) : video.status === 'publishing' ? (
                    <span className="text-[10px] font-black uppercase text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-100 flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                      Sending to YT
                    </span>
                  ) : video.status === 'failed' ? (
                    <button
                      onClick={() => handlePublishClick(video)}
                      className="text-[10px] font-black uppercase text-red-600 bg-red-50 px-2.5 py-1 rounded-md hover:bg-red-600 hover:text-white transition-all border border-red-100"
                    >
                      Retry
                    </button>
                  ) : (
                    <button
                      disabled={video.status === 'uploading'}
                      onClick={() => handlePublishClick(video)}
                      className="text-[10px] font-black uppercase text-orange-600 bg-orange-50 px-2.5 py-1 rounded-md hover:bg-orange-600 hover:text-white transition-all border border-orange-100 disabled:opacity-50"
                    >
                      Publish
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {videos.length === 0 && (
          <div className="col-span-2 flex flex-col items-center justify-center py-20 text-center bg-gray-50/50 rounded-2xl border-2 border-dashed border-gray-100">
            <UploadCloud className="w-10 h-10 text-orange-200 mb-4" />
            <p className="text-sm font-bold text-gray-900 mb-1">Queue is Clear</p>
            <p className="text-xs text-gray-500">Import your assets to begin the sequence.</p>
          </div>
        )}
      </div>

      {/* Metadata Editor Side Panel */}
      {showMetadataEditor && editingVideo && currentMetadata && (
        <MetadataEditor
          filename={editingVideo.filename}
          initialData={currentMetadata}
          onSave={handleApplyMetadata}
          onClose={() => setShowMetadataEditor(false)}
        />
      )}
    </div>
  );
}
