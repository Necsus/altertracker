export interface UserSearchModel {
  id: number; // ID unique de la recherche
  id_user: number; // ID de l'utilisateur associé
  name_search: string; // Nom de la recherche
  url_search: string; // URL de la recherche
  created_at: string; // Date de création au format ISO
  active_notification?: boolean; // Indique si les notifications sont actives pour cette recherche
}