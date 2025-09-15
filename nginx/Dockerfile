FROM nginx:alpine

# Instalar dependências adicionais
RUN apk add --no-cache \
    curl \
    tzdata \
    && rm -rf /var/cache/apk/*

# Configurar timezone
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directories for static and media files
RUN mkdir -p /app/static /app/media /var/log/nginx

# Set proper permissions
RUN chown -R nginx:nginx /app /var/log/nginx

# Criar arquivos de log vazios
RUN touch /var/log/nginx/access.log /var/log/nginx/error.log /var/log/nginx/static.log /var/log/nginx/media.log /var/log/nginx/api.log
RUN chown nginx:nginx /var/log/nginx/*.log

# Expose port 80
EXPOSE 80

# Health check otimizado
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
