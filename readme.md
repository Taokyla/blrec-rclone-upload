# 通过 Docker Compose 部署

```yaml
version: "3.7"
services:
  blrec-rclone-upload:
    restart: unless-stopped
    image: ghcr.io/taokyla/blrec-rclone-upload:latest
    environment:
      - RECORD_REPLACE_DIR=/rec
      # blrec的前置路径，如果blrec在docker里用默认值即可
      - RECORD_SOURCE_DIR=/rec 
      # 当前docker的映射路径
      - RECORD_DESTINATION_DIR=onedrive:record 
      # rclone的远程推送路径
    volumes:
      - '~/.config/rclone:/config/rclone'
      # rclone的配置文件
      - '~/bilibili_record:/rec'  
      # 录像的真实所在路径，一定要有权限
    container_name: blrec-rclone-upload
    ports:
      - "8000:8000"
```

复制上面的内容到 `docker-compose.yml` 文件中

```bash
docker compose up -d
```

创建rclone配置
```bash
docker exec -it blrec-rclone-upload bash -c "rclone config"
```
