import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, UserPlus, Sparkles, Check, Copy, ExternalLink } from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { PhotoGrid } from '../components/PhotoGrid';
import { CreateGalleryModal } from '../components/CreateGalleryModal';
import { AssignMemberModal } from '../components/AssignMemberModal';
import { api } from '../services/api';
import type { Event, Photo, Gallery } from '../types';

export const AdminEventDetailPage: React.FC = () => {
  const { eventId } = useParams<{ eventId: string }>();
  const [event, setEvent] = useState<Event | null>(null);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [galleries, setGalleries] = useState<Gallery[]>([]);
  const [selectedPhotoIds, setSelectedPhotoIds] = useState<string[]>([]);

  const [isGalleryModalOpen, setIsGalleryModalOpen] = useState(false);
  const [isMemberModalOpen, setIsMemberModalOpen] = useState(false);
  const [copiedSlug, setCopiedSlug] = useState<string | null>(null);

  const fetchData = async () => {
    if (!eventId) return;
    try {
      const [evRes, photoRes, galRes] = await Promise.all([
        api.get(`/events/${eventId}`),
        api.get(`/events/${eventId}/photos`),
        api.get(`/galleries/events/${eventId}`),
      ]);
      setEvent(evRes.data);
      setPhotos(photoRes.data);
      setGalleries(galRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [eventId]);

  const handleToggleSelectPhoto = (photoId: string) => {
    setSelectedPhotoIds((prev) =>
      prev.includes(photoId) ? prev.filter((id) => id !== photoId) : [...prev, photoId]
    );
  };

  const handleSelectAll = () => {
    setSelectedPhotoIds(photos.map((p) => p.id));
  };

  const handleDeselectAll = () => {
    setSelectedPhotoIds([]);
  };

  const handleDeletePhoto = async (photoId: string) => {
    try {
      await api.delete(`/photos/${photoId}`);
      setPhotos((prev) => prev.filter((p) => p.id !== photoId));
      setSelectedPhotoIds((prev) => prev.filter((id) => id !== photoId));
    } catch (err) {
      console.error(err);
    }
  };

  const handleCopyLink = (shareUrl: string, slug: string) => {
    navigator.clipboard.writeText(shareUrl);
    setCopiedSlug(slug);
    setTimeout(() => setCopiedSlug(null), 2000);
  };

  if (!event) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <p className="text-slate-400">Loading event details...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-8">
        <Link to="/admin" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-sky-400 font-medium">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>

        {/* Event Header Banner */}
        <div className="glass-card p-6 md:p-8 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <span className="text-xs font-mono text-sky-400 bg-sky-950/60 px-2.5 py-1 rounded-md border border-sky-800/50">
              EVENT DATE: {event.event_date}
            </span>
            <h1 className="text-3xl font-extrabold text-slate-100 mt-2">{event.name}</h1>
            <p className="text-sm text-slate-400 mt-1">{event.description || 'No description provided.'}</p>

            <div className="flex items-center gap-4 mt-4 text-xs text-slate-300">
              <span>Total Photos: <strong className="text-sky-400">{photos.length}</strong></span>
              <span>Assigned Photographers: <strong className="text-emerald-400">{event.members.length}</strong></span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => setIsMemberModalOpen(true)}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm border border-slate-700 flex items-center gap-2 transition-colors"
            >
              <UserPlus className="w-4 h-4 text-emerald-400" /> Assign Photographer
            </button>

            <button
              onClick={() => setIsGalleryModalOpen(true)}
              disabled={photos.length === 0}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-sky-500/25 flex items-center gap-2 disabled:opacity-50 transition-all"
            >
              <Sparkles className="w-4 h-4" /> Create & Publish Gallery
            </button>
          </div>
        </div>

        {/* Published Galleries Section */}
        {galleries.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-slate-200">Published Customer Galleries</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {galleries.map((gal) => (
                <div key={gal.id} className="glass-card p-5 rounded-2xl border border-sky-900/60 bg-sky-950/20 flex flex-col justify-between gap-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-emerald-400 bg-emerald-950/80 px-2.5 py-0.5 rounded-full border border-emerald-800/60">
                        ● {gal.status}
                      </span>
                      <span className="text-xs text-slate-400 font-mono">PIN PROTECTED</span>
                    </div>
                    <h3 className="text-lg font-bold text-slate-100">{gal.name}</h3>
                    <p className="text-xs text-slate-400 mt-1">Contains {gal.photo_count} selected photographs.</p>
                  </div>

                  <div className="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
                    <div className="truncate text-xs font-mono text-sky-400 bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800 flex-1 truncate">
                      {gal.share_url}
                    </div>
                    <button
                      onClick={() => handleCopyLink(gal.share_url, gal.slug)}
                      className="px-3 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-white text-xs font-bold flex items-center gap-1 shrink-0 transition-colors"
                    >
                      {copiedSlug === gal.slug ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                      {copiedSlug === gal.slug ? 'Copied!' : 'Copy Link'}
                    </button>
                    <a
                      href={gal.share_url}
                      target="_blank"
                      rel="noreferrer"
                      className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 shrink-0"
                      title="Open Gallery Link"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Uploaded Photos Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold text-slate-200">Event Uploaded Photos</h2>
              <p className="text-xs text-slate-400">Review all photographs uploaded by team members and select photos to include in public galleries.</p>
            </div>
          </div>

          <PhotoGrid
            photos={photos}
            selectedPhotoIds={selectedPhotoIds}
            onToggleSelectPhoto={handleToggleSelectPhoto}
            onSelectAll={handleSelectAll}
            onDeselectAll={handleDeselectAll}
            onDeletePhoto={handleDeletePhoto}
            selectable={true}
          />
        </div>
      </main>

      <CreateGalleryModal
        isOpen={isGalleryModalOpen}
        onClose={() => setIsGalleryModalOpen(false)}
        eventId={event.id}
        selectedPhotoIds={selectedPhotoIds.length > 0 ? selectedPhotoIds : photos.map((p) => p.id)}
        onGalleryCreated={(newGal) => {
          setGalleries((prev) => [newGal, ...prev]);
        }}
      />

      <AssignMemberModal
        isOpen={isMemberModalOpen}
        onClose={() => setIsMemberModalOpen(false)}
        eventId={event.id}
        onMemberAssigned={() => fetchData()}
      />
    </div>
  );
};
