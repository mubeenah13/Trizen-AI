import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Image as ImageIcon } from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { DragDropUploader } from '../components/DragDropUploader';
import { PhotoGrid } from '../components/PhotoGrid';
import { api } from '../services/api';
import type { Event, Photo } from '../types';

export const TeamEventDetailPage: React.FC = () => {
  const { eventId } = useParams<{ eventId: string }>();
  const [event, setEvent] = useState<Event | null>(null);
  const [photos, setPhotos] = useState<Photo[]>([]);

  const fetchData = async () => {
    if (!eventId) return;
    try {
      const [evRes, photoRes] = await Promise.all([
        api.get(`/events/${eventId}`),
        api.get(`/events/${eventId}/photos`),
      ]);
      setEvent(evRes.data);
      setPhotos(photoRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [eventId]);

  const handleUploadSuccess = (newPhotos: Photo[]) => {
    setPhotos((prev) => [...newPhotos, ...prev]);
  };

  if (!event) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <p className="text-slate-400">Loading assigned event...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-8">
        <Link to="/team" className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-sky-400 font-medium">
          <ArrowLeft className="w-4 h-4" /> Back to Photographer Portal
        </Link>

        {/* Event Banner */}
        <div className="glass-card p-6 md:p-8 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-950/60 px-2.5 py-1 rounded-md border border-emerald-800/50">
              ASSIGNED EVENT
            </span>
            <h1 className="text-3xl font-extrabold text-slate-100 mt-2">{event.name}</h1>
            <p className="text-sm text-slate-400 mt-1">{event.description || 'No description provided.'}</p>
          </div>

          <div className="flex items-center gap-3 bg-slate-900/80 px-4 py-2 rounded-xl border border-slate-800">
            <ImageIcon className="w-5 h-5 text-sky-400" />
            <span className="text-sm font-semibold text-slate-200">Uploaded: <strong className="text-sky-400">{photos.length}</strong> photos</span>
          </div>
        </div>

        {/* Multi-photo Uploader */}
        <div>
          <h2 className="text-xl font-bold text-slate-200 mb-3">Upload Photography Files</h2>
          <DragDropUploader eventId={event.id} onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Uploaded Event Photos */}
        <div>
          <h2 className="text-xl font-bold text-slate-200 mb-4">Event Gallery Photographs</h2>
          <PhotoGrid photos={photos} selectable={false} />
        </div>
      </main>
    </div>
  );
};
