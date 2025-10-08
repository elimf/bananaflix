export type Genre = {
  uuid: number;
  name: string;
};



export type TokenPayload = {
  sub: string;
  role: string;
  pseudo: string;
  exp: number;
};

export type AuthContextType = {
  token: string | null;
  role: string | null;
  login: (token: string) => void;
  logout: () => void;
};

export interface VideoUserInfo {
  id: number;
  video_id: number;
  user_id: string;
  progress_duration: number;
  status: string;
  created_at: string;
  updated_at: string;
  quality: string;

}

export type GenreVideo = {
  id: number;
  name: string;
};

export type VideoStatus = "processing" | "done" | "failed";
export type TrailerStatus = "none" | "processing" | "done" | "failed";

export type VideoDetail = {
  id: number;
  title: string;
  description: string;
  duration: number;
  genre: GenreVideo | null;
  status: VideoStatus;
  output_file: string | null;
  qualities: Record<string, string>; // ex: { "360p": "...", "720p": "...", "1080p": "..." }
  trailer_file: string | null;
  trailer_status: TrailerStatus;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
};

export type PaginatedVideos = {
  total: number;
  skip: number;
  limit: number;
  videos: VideoDetail[];
};

export interface Stats {
  add_bookmark: number;
  remove_bookmark: number;
  as_view: number;
  stop: number;
  play: number;
  pause: number;
}

export interface VideoStats {
  video: VideoDetail;
  stats: Stats;
}

// Type pour un tableau de stats globales
export type GlobalStats = VideoStats[];

export interface BookmarkVideo {
  bookmark_uuid: string;
  video_id: number;
  title: string;
  description: string | null;
  duration: number;
  status: string;
  output_file: string | null;
  trailer_file: string | null;
  trailer_status: string;
}