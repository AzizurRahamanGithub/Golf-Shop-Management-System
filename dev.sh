echo "remove previous containers"
docker-compose -p django_dev -f docker/docker-compose.dev.yml down -v

echo "Remove unused images for django project only"
docker image prune -f --filter label=com.docker.compose.project=django_dev

echo "Starting in DEVELOPMENT mode..."
docker-compose -p django_dev -f docker/docker-compose.dev.yml up -d --build

echo "Compose is ready for development mode"

#run command 
# chmod +x dev.sh

# ./dev.sh dev
