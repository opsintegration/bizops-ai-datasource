# bizops-ai

docker build -t bizops-ai-datasource .

docker run -it --entrypoint /bin/bash bizops-ai-datasource

docker run -d --name bizops-ai-datasource
docker run --env-file creds.env -it --entrypoint /bin/bash bizops-ai-datasource
docker logs -f bizops-ai-datasource-container

# export $(grep -v '^#' creds.env | sed "s/^'\(.*\)'$/\1/;s/^\(.*\)='\(.*\)'/\1=\2/" | xargs)
# apt install vim -y