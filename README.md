# Docker Compose 搭建 QQ 鸣潮机器人（NoneBot2 + NapCat + GsCore）

## Docker Compose 内容

1. 部署包含 nonebot-plugin-genshinuid 的 NoneBot2 环境
2. 启动 NapCatQQ 客户端
3. 部署 GsCore



## 部署

1. Docker 环境安装不再赘述

2. 下载项目

   ```shell
   git clone https://github.com/sklun/WutheringWavesUID_in_Docker.git
   ```

3. 构建 NoneBot 镜像

   ```shell
   cd WutheringWavesUID_in_Docker/nonebot
   docker build -t nonebot .   ```

4. 启动 Docker compose

   ```shell
   cd ..
   docker compose up -d
   ```

5. 部署完成后的目录结构

   ```shell
   .
   ├── compose.yaml
   ├── gscore
   │   ├── gscore_data
   │   └── gscore_plugins
   ├── napcat
   │   ├── config
   │   └── qq_config
   ├── nonebot
   │   ├── app
   │   └── Dockerfile
   └── README.md
   ```

 ## 配置

1. NapCat

   1. 获取 WebUI token

   - 可以通过`docker logs napcat`查看容器日志，在其中找到形如 `[WebUI] WebUI Local Panel Url: http://127.0.0.1:6099/webui?token=xxxx` 的 token 信息。

   - 也可打开 napcat/config/webui.json 文件，在其中找到 token。

   2. 登录 WebUI `http://127.0.0.1:6099/webui/`，进行如下操作：

   - 进入 QQ 登录，点击 `QRCode` 进行二维码登录

   - 登录成功后，进入网络配置，点击 "新建" 创建 `Websocket 客户端`，URL 填写 `ws://nonebot:3002/onebot/v11/ws`， Token 自行设置，点击启用后保存

2. NoneBot

   - 配置文件模板 `WutheringWavesUID_in_Docker/nonebot/.env.template` 将该文件复制到 `nonebot/app` 目录下并重命名为 `.env`（注意该目录不要保留 .env.template）

   - 将创建 Websocket 客户端 时填写的 `Token` 写入配置文件 `WutheringWavesUID_in_Docker/nonebot/app/.env` 中 `ONEBOT_ACCESS_TOKEN=设置的token`


3. GsCore

   1. 登录 GsCore 网页控制台： `http://127.0.0.1:8765/genshinuid/`，默认账号 `root/root`，进入之后请**务必**修改密码

   2. 进入目录 `gscore/gscore_plugins`，下载鸣潮插件

      ```shell
      # XutheringWavesUID 鸣潮Bot插件
      git clone -b main https://github.com/Loping151/XutheringWavesUID.git --depth=1 --single-branch
      # RoverSign 鸣潮签到插件
      git clone -b main https://github.com/tyql688/RoverSign.git --depth=1 --single-branch

      # [已迁移] WutheringWavesUID 鸣潮Bot插件 (可以在 GsCore 网页控制台插件管理中下载)
      # git clone -b master https://github.com/tyql688/WutheringWavesUID.git --depth=1 --single-branch
      ```

   3. 下载完成后重启 GsCore

      ```shell
      docker restart gsuidcore
      ```

4. 鸣潮插件配置

   1. 登录 GsCore 网页控制台，进入`插件管理/修改插件设定`
   2. 进入 WutheringWavesUID 配置

   3. 库街区登录配置参照插件[补充文档地址](https://wiki.wavesuid.top/)中的"鸣潮登录帮助"


## 资源/资料

- [早柚核心Docs](https://docs.sayu-bot.com/)
- ~~[鸣潮插件](https://github.com/tyql688/WutheringWavesUID)~~ 已迁移至 [鸣潮插件](https://github.com/Loping151/XutheringWavesUID)
- [鸣潮签到插件](https://github.com/tyql688/RoverSign)
- [NoneBot](https://nonebot.dev/)
- [NapCatQQ](https://napneko.github.io/)
