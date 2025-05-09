# Étape 1 : Build de l'application Angular
FROM node:18 AS builder

# Créer un dossier de travail
WORKDIR /client

# Copier les fichiers package
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste du code Angular
COPY . .

# Builder en mode production
RUN npm run build

# Étape 2 : Servir l'app avec Nginx
FROM nginx:alpine

# Supprimer le contenu par défaut de Nginx
RUN rm -rf /usr/share/nginx/html/*

# Copier le build Angular dans le dossier Nginx
COPY --from=builder /client/dist/* /usr/share/nginx/html

# Copier un fichier Nginx personnalisé si besoin (optionnel)
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]