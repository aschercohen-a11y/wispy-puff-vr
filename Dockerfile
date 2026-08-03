# Wispy Puff VR — hébergement statique via nginx
FROM nginx:alpine

# Sert les fichiers du jeu (index.html, game.js, assets/, vendor/)
COPY . /usr/share/nginx/html

# WebXR + modules JS : bons types MIME, et SURTOUT revalidation systematique.
# Sans en-tete Cache-Control, les navigateurs appliquent un cache heuristique :
# le casque Quest pouvait servir d anciens .glb tout en ayant la nouvelle page,
# donnant un rendu degrade impossible a diagnostiquer. "no-cache" ne desactive
# pas le cache, il force juste a revalider : un fichier inchange repond 304
# (quelques centaines d octets), donc le cout est negligeable et on ne peut
# plus jamais melanger ancienne et nouvelle version.
RUN printf 'server {\n\
  listen 80;\n\
  root /usr/share/nginx/html;\n\
  index index.html;\n\
  add_header Cache-Control "no-cache" always;\n\
  location / { try_files $uri $uri/ /index.html; }\n\
  types {\n\
    text/html html;\n\
    application/javascript js mjs;\n\
    text/css css;\n\
    image/png png;\n\
    image/jpeg jpg jpeg;\n\
    image/webp webp;\n\
    model/gltf-binary glb;\n\
    application/json json;\n\
    audio/mpeg mp3;\n\
  }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
