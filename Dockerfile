# Wispy Puff VR — hébergement statique via nginx
FROM nginx:alpine

# Sert les fichiers du jeu (index.html, game.js, assets/, vendor/)
COPY . /usr/share/nginx/html

# WebXR + modules JS : on s'assure des bons types MIME et du cache raisonnable
RUN printf 'server {\n\
  listen 80;\n\
  root /usr/share/nginx/html;\n\
  index index.html;\n\
  location / { try_files $uri $uri/ /index.html; }\n\
  types {\n\
    text/html html;\n\
    application/javascript js mjs;\n\
    text/css css;\n\
    image/png png;\n\
    image/jpeg jpg jpeg;\n\
    application/json json;\n\
    audio/mpeg mp3;\n\
  }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
