server {
    listen 80;
    server_name csscrusaders.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
    }

}