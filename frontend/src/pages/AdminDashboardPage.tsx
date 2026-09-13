import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Image as ImageIcon, Sparkles, Users, Plus, ArrowRight, Camera } from 'lucide-react';
import { Navbar } from '../components/Navbar';
import { Modal } from '../components/Modal';
import { api } from '../services/api';
import type { Event } from '../types';

export const AdminDashboardPage: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // New Event Form State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [eventName, setEventName] = useState('');
  const [eventDesc, setEventDesc] = useState('');
  const [eventDate, setEventDate] = useState(new Date().toISOString().split('T')[0]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = async () => {
    try {
      const res = await api.get('/events');
      setEvents(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleCreateEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await api.post('/events', {
        name: eventName.trim(),
        description: eventDesc.trim(),
        event_date: eventDate,
      });

      setIsModalOpen(false);
      setEventName('');
      setEventDesc('');
      fetchEvents();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create event.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Real Database Metrics
  const totalEvents = events.length;
  const totalPhotos = events.reduce((sum, e) => sum + e.photo_count, 0);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8 space-y-8">
        {/* Header Title */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight gradient-text">Lead Admin Dashboard</h1>
            <p className="text-sm text-slate-400 mt-1">Manage events, assign photographers, and publish customer galleries.</p>
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-sky-500/25 flex items-center gap-2 transition-all"
          >
            <Plus className="w-4 h-4" /> Create New Event
          </button>
        </div>

        {/* Real Metrics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="glass-card p-6 rounded-2xl border border-slate-800 flex items-center gap-4">
            <div className="p-3.5 rounded-xl bg-sky-950/80 text-sky-400 border border-sky-800/50">
              <Calendar className="w-6 h-6" />
            </div>
            <div>
              <span className="text-2xl font-bold text-slate-100">{totalEvents}</span>
              <p className="text-xs font-semibold text-slate-400">Total Managed Events</p>
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-slate-800 flex items-center gap-4">
            <div className="p-3.5 rounded-xl bg-indigo-950/80 text-indigo-400 border border-indigo-800/50">
              <ImageIcon className="w-6 h-6" />
            </div>
            <div>
              <span className="text-2xl font-bold text-slate-100">{totalPhotos}</span>
              <p className="text-xs font-semibold text-slate-400">Uploaded Event Photos</p>
            </div>
          </div>

          <div className="glass-card p-6 rounded-2xl border border-slate-800 flex items-center gap-4">
            <div className="p-3.5 rounded-xl bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <span className="text-2xl font-bold text-slate-100">{totalEvents}</span>
              <p className="text-xs font-semibold text-slate-400">Active Photography Pipelines</p>
            </div>
          </div>
        </div>

        {/* Events Grid */}
        <div>
          <h2 className="text-xl font-bold text-slate-200 mb-4">Event Catalog</h2>

          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((n) => (
                <div key={n} className="h-44 rounded-2xl bg-slate-900 animate-pulse border border-slate-800" />
              ))}
            </div>
          ) : events.length === 0 ? (
            <div className="glass-card p-12 text-center rounded-2xl border border-slate-800">
              <Camera className="w-12 h-12 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-300 font-semibold">No events created yet.</p>
              <p className="text-xs text-slate-500 mt-1">Click "Create New Event" to get started.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {events.map((ev) => (
                <div
                  key={ev.id}
                  className="glass-card rounded-2xl p-6 border border-slate-800 hover:border-slate-700 transition-all flex flex-col justify-between group"
                >
                  <div>
                    <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                      <span className="flex items-center gap-1 font-mono">
                        <Calendar className="w-3.5 h-3.5 text-sky-400" /> {ev.event_date}
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-semibold border border-slate-700">
                        {ev.photo_count} Photos
                      </span>
                    </div>

                    <h3 className="text-lg font-bold text-slate-100 group-hover:text-sky-400 transition-colors mb-2">
                      {ev.name}
                    </h3>
                    <p className="text-xs text-slate-400 line-clamp-2 mb-4">{ev.description || 'No description provided.'}</p>
                  </div>

                  <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <Users className="w-3.5 h-3.5 text-indigo-400" /> {ev.members.length} Photographers
                    </span>
                    <Link
                      to={`/admin/events/${ev.id}`}
                      className="inline-flex items-center gap-1 text-xs font-bold text-sky-400 hover:text-sky-300 bg-sky-950/40 hover:bg-sky-950/80 px-3 py-1.5 rounded-lg border border-sky-800/50 transition-colors"
                    >
                      Manage <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Create Event Modal */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Create New Event">
        <form onSubmit={handleCreateEvent} className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-1">Event Name</label>
            <input
              type="text"
              placeholder="e.g. Annual Tech Gala 2026"
              value={eventName}
              onChange={(e) => setEventName(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-1">Event Date</label>
            <input
              type="date"
              value={eventDate}
              onChange={(e) => setEventDate(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 focus:outline-none focus:border-sky-500 text-sm"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-1">Description (Optional)</label>
            <textarea
              placeholder="Brief details about the venue, timeline, or photography scope..."
              value={eventDesc}
              onChange={(e) => setEventDesc(e.target.value)}
              rows={3}
              className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm"
            />
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-red-950/60 border border-red-800 text-red-300 text-xs">
              {error}
            </div>
          )}

          <div className="pt-3 flex justify-end gap-3">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-sky-500/20 disabled:opacity-50"
            >
              {isSubmitting ? 'Creating...' : 'Create Event'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
