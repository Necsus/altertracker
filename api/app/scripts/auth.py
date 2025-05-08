import requests

def get_token() -> str:
    url = "https://www.altered.gg/api/auth/session"
    try:
        # Effectuer une requête GET vers l'URL
        response = requests.get(url)
        
        # Vérifier si la requête a réussi (code 200)
        response.raise_for_status()
        
        # Récupérer les données au format JSON
        data = response.json()
        
        # Test si le token d'accès est présent dans la réponse
        if 'accessToken' not in data:
            return generate_token()
        return data.accessToken
    except requests.exceptions.RequestException as e:
        # Gérer les erreurs de requête
        print(f"Erreur lors de la requête : {e}")
        return None
    
def generate_token() -> str:
    # TODO ne pas hardcoder le token
    return "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJDMFo0V3JVWE1xT2JtMy1CTU8xRFV5YktidFA2bldLb2VvWmE1UGJuZHhZIn0.eyJleHAiOjE3NDY3MTMzOTgsImlhdCI6MTc0NjcwNjE5OCwiYXV0aF90aW1lIjoxNzQ2NzA2MTk4LCJqdGkiOiI2M2I4NWY5ZC02ZGFlLTRiNGQtOWI0ZS0zYzkzMmZlNDdiMmEiLCJpc3MiOiJodHRwczovL2F1dGguYWx0ZXJlZC5nZy9yZWFsbXMvcGxheWVycyIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiI0Zjc4ZWI5MC01NTRlLTQwYjQtODgzNS01MmYyNjQ3YTgxNzciLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ3ZWIiLCJzaWQiOiIyZWVkZDU5NC00YjQxLTRhMTQtYjBjYi0yZDA2ODZjNTY5OTIiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vYXV0aC5hbHRlcmVkLmdnIiwiaHR0cHM6Ly93d3cuYWx0ZXJlZC5nZyJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib3RwX2VtYWlsIiwiZGVmYXVsdC1yb2xlcy1wbGF5ZXJzIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIHByb2ZpbGUgZW1haWwiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicHJlZmVycmVkX3VzZXJuYW1lIjoianVsaWVuLm1hbGlnZUBob3RtYWlsLmZyIiwiZW1haWwiOiJqdWxpZW4ubWFsaWdlQGhvdG1haWwuZnIifQ.STHTordcMPLLuzxRff8gevASNVeipztAy2XmaaTJvBO15vtxFRGSyTHsXLw11eEFy-glDwirFvr1wzxzqZSTmOWYsgTpnnmmrKcGwaE87GrVCScKGUJfsUu1ykf2R8357xA0wWLR6rp5gCxeF3d-6ei7lYjzx1-n1VJCKT08OgWn3UpcRWEAJXUzoaYAaNMZSZqlGqRZK6SuaYO58HN-QkK4sswiHhICfuwqCrAb6vu90QZbvRQ_3fEO_D9lU4oZ7MuuyclStGMf1fk2TPIGHmUxEp75Wx4F_60bjcNNbZnaqa41P248FmSmLttVm61mwU_ueDcJ_8D8ky2t3S2rKA"