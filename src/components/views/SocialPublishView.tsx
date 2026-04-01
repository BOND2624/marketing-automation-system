import React, { useState, useEffect, useCallback } from 'react';
import {
  Share2,
  Image as ImageIcon,
  Video,
  Send,
  Loader2,
  Facebook,
  Instagram,
  Youtube,
  AlertCircle,
  CheckCircle2,
  Upload,
  Sparkles,
  X,
} from 'lucide-react';
import { uploadsApi, publishApi } from '@/services/api';

interface PublishResult {
  success: boolean;
  message: string;
  post_id?: string;
  video_id?: string;
}

type Platform = 'facebook' | 'instagram' | 'youtube';
type YoutubeFormat = 'short' | 'video';

type MediaValidation =
  | { status: 'idle' }
  | { status: 'checking' }
  | { status: 'ok'; message: string }
  | { status: 'error'; message: string };

type AiTone = 'casual' | 'professional' | 'fun';

interface AiReviewDraft {
  title: string;
  body: string;
  tagsLine: string;
  hashtagsLine: string;
}

const SHORT_MAX_SEC = 60;
const ASPECT_9_16 = 9 / 16;
const ASPECT_TOLERANCE = 0.12;
const REG_MAX_SEC = 12 * 60 * 60;

function probeVideoMetadata(file: File): Promise<{ duration: number; width: number; height: number }> {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const video = document.createElement('video');
    video.preload = 'metadata';
    const cleanup = () => URL.revokeObjectURL(url);
    video.onloadedmetadata = () => {
      const meta = {
        duration: Number.isFinite(video.duration) ? video.duration : 0,
        width: video.videoWidth,
        height: video.videoHeight,
      };
      cleanup();
      resolve(meta);
    };
    video.onerror = () => {
      cleanup();
      reject(new Error('Could not read video file'));
    };
    video.src = url;
  });
}

function validateYoutubeShort(
  duration: number,
  width: number,
  height: number
): { ok: boolean; message: string } {
  if (!duration || duration > SHORT_MAX_SEC) {
    return {
      ok: false,
      message: `Shorts must be ${SHORT_MAX_SEC}s or less (got ${duration.toFixed(1)}s).`,
    };
  }
  if (height <= 0 || width <= 0) {
    return { ok: false, message: 'Could not read video dimensions.' };
  }
  if (width >= height) {
    return { ok: false, message: 'Shorts must be vertical (height greater than width).' };
  }
  const r = width / height;
  if (Math.abs(r - ASPECT_9_16) > ASPECT_TOLERANCE) {
    return {
      ok: false,
      message: `Aspect ratio should be about 9:16 (current ~${r.toFixed(2)}:1).`,
    };
  }
  return { ok: true, message: 'Short requirements met.' };
}

function validateYoutubeVideo(
  duration: number,
  width: number,
  height: number
): { ok: boolean; message: string } {
  if (!duration || duration <= 0) {
    return { ok: false, message: 'Video must have a duration greater than zero.' };
  }
  if (duration > REG_MAX_SEC) {
    return { ok: false, message: 'Video exceeds 12 hour maximum.' };
  }
  if (width < 256 || height < 144) {
    return {
      ok: false,
      message: `Resolution ${width}x${height} is below minimum (~256x144).`,
    };
  }
  return { ok: true, message: 'Standard video requirements met.' };
}

