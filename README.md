# bizops-ai

docker build -t bizops-ai-datasource .

docker run --env-file creds.env -it --entrypoint /bin/bash bizops-ai-datasource

docker run --env-file creds.env -it bizops-ai-datasource

docker run -e TZ=America/Sao_Paulo --name bizops-ai-datasource bizops-ai-datasource

docker logs -f bizops-ai-datasource

# export $(grep -v '^#' creds.env | sed "s/^'\(.*\)'$/\1/;s/^\(.*\)='\(.*\)'/\1=\2/" | xargs)
# apt install vim -y