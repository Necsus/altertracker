export interface GameModel {
  id: string; // UUID
  table_id: number;
  ranked?: boolean;
  tournament_id?: string; // UUID

  // Joueurs
  player1_id: string; // UUID
  player1_name?: string;
  player2_id: string; // UUID
  player2_name?: string;

  player1_faction?: string;
  player2_faction?: string;

  player1_hero?: string;
  player2_hero?: string;

  // Decks utilisés
  player1_deck_id?: string; // UUID
  player2_deck_id?: string; // UUID

  player1_reflexion_time?: number; // en secondes
  player2_reflexion_time?: number; // en secondes

  player1_nb_turns?: number;
  player2_nb_turns?: number;

  player1_arena_point_win?: number;
  player2_arena_point_win?: number;

  player1_arena_point_after_game?: number;
  player2_arena_point_after_game?: number;

  // Résultat
  winner_id?: string; // UUID
  is_draw: boolean;

  // Contexte
  season?: string;
  round?: number;
  game_format?: string;

  // Temporalité
  played_at: string; // ISO DateTime
  start?: string; // ISO DateTime
  end?: string; // ISO DateTime
  duration_minutes?: number;

  // Méta
  replay_url?: string;
  notes?: string;

  // Validation
  is_verified: boolean;
  verified_by?: number;
  verified_at?: string; // ISO DateTime
}

export interface GameListResponse {
  games: GameModel[];
  total: number;
  page: number;
  limit: number;
}

export interface GameFilters {
  player_id?: string;
  opponent_id?: string;
  tournament_id?: string;
  season?: string;
  ranked?: boolean;
  is_draw?: boolean;
  date_from?: string;
  date_to?: string;
  game_format?: string;
}

export interface GameStats {
  total_games: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  avg_duration_minutes?: number;
  last_game_at?: string;
}

// Classes utilitaires
export class GameHelper {
  static getWinnerName(game: GameModel): string | null {
    if (game.is_draw) return 'Draw';
    if (!game.winner_id) return null;
    return game.winner_id === game.player1_id ? game.player1_name || 'Player 1' : game.player2_name || 'Player 2';
  }

  static getLoserName(game: GameModel): string | null {
    if (game.is_draw) return null;
    if (!game.winner_id) return null;
    return game.winner_id === game.player1_id ? game.player2_name || 'Player 2' : game.player1_name || 'Player 1';
  }

  static getOpponentId(game: GameModel, playerId: string): string {
    return game.player1_id === playerId ? game.player2_id : game.player1_id;
  }

  static getOpponentName(game: GameModel, playerId: string): string | undefined {
    return game.player1_id === playerId ? game.player2_name : game.player1_name;
  }

  static isPlayerWinner(game: GameModel, playerId: string): boolean {
    return game.winner_id === playerId;
  }

  static getGameResult(game: GameModel, playerId: string): 'win' | 'loss' | 'draw' {
    if (game.is_draw) return 'draw';
    return game.winner_id === playerId ? 'win' : 'loss';
  }

  static formatDuration(durationMinutes?: number): string {
    if (!durationMinutes) return 'N/A';
    const hours = Math.floor(durationMinutes / 60);
    const minutes = durationMinutes % 60;
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  static formatPlayedAt(playedAt: string): string {
    const date = new Date(playedAt);
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}

// Constantes
export const GAME_FORMATS = [
  'Constructed',
  'Limited',
  'Draft',
  'Sealed',
  'Commander',
  'Custom'
] as const;

export type GameFormat = typeof GAME_FORMATS[number];

export const GAME_STATUS = {
  VERIFIED: 'verified',
  PENDING: 'pending',
  REJECTED: 'rejected'
} as const;