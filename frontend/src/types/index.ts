export type UserRole = 'ADMIN' | 'TEAM_MEMBER';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  created_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface EventMember {
  id: string;
  event_id: string;
  user_id: string;
  user_name: string;
  user_email: string;
  assigned_at: string;
}

export interface Event {
  id: string;
  name: string;
  description?: string;
  event_date: string;
  created_by: string;
  created_at: string;
  photo_count: number;
  members: EventMember[];
}

export interface Photo {
  id: string;
  event_id: string;
  uploaded_by: string;
  uploader_name?: string;
  filename: string;
  storage_key: string;
  url: string;
  file_size: number;
  mime_type: string;
  width?: number;
  height?: number;
  created_at: string;
}

export type GalleryStatus = 'DRAFT' | 'PUBLISHED';

export interface Gallery {
  id: string;
  event_id: string;
  event_name?: string;
  name: string;
  slug: string;
  status: GalleryStatus;
  published_at?: string;
  created_by: string;
  photo_count: number;
  created_at: string;
  share_url: string;
}

export interface PublicGalleryMeta {
  name: string;
  slug: string;
  event_name: string;
  event_date: string;
  photo_count: number;
  is_protected: boolean;
}

export interface PublicPhoto {
  id: string;
  filename: string;
  file_size: number;
  mime_type: string;
  url: string;
  created_at: string;
}
