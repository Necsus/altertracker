import { PlayerModel } from './player.model';

export interface FactionStats {
  wins: number;
  losses: number;
  draws: number;
  games: number;
  win_rate: number;
}

export interface HeroStats {
  wins: number;
  losses: number;
  draws: number;
  games: number;
  win_rate: number;
}

export interface PlayerSeasonStatsModel {
  id: string; // UUID
  player_id: string; // UUID

  player: PlayerModel;

  season: string; // Ex: "19", "10"

  // Points et statistiques
  points: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  total_games: number; // Calculé côté backend

  // Classement
  rank: number | null;
  highest_rank: number | null;

  // ✅ Nouvelles propriétés
  most_played_faction: string | null;
  most_played_hero: string | null;
  faction_stats: Record<string, FactionStats>;
  hero_stats: Record<string, HeroStats>;

  // Stats de temps
  total_reflexion_time: number | null;
  total_turns: number | null;  // Total de tours joués
  fastest_game_minutes: number | null;
  slowest_game_minutes: number | null;

  current_streak: number;
  best_win_streak: number;
  worst_loss_streak: number;

  // Tournois
  tournaments_played: number;
  tournaments_won: number;

  // Métadonnées
  created_at: string; // ISO DateTime
  updated_at: string; // ISO DateTime
}