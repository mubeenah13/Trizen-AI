import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Lock, Camera, ShieldCheck, Sparkles, AlertCircle, ArrowRight, Eye, Calendar } from 'lucide-react';
import { publicApi } from '../services/api';
import type { PublicGalleryMeta, PublicPhoto } from '../types';
import { LightboxModal } from '../components/LightboxModal';

export const PublicGalleryPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [meta, setMeta] = useState<PublicGalleryMeta | null>(null);
  const [isLocked, setIsLocked] = useState(true);
  const [pin, setPin] = useState('');
  const [photos, setPhotos] = useState<PublicPhoto[]>([]);

  const [isLoadingMeta, setIsLoadingMeta] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activePhotoIndex, setActivePhotoIndex] = useState<number | null>(null);

  useEffect(() => {
    const fetchMeta = async () => {
      if (!slug) return;
      try {
        const res = await publicApi.get(`/public/galleries/${slug}`);
        setMeta(res.data);
      } catch (err: any) {
        setError('Gallery not found or is currently private/unpublished.');
      } finally {
        setIsLoadingMeta(false);
      }
    };
    fetchMeta();
  }, [slug]);

  const handleVerifyPin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pin || pin.length < 4 || pin.length > 8) {
      setError('Please enter a valid 4-8 digit PIN');
      return;
    }

    setIsVerifying(true);
    setError(null);

    try {
      const verifyRes = await publicApi.post(`/public/galleries/${slug}/verify`, { pin: pin.trim() });
      const token = verifyRes.data.gallery_access_token;

      const photoRes = await publicApi.get(`/public/galleries/${slug}/photos`, {
        headers: { 'X-Gallery-Token': token },
      });

      setPhotos(photoRes.data);
      setIsLocked(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Incorrect PIN. Access denied.');
    } finally {
      setIsVerifying(false);
    }
  };

  if (isLoadingMeta) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4">
        <p className="text-slate-400">Loading customer gallery...</p>
      </div>
    );
  }

  if (!meta && error) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full glass-card p-8 rounded-2xl text-center border border-slate-800">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-100">Gallery Unavailable</h2>
          <p className="text-sm text-slate-400 mt-2">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <header className="glass-nav px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 shadow-lg shadow-sky-500/20">
            <Camera className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight text-slate-100">{meta?.name || 'Customer Gallery'}</span>
            <span className="ml-2 text-xs text-sky-400 bg-sky-950/60 px-2 py-0.5 rounded-full border border-sky-800/50">
              {meta?.event_name}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>{isLocked ? 'PIN Protected' : 'Unlocked Session'}</span>
        </div>
      </header>

      {isLocked ? (
        <main className="flex-1 flex items-center justify-center p-4 sm:p-8">
          <div className="w-full max-w-md glass-card rounded-2xl p-8 border border-slate-800 shadow-2xl animate-fade-in text-center">
            <div className="inline-flex p-4 rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 shadow-xl shadow-sky-500/20 mb-6">
              <Lock className="w-8 h-8 text-white" />
            </div>

            <h1 className="text-2xl font-bold text-slate-100 mb-1">{meta?.name}</h1>
            <p className="text-xs text-slate-400 mb-6">
              Official Photography Gallery for <strong className="text-sky-400">{meta?.event_name}</strong> ({meta?.photo_count} Photos)
            </p>

            {error && (
              <div className="mb-6 p-3.5 rounded-xl bg-red-950/60 border border-red-800 text-red-300 text-xs flex items-center justify-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleVerifyPin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-2 uppercase tracking-wider">
                  Enter Gallery Access PIN
                </label>
                <input
                  type="text"
                  placeholder="e.g. 123456"
                  value={pin}
                  onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 8))}
                  className="w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-sky-500 text-center font-mono text-xl tracking-widest"
                  autoFocus
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isVerifying}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold shadow-lg shadow-sky-500/25 flex items-center justify-center gap-2 transition-all text-sm disabled:opacity-50"
              >
                {isVerifying ? 'Verifying PIN...' : 'Unlock Gallery'} <ArrowRight className="w-4 h-4" />
              </button>
            </form>

            <p className="text-[11px] text-slate-500 mt-6">
              PIN is provided by your event organizer or photography studio.
            </p>
          </div>
        </main>
      ) : (
        <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-6 animate-fade-in">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 glass-card p-6 rounded-2xl border border-slate-800">
            <div>
              <h1 className="text-2xl font-bold text-slate-100">{meta?.name}</h1>
              <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                <Calendar className="w-3.5 h-3.5 text-sky-400" /> {meta?.event_date} • {photos.length} Published Photographs
              </p>
            </div>

            <span className="text-xs font-semibold text-emerald-400 bg-emerald-950/60 px-3 py-1 rounded-full border border-emerald-800/60 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> High-Resolution Collection
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {photos.map((photo, idx) => (
              <div
                key={photo.id}
                onClick={() => setActivePhotoIndex(idx)}
                className="group relative rounded-xl overflow-hidden glass-card border border-slate-800 hover:border-sky-500/60 transition-all duration-300 cursor-pointer aspect-[4/3] bg-slate-950"
              >
                <img
                  src={photo.url}
                  alt={photo.filename}
                  loading="lazy"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />

                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity p-4 flex flex-col justify-end">
                  <span className="text-xs font-semibold text-slate-100 flex items-center gap-1">
                    <Eye className="w-4 h-4 text-sky-400" /> View Full Resolution
                  </span>
                </div>
              </div>
            ))}
          </div>

          {activePhotoIndex !== null && (
            <LightboxModal
              photo={photos[activePhotoIndex]}
              onClose={() => setActivePhotoIndex(null)}
              onPrev={() => setActivePhotoIndex((prev) => (prev !== null && prev > 0 ? prev - 1 : prev))}
              onNext={() => setActivePhotoIndex((prev) => (prev !== null && prev < photos.length - 1 ? prev + 1 : prev))}
              hasPrev={activePhotoIndex > 0}
              hasNext={activePhotoIndex < photos.length - 1}
            />
          )}
        </main>
      )}
    </div>
  );
};
