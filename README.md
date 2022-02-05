# Surveillance Server
An FTP server combined with Telegram bot: receiving photos from video cameras and sending them into Telegram.

Allows keeping the cameras in the private network behind NAT with no need to provide access to them from the Internet.

The cameras detect movement and send photos to the server and the server re-sends them to the trusted Telegram users.

# Development Environment
The project is in Python 3.10.

Dependency management is done with Poetry.

Please see Poetry documentation on how to initialize the virtual environment.

Please create .env file in the root directory of the project based on .env.example.

Run main.py inside src directory as the server startup point.

Use docker_build.sh to build a docker image.

# Deploying with Docker

Either build your own image or use the existing one: mviktorov/surv_server.

The project contains FTP server.

FTP uses two data channels: (1) for commands and (2) for the data transfer.
FTP server always listens for connections for the command channel.

But for the data channel there are two variants:
1. active/PORT - client provides its IP address and port for the server to connect to it; 
2. passive/PASV - server creates another listening socket on some port and provides IP and port
to the client and the client connects to the server.

Usually the network cameras are behind NAT and for the safety it makes sense to avoid 
connecting to them from the Internet. This means we need passive FTP mode - 
the cameras connect to the server for the data transfer.

The FTP server is going to be executed inside a Docker container for the deployment 
simplicity and it needs the following ports to be exposed on the host machine:
1. commands port - usually 21 or 2121;
2. passive data connection port range - it can be something like 60000 - 60300.

Deployment depends on the concrete use case but here are the instructions for a simple
variant:
1. Obtain a virtual machine at one of cloud providers.

I tested for Digital Ocean.
- OS: Ubuntu 20.04
- RAM: 1GB
- Root disk: 25GB (can be less).
- Make an additional disk for the photo/data storage and mount it to /data.

An additional disk is needed to avoid problems if filling the whole root disk occasionally 
(the system will not be able to boot, login is blocked e.t.c.).

Mount the disk to /data using instructions for your cloud provider.
Add the mount instructions to /etc/fstab.

2. In the firewall at the cloud provider open TCP ports: 
22 (SSH), 2121 (FTP commands), 60000 - 60300 (FTP data).
3. Install Docker to Ubuntu.
You can use any of the tutorials available through Google.
4. Change Docker data dir to the separate disk and disable userland-proxy. 
   - Stop Docker: `service docker stop` 
   - Edit /etc/docker/daemon.json to be:
   ```json
    {
      "data-root": "/data/docker",
      "userland-proxy": false
    }
    ```
   - Create `/data/docker` dir owned by root. 
   - Start Docker: `service docker start`. 
   
Keeping data in a separate disk is good for avoiding the root disk overfilling.
Disabling userland proxy - is a workaround for this problem:
https://github.com/moby/moby/issues/14288

The FTP server requires publishing large port range to the host machine
and it appeared that with userland proxy enabled Docker hangs the machine 
and makes the processes being killed by OutOfMemory.

5. Create a directory for the SurvServer data and deployment scripts:
```mkdir /data/surv_server```
6. Get external IP address of this machine:
```curl ifconfig.me```
7. Create a Telegram bot:
- In Telegram talk to BotFather bot: /newbot .
- Enter the bot name ending with "Bot".
- BotFather will respond with your bot token which you need to enter
in .env file.
8. Create and configure /data/surv_server/.env file:
```
SURV_SERVER_FTP_BIND_HOST=0.0.0.0
SURV_SERVER_FTP_BIND_PORT=2121
SURV_SERVER_FTP_UPLOAD_USER=user
SURV_SERVER_FTP_UPLOAD_PASSWORD=password
SURV_SERVER_DATA_DIR=/data
SURV_SERVER_TELEGRAM_BOT_TOKEN="1234567890:QWERTYUIOPOIUYTREWQ"
SURV_SERVER_TELEGRAM_BOT_ADMIN=your_telegram_name
SURV_SERVER_FTP_LOG_LEVEL=DEBUG
SURV_SERVER_FTP_NAT_ADDRESS=external_ip_address_of_this_machine
SURV_SERVER_FTP_PASSIVE_PORTS_FROM=60000
SURV_SERVER_FTP_PASSIVE_PORTS_TO=60300

```
9. Create the deployment script `/data/surv_server/install.sh`:
```shell
#!/bin/bash

docker pull mviktorov/surv_server:latest
docker stop surv_server
docker rm -f surv_server
docker run --detach \
           --restart always \
           --publish 2121:2121 \
           --publish 60000-60300:60000-60300 \
           --name surv_server \
           -v /data/surv_server/.env:/.env \
           -v /data/surv_server/data:/data \
           mviktorov/surv_server:latest

```
10. Run the deployment script.
11. Check docker logs:
```docker logs -f surv_server```
12. Search for your new bot in Telegram and start talking to it.
13. Configure your IP cameras to upload images to this FTP server
when a motion has been detected.
14. When a new image is uploaded to FTP the bot should re-send it to you.
15. You are the bot admin and you can allow the bot sending photo to other users:
```
/add_user telegram_user_name
/remove_user telegram_user_name
/list_users
```
After you added a user with `/add_user` - this user can find the bot in Telegram
and start talking to it.
The bot stores the chat and starts sending the images to this user as well.

If a user, who is not added by admin, tries to connect to the bot - 
it will respond that the bot is private and will not send images.