export default function SocialPublishView() {
  const [platform, setPlatform] = useState<Platform>('facebook');
  const [content, setContent] = useState('');
  const [mediaUrl, setMediaUrl] = useState('');
  const [mediaType, setMediaType] = useState<'IMAGE' | 'REELS'>('IMAGE');
  const [youtubeFormat, setYoutubeFormat] = useState<YoutubeFormat>('video');
  const [youtubeTitle, setYoutubeTitle] = useState('');
  const [youtubeTags, setYoutubeTags] = useState('');
  const [aiTone, setAiTone] = useState<AiTone>('casual');
  const [aiPanelOpen, setAiPanelOpen] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiReview, setAiReview] = useState<AiReviewDraft | null>(null);
  const [isPublishing, setIsPublishing] = useState(false);
  const [result, setResult] = useState<PublishResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [mediaValidation, setMediaValidation] = useState<MediaValidation>({ status: 'idle' });

  const revokePreview = useCallback((url: string | null) => {
    if (url && url.startsWith('blob:')) {
      URL.revokeObjectURL(url);
    }
  }, []);

  const runYoutubeValidation = useCallback(
    async (file: File | null, format: YoutubeFormat) => {
      if (!file) {
        setMediaValidation({ status: 'idle' });
        return;
      }
      if (!file.type.startsWith('video/')) {
        setMediaValidation({
          status: 'error',
          message: 'YouTube uploads require a video file (not an image).',
        });
        return;
      }
      setMediaValidation({ status: 'checking' });
      try {
        const { duration, width, height } = await probeVideoMetadata(file);
        const check =
          format === 'short'
            ? validateYoutubeShort(duration, width, height)
            : validateYoutubeVideo(duration, width, height);
        if (check.ok) {
          setMediaValidation({ status: 'ok', message: check.message });
        } else {
          setMediaValidation({ status: 'error', message: check.message });
        }
      } catch {
        setMediaValidation({
          status: 'error',
          message: 'Could not read this video. Try another file or format (e.g. MP4).',
        });
      }
    },
    []
  );

  useEffect(() => {
    if (platform !== 'youtube') {
      setMediaValidation({ status: 'idle' });
      return;
    }
    runYoutubeValidation(selectedFile, youtubeFormat);
  }, [platform, selectedFile, youtubeFormat, runYoutubeValidation]);

  useEffect(() => {
    return () => revokePreview(previewUrl);
  }, [previewUrl, revokePreview]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      revokePreview(previewUrl);
      setSelectedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      if (platform === 'youtube') {
        setMediaUrl('');
      } else {
        setMediaUrl(file.name);
      }

      const ext = file.name.split('.').pop()?.toLowerCase();
      if (['mp4', 'mov'].includes(ext || '')) {
        setMediaType('REELS');
      } else {
        setMediaType('IMAGE');
      }
    }
  };

  const buildUserInputForAi = useCallback(() => {
    const parts: string[] = [];
    if (platform === 'youtube' && youtubeTitle.trim()) {
      parts.push(youtubeTitle.trim());
    }
    if (content.trim()) {
      parts.push(content.trim());
    }
    return parts.join('\n\n');
  }, [platform, youtubeTitle, content]);

  const handleGenerateAi = async () => {
    const seed = buildUserInputForAi().trim();
    if (!seed) {
      setAiError('Add a title, caption, or description first so the AI has something to work from.');
      setAiReview(null);
      setAiPanelOpen(true);
      return;
    }
    setAiLoading(true);
    setAiError(null);
    setAiReview(null);
    setAiPanelOpen(true);
    try {
      const { data } = await publishApi.personalize({
        user_input: seed,
        platform,
        tone: aiTone,
      });
      setAiReview({
        title: data.title || '',
        body: data.body || data.description || '',
        tagsLine: (data.tags || []).join(', '),
        hashtagsLine: (data.hashtags || []).join(' '),
      });
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } }; message?: string };
      setAiError(
        err.response?.data?.detail ||
          err.message ||
          'Could not reach the AI service. Is Ollama running?'
      );
      setAiReview(null);
    } finally {
      setAiLoading(false);
    }
  };

  const applyAiToForm = () => {
    if (!aiReview) return;
    if (platform === 'youtube') {
      setYoutubeTitle(aiReview.title);
      setContent(aiReview.body);
      setYoutubeTags(aiReview.tagsLine);
    } else {
      let body = aiReview.body.trim();
      const extraTags = aiReview.hashtagsLine.trim();
      if (extraTags && !body.includes('#')) {
        body = `${body}\n\n${extraTags}`;
      }
      setContent(body);
    }
    setAiPanelOpen(false);
    setResult(null);
  };

  const dismissAiPanel = () => {
    setAiPanelOpen(false);
    setAiError(null);
  };

  const handlePlatformChange = (next: Platform) => {
    setPlatform(next);
    setResult(null);
    setAiPanelOpen(false);
    setAiReview(null);
    setAiError(null);
    if (next !== 'youtube') {
      setYoutubeTitle('');
      setYoutubeTags('');
    }
    if (next === 'youtube' && selectedFile && !selectedFile.type.startsWith('video/')) {
      revokePreview(previewUrl);
      setSelectedFile(null);
      setPreviewUrl(null);
      setMediaUrl('');
    }
  };

  const handlePublish = async () => {
    if (platform === 'youtube') {
      if (!selectedFile) {
        setResult({ success: false, message: 'Choose a video file to upload to YouTube.' });
        return;
      }
      if (mediaValidation.status !== 'ok') {
        setResult({
          success: false,
          message:
            mediaValidation.status === 'error'
              ? mediaValidation.message
              : 'Wait for validation or fix the issues shown above.',
        });
        return;
      }
    } else if (!content && !mediaUrl && !selectedFile) {
      setResult({ success: false, message: 'Please provide content and media (URL or File).' });
      return;
    }

    setIsPublishing(true);
    setResult(null);

    try {
      let finalMediaUrl = mediaUrl;

      if (selectedFile) {
        const uploadRes = await uploadsApi.upload(selectedFile, () => {});
        const uploadData = uploadRes.data;
        if (!uploadData.success) {
          throw new Error(uploadData.detail || 'File upload failed');
        }
        finalMediaUrl = uploadData.filename;
      }

      if (platform === 'youtube') {
        const tagList = youtubeTags
          .split(',')
          .map((t) => t.trim())
          .filter(Boolean);

        const response = await publishApi.social({
          platform: 'youtube',
          content,
          media_url: finalMediaUrl || null,
          title: youtubeTitle.trim() || undefined,
          youtube_format: youtubeFormat,
          ...(tagList.length ? { tags: tagList } : {}),
        });

        const data = response.data;
        if (data.success) {
          setResult({
            success: true,
            message: 'Uploaded to YouTube successfully!',
            post_id: data.post_id,
            video_id: data.video_id,
          });
          setContent('');
          setMediaUrl('');
          setYoutubeTitle('');
          setYoutubeTags('');
          revokePreview(previewUrl);
          setSelectedFile(null);
          setPreviewUrl(null);
          setMediaValidation({ status: 'idle' });
        } else {
          setResult({
            success: false,
            message: data.error || 'YouTube upload failed. Check OAuth and API key in settings.',
          });
        }
        return;
      }

      const response = await publishApi.social({
        platform,
        content,
        media_url: finalMediaUrl || null,
        media_type: platform === 'instagram' ? mediaType : undefined,
      });

      const data = response.data;
      if (data.success) {
        setResult({
          success: true,
          message: 'Published successfully!',
          post_id: data.post_id,
        });
        setContent('');
        setMediaUrl('');
        revokePreview(previewUrl);
        setSelectedFile(null);
        setPreviewUrl(null);
      } else {
        setResult({
          success: false,
          message: data.error || 'Failed to publish. Please check your integration settings.',
        });
      }
    } catch (error: unknown) {
      const err = error as { response?: { data?: { detail?: string; error?: string } }; message?: string };
      setResult({
        success: false,
        message:
          err.response?.data?.detail ||
          err.response?.data?.error ||
          err.message ||
          'An error occurred during publishing.',
      });
    } finally {
      setIsPublishing(false);
    }
  };

  const fileAccept = platform === 'youtube' ? 'video/*' : 'image/*,video/*';

  const publishDisabled =
    isPublishing ||
    (platform === 'instagram' && !mediaUrl && !selectedFile) ||
    (platform === 'youtube' && (!selectedFile || mediaValidation.status !== 'ok'));

  const previewAspectClass =
    platform === 'youtube'
      ? youtubeFormat === 'short'
        ? 'aspect-[9/16] max-h-[420px] mx-auto'
        : 'aspect-video'
      : 'aspect-square';

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Share2 className="w-6 h-6 text-orange-600" />
          Social Publish
        </h1>
        <p className="text-gray-500 mt-1">Create and publish content across your social channels.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Select Platform</label>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => handlePlatformChange('facebook')}
                    className={`flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 transition-all ${
                      platform === 'facebook'
                        ? 'border-blue-600 bg-blue-50 text-blue-600'
                        : 'border-gray-100 bg-gray-50 text-gray-400 hover:border-gray-200'
                    }`}
                  >
                    <Facebook className="w-5 h-5 shrink-0" />
                    <span className="font-semibold">Facebook</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => handlePlatformChange('instagram')}
                    className={`flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 transition-all ${
                      platform === 'instagram'
                        ? 'border-pink-600 bg-pink-50 text-pink-600'
                        : 'border-gray-100 bg-gray-50 text-gray-400 hover:border-gray-200'
                    }`}
                  >
                    <Instagram className="w-5 h-5 shrink-0" />
                    <span className="font-semibold">Instagram</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => handlePlatformChange('youtube')}
                    className={`flex items-center justify-center gap-2 py-3 px-4 rounded-lg border-2 transition-all ${
                      platform === 'youtube'
                        ? 'border-red-600 bg-red-50 text-red-600'
                        : 'border-gray-100 bg-gray-50 text-gray-400 hover:border-gray-200'
                    }`}
                  >
                    <Youtube className="w-5 h-5 shrink-0" />
                    <span className="font-semibold">YouTube</span>
                  </button>
                </div>
              </div>

              {platform === 'youtube' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">YouTube format</label>
                  <div className="flex flex-wrap gap-2">
                    {(['video', 'short'] as const).map((fmt) => (
                      <button
                        key={fmt}
                        type="button"
                        onClick={() => setYoutubeFormat(fmt)}
                        className={`px-4 py-2 rounded-full text-sm font-medium border transition-all ${
                          youtubeFormat === fmt
                            ? 'bg-red-100 border-red-200 text-red-700'
                            : 'bg-gray-50 border-gray-100 text-gray-500 hover:bg-gray-100'
                        }`}
                      >
                        {fmt === 'short' ? 'Short' : 'Standard video'}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Shorts: vertical 9:16, up to {SHORT_MAX_SEC}s. Standard video: typical horizontal or any
                    layout, resolution at least ~256×144, up to 12 hours.
                  </p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {platform === 'youtube' ? 'Title (optional)' : 'Post Content'}
                </label>
                {platform === 'youtube' && (
                  <input
                    type="text"
                    value={youtubeTitle}
                    onChange={(e) => setYoutubeTitle(e.target.value)}
                    placeholder="Video title — if empty, first line of description is used"
                    className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all mb-3"
                  />
                )}
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  {platform === 'youtube' ? 'Description' : platform === 'instagram' ? 'Caption' : 'Post'}
                </label>
                <textarea
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder={
                    platform === 'instagram'
                      ? 'Write a caption...'
                      : platform === 'youtube'
                        ? 'Video description...'
                        : "What's on your mind?"
                  }
                  className="w-full h-32 px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all resize-none"
                />
                {platform === 'youtube' && (
                  <div className="mt-3">
                    <label className="block text-xs font-medium text-gray-500 mb-1">
                      Tags (optional, comma-separated)
                    </label>
                    <input
                      type="text"
                      value={youtubeTags}
                      onChange={(e) => setYoutubeTags(e.target.value)}
                      placeholder="marketing, tutorial, behind the scenes"
                      className="w-full px-4 py-2 rounded-xl border border-gray-200 focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                    />
                  </div>
                )}
              </div>

              <div className="rounded-xl border border-violet-200 bg-violet-50/60 p-4 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-sm font-semibold text-violet-900">
                    <Sparkles className="w-4 h-4 text-violet-600" />
                    AI copy assistant
                  </div>
                  <select
                    value={aiTone}
                    onChange={(e) => setAiTone(e.target.value as AiTone)}
                    className="text-xs border border-violet-200 rounded-lg px-2 py-1.5 bg-white text-violet-900"
                  >
                    <option value="casual">Tone: Casual</option>
                    <option value="professional">Tone: Professional</option>
                    <option value="fun">Tone: Fun</option>
                  </select>
                </div>
                <p className="text-xs text-violet-800/85 leading-relaxed">
                  Generates a title, caption or description, and tags from what you typed above. Review the draft,
                  then choose <strong>Use for publish</strong> or keep editing by hand. Nothing goes live until you
                  click Publish Now.
                </p>
                <button
                  type="button"
                  onClick={handleGenerateAi}
                  disabled={aiLoading}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium bg-violet-600 text-white hover:bg-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {aiLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                  {aiLoading ? 'Generating…' : 'Generate with AI'}
                </button>

                {aiPanelOpen && (
                  <div className="rounded-lg border border-violet-100 bg-white p-4 space-y-3 shadow-sm">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-medium text-gray-900">Review AI draft</p>
                      <button
                        type="button"
                        onClick={dismissAiPanel}
                        className="p-1 rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                        aria-label="Close"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    {aiError && (
                      <div className="text-sm text-red-700 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                        {aiError}
                      </div>
                    )}
                    {aiLoading && (
                      <p className="text-sm text-gray-500 flex items-center gap-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Calling your local model…
                      </p>
                    )}
                    {aiReview && !aiLoading && (
                      <>
                        <div className="space-y-2">
                          {platform === 'youtube' && (
                            <div>
                              <label className="block text-xs font-medium text-gray-500 mb-1">Title</label>
                              <input
                                type="text"
                                value={aiReview.title}
                                onChange={(e) =>
                                  setAiReview((r) => (r ? { ...r, title: e.target.value } : null))
                                }
                                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm"
                              />
                            </div>
                          )}
                          <div>
                            <label className="block text-xs font-medium text-gray-500 mb-1">
                              {platform === 'youtube'
                                ? 'Description'
                                : platform === 'instagram'
                                  ? 'Caption'
                                  : 'Post text'}
                            </label>
                            <textarea
                              value={aiReview.body}
                              onChange={(e) =>
                                setAiReview((r) => (r ? { ...r, body: e.target.value } : null))
                              }
                              rows={5}
                              className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm resize-y min-h-[100px]"
                            />
                          </div>
                          {platform === 'youtube' && (
                            <div>
                              <label className="block text-xs font-medium text-gray-500 mb-1">
                                Tags (comma-separated)
                              </label>
                              <input
                                type="text"
                                value={aiReview.tagsLine}
                                onChange={(e) =>
                                  setAiReview((r) => (r ? { ...r, tagsLine: e.target.value } : null))
                                }
                                className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm"
                              />
                            </div>
                          )}
                          {(platform === 'instagram' || platform === 'facebook') &&
                            aiReview.hashtagsLine.trim() && (
                              <div>
                                <label className="block text-xs font-medium text-gray-500 mb-1">
                                  Hashtags (edit if needed)
                                </label>
                                <input
                                  type="text"
                                  value={aiReview.hashtagsLine}
                                  onChange={(e) =>
                                    setAiReview((r) => (r ? { ...r, hashtagsLine: e.target.value } : null))
                                  }
                                  className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm"
                                />
                                <p className="text-[11px] text-gray-500 mt-1">
                                  Included automatically when you click Use for publish if the caption has no hashtags yet.
                                </p>
                              </div>
                            )}
                        </div>
                        <div className="flex flex-wrap gap-2 pt-1">
                          <button
                            type="button"
                            onClick={applyAiToForm}
                            className="px-4 py-2 rounded-lg text-sm font-semibold bg-green-600 text-white hover:bg-green-700"
                          >
                            Use for publish
                          </button>
                          <button
                            type="button"
                            onClick={dismissAiPanel}
                            className="px-4 py-2 rounded-lg text-sm font-medium border border-gray-200 text-gray-700 hover:bg-gray-50"
                          >
                            Cancel
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Media</label>
                <div className="space-y-4">
                  <div className="flex items-center justify-center w-full">
                    <label
                      className={`flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
                        selectedFile ? 'border-orange-500 bg-orange-50' : 'border-gray-200 bg-gray-50 hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex flex-col items-center justify-center pt-5 pb-6 px-4 text-center">
                        {selectedFile ? (
                          <>
                            <CheckCircle2 className="w-8 h-8 mb-3 text-orange-500" />
                            <p className="text-sm text-orange-600 font-medium break-all">{selectedFile.name}</p>
                          </>
                        ) : (
                          <>
                            <Upload className="w-8 h-8 mb-3 text-gray-400" />
                            <p className="text-sm text-gray-500">
                              <span className="font-semibold">Click to upload</span> or drag and drop
                            </p>
                            <p className="text-xs text-gray-400">
                              {platform === 'youtube' ? 'Video only (max 100MB)' : 'Images or Videos (max 100MB)'}
                            </p>
                          </>
                        )}
                      </div>
                      <input type="file" className="hidden" onChange={handleFileChange} accept={fileAccept} />
                    </label>
                  </div>

                  {platform === 'youtube' && (
                    <div
                      className={`rounded-lg px-3 py-2 text-sm flex items-start gap-2 ${
                        mediaValidation.status === 'ok'
                          ? 'bg-green-50 text-green-800 border border-green-100'
                          : mediaValidation.status === 'error'
                            ? 'bg-red-50 text-red-800 border border-red-100'
                            : mediaValidation.status === 'checking'
                              ? 'bg-amber-50 text-amber-900 border border-amber-100'
                              : 'bg-gray-50 text-gray-600 border border-gray-100'
                      }`}
                    >
                      {mediaValidation.status === 'checking' ? (
                        <Loader2 className="w-4 h-4 mt-0.5 animate-spin shrink-0" />
                      ) : mediaValidation.status === 'ok' ? (
                        <CheckCircle2 className="w-4 h-4 mt-0.5 shrink-0" />
                      ) : mediaValidation.status === 'error' ? (
                        <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                      ) : (
                        <AlertCircle className="w-4 h-4 mt-0.5 text-gray-400 shrink-0" />
                      )}
                      <span>
                        {mediaValidation.status === 'idle' &&
                          'Select a video file. Requirements are checked automatically.'}
                        {mediaValidation.status === 'checking' && 'Checking video…'}
                        {mediaValidation.status === 'ok' && mediaValidation.message}
                        {mediaValidation.status === 'error' && mediaValidation.message}
                      </span>
                    </div>
                  )}

                  {platform !== 'youtube' && (
                    <>
                      <div className="relative flex items-center gap-3">
                        <div className="flex-1 h-px bg-gray-100" />
                        <span className="text-[10px] font-bold text-gray-300 uppercase">Or provide URL</span>
                        <div className="flex-1 h-px bg-gray-100" />
                      </div>

                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                          <ImageIcon className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          type="text"
                          value={mediaUrl}
                          onChange={(e) => {
                            setMediaUrl(e.target.value);
                            if (selectedFile) setSelectedFile(null);
                            revokePreview(previewUrl);
                            setPreviewUrl(null);
                          }}
                          placeholder="https://example.com/image.jpg"
                          className="block w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                        />
                      </div>
                    </>
                  )}
                </div>
                {platform === 'instagram' && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Media Type</label>
                    <div className="flex gap-2">
                      {(['IMAGE', 'REELS'] as const).map((type) => (
                        <button
                          key={type}
                          type="button"
                          onClick={() => setMediaType(type)}
                          className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                            mediaType === type
                              ? 'bg-orange-100 border-orange-200 text-orange-600'
                              : 'bg-gray-50 border-gray-100 text-gray-500 hover:bg-gray-100'
                          }`}
                        >
                          {type}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {result && (
                <div
                  className={`p-4 rounded-lg flex items-start gap-3 ${
                    result.success
                      ? 'bg-green-50 text-green-700 border border-green-100'
                      : 'bg-red-50 text-red-700 border border-red-100'
                  }`}
                >
                  {result.success ? (
                    <CheckCircle2 className="w-5 h-5 mt-0.5 shrink-0" />
                  ) : (
                    <AlertCircle className="w-5 h-5 mt-0.5 shrink-0" />
                  )}
                  <div>
                    <p className="text-sm font-medium">{result.message}</p>
                    {(result.video_id || result.post_id) && (
                      <p className="text-xs mt-1 opacity-70">
                        {result.video_id ? `Video ID: ${result.video_id}` : `Post ID: ${result.post_id}`}
                      </p>
                    )}
                  </div>
                </div>
              )}

              <button
                type="button"
                onClick={handlePublish}
                disabled={publishDisabled}
                className={`w-full py-4 rounded-xl flex items-center justify-center gap-2 font-bold text-white transition-all shadow-lg ${
                  publishDisabled
                    ? 'bg-gray-300 cursor-not-allowed shadow-none'
                    : 'bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 active:transform active:scale-[0.98]'
                }`}
              >
                {isPublishing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Publishing...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Publish Now</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <label className="block text-sm font-medium text-gray-700">Live Preview</label>
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden max-w-[320px] mx-auto">
            <div className="px-4 py-3 flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-orange-500 to-yellow-500" />
              <div>
                <p className="text-xs font-bold text-gray-900">
                  {platform === 'youtube' ? 'Your Channel' : 'Your Business'}
                </p>
                <p className="text-[10px] text-gray-400">
                  {platform === 'youtube'
                    ? youtubeFormat === 'short'
                      ? 'YouTube Shorts'
                      : 'YouTube'
                    : 'Sponsored • Local'}
                </p>
              </div>
            </div>

            <div
              className={`bg-gray-50 flex items-center justify-center border-y border-gray-50 overflow-hidden ${previewAspectClass}`}
            >
              {previewUrl && selectedFile?.type.startsWith('video/') ? (
                <video
                  src={previewUrl}
                  className="w-full h-full object-cover"
                  muted
                  playsInline
                  preload="metadata"
                />
              ) : previewUrl || (mediaUrl && mediaUrl.startsWith('http')) ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={previewUrl || mediaUrl} alt="Preview" className="w-full h-full object-cover" />
              ) : (
                <div className="flex flex-col items-center gap-2 text-gray-300 p-6">
                  {mediaType === 'REELS' || platform === 'youtube' ? (
                    <Video className="w-12 h-12" />
                  ) : (
                    <ImageIcon className="w-12 h-12" />
                  )}
                  <span className="text-[10px] font-medium text-center">Media Preview</span>
                </div>
              )}
            </div>

            <div className="p-4 space-y-3">
              <div className="flex gap-4">
                <div className="w-5 h-5 rounded bg-gray-100" />
                <div className="w-5 h-5 rounded bg-gray-100" />
                <div className="w-5 h-5 rounded bg-gray-100 ml-auto" />
              </div>
              <div className="space-y-2">
                <div className="h-2 w-24 bg-gray-100 rounded" />
                <p className="text-xs text-gray-600 line-clamp-3 leading-relaxed">
                  <span className="font-bold text-gray-900 mr-2">
                    {platform === 'youtube' ? youtubeTitle || 'Title' : 'Your Business'}
                  </span>
                  {content || 'Your post content will appear here...'}
                </p>
              </div>
              <p className="text-[10px] text-gray-300 uppercase font-medium">Just now</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
