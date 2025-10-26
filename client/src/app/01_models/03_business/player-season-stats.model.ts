import { PlayerModel } from './player.model';

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

  // Tournois
  tournaments_played: number;
  tournaments_won: number;

  // Métadonnées
  created_at: string; // ISO DateTime
  updated_at: string; // ISO DateTime
}