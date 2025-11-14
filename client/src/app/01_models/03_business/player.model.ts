export interface PlayerModel {
  id: string | null;
  bga_id: number;
  bga_banned: boolean | null;
  name: string;
  country: string | null;
  team_id: string | null;
  team_name: string | null;
  avatar_url: string | null;
  bio: string | null;
  total_points: number | null;
  total_wins: number | null;
  total_losses: number | null;
  total_draws: number | null;
  win_rate: number | null;
  total_games: number | null;
  created_at: string | null;
  updated_at: string | null;
  is_active: boolean | null;
  last_game_at: string | null;
  is_anonymized: boolean | null;
}
