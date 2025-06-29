for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo service docker start

sudo service docker enable

sudo tee /etc/docker/daemon.json <<-'EOF'
{
    "registry-mirrors": [
        "https://docker.xuanyuan.run",
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com"
    ]
} 
EOF

sudo systemctl daemon-reload && sudo systemctl restart docker

sudo docker pull hello-world

# hades@Hades:~/DataFlow$ docker images
# REPOSITORY       TAG       IMAGE ID       CREATED        SIZE
# node             22.17.0   b0a29cf1eca0   4 days ago     1.12GB
# elasticsearch    9.0.2     326d884a38b1   3 weeks ago    1.37GB
# python           3.12.11   8c5092866cc6   3 weeks ago    1.02GB
# redis            latest    c09c2832ba40   4 weeks ago    128MB
# amazoncorretto   24        cd580064eb54   7 weeks ago    526MB
# mysql            latest    103520d778e4   2 months ago   859MB
# apache/kafka     latest    12b98f0f2c1f   3 months ago   425MB
# openjdk          24        2362924ff4da   4 months ago   597MB

sudo docker pull node:22.17.0
sudo docker pull elasticsearch:9.0.2
sudo docker pull python:3.12.11
sudo docker pull redis:latest
sudo docker pull amazoncorretto:24
sudo docker pull mysql:latest
sudo docker pull apache/kafka:latest
sudo docker pull openjdk:24
