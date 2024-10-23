# bizops-ai-datasource

# Build the Docker image
docker build -t bizops-ai-datasource .

# Run the Docker container
container_id=$(docker run -d --name bizops-ai-datasource bizops-ai-datasource)

# Wait for the container to finish
docker wait $container_id

# Remove the container
docker rm -f $container_id

# Optionally, remove the image, don't put in airflow
docker rmi bizops-ai-datasource