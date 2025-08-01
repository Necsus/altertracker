
export interface UserAlertModel {
  id: number; // ID unique de la recherche
  id_user: number; // ID de l'utilisateur associé
  id_search?: number; // ID de la recherche associée (optionnel)
  reference_card: string; // Nom de la recherche
  mail_active: boolean; // URL de la recherche
  created_at: string; // Date de création au format ISO
}