export interface SeasonModel {
  id: number;
  season: number;
  start: number;      // Timestamp Unix en secondes
  end: number;        // Timestamp Unix en secondes
  current: boolean;
}
