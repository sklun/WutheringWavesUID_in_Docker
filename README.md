# Docker Compose 搭建 QQ 鸣潮机器人（NoneBot2 + NapCat + GsCore）

## Docker Compose 内容

1. 启动 NapCatQQ 客户端（WebUI 默认端口 `6099`）
2. 部署带 `nonebot-plugin-genshinuid` 的 NoneBot2（端口 `3002`）
3. 部署 GsCore 网页控制台（默认端口 `8765`）
4. （可选）启动 AstrBot（默认端口 `6185` / `9600`）
5. （可选）启动 Shipyard，用于提供 AstrBot 沙盒环境
6. 提供 GsCore、NoneBot、NapCat 之间的共享文件目录，用于 QQ 文件发送


## 部署

1. Docker / Docker Compose 环境安装不再赘述

2. 下载项目

   ```shell
   git clone git@github.com:sklun/WutheringWavesUID_in_Docker.git
   cd WutheringWavesUID_in_Docker
   ```

3. 准备配置文件

   ```shell
   cp nonebot/.env.template nonebot/app/.env
   cp gsuid_core/.env.example gsuid_core/.env
   ```

   - `nonebot/app/.env`：用于配置 OneBot Token、NoneBot 监听地址、GsCore 地址等
   - `gsuid_core/.env`：用于配置端口、Python 源、代理、挂载路径等
   - `.env`、token、密码、Cookie 等敏感信息不要提交到仓库


4. 构建并启动服务

   ```shell
   docker compose up -d --build
   ```

5. 部署完成后的目录结构大致如下

   ```shell
   .
   ├── astrbot
   │   └── data
   ├── compose.yaml
   ├── gscore.Dockerfile
   ├── gsuid_core
   │   └── data
   ├── napcat
   │   ├── config
   │   └── qq_config
   ├── nonebot
   │   ├── app
   │   ├── .env.template
   │   └── Dockerfile
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

        ```env
        PORT=3002
        HOST=0.0.0.0
        GSUID_CORE_HOST=gsuidcore
        GSUID_CORE_PORT=8765
        GSUID_CORE_WS_TOKEN=<按需设置>
        ```

   - `ONEBOT_ACCESS_TOKEN` 需要与 NapCat WebSocket 客户端保持一致
   - `GSUID_CORE_HOST` / `GSUID_CORE_PORT` 对应 compose 中的 `gsuidcore` 服务
   - `GSUID_CORE_WS_TOKEN` 如果启用，请与 GsCore 侧保持一致

   - `gscore_qq_file_patch` 用于补齐 GsCore 到 OneBot 的文件发送链路，优先使用 QQ 文件上传

3. GsCore

   1. 登录 GsCore 网页控制台： `http://127.0.0.1:8765/genshinuid/`，默认账号 `root/root`，进入之后请**务必**修改密码

   3. 可选配置位于 `gsuid_core/.env`，例如：

   - `PORT`
   - `GSCORE_PYTHON_INDEX`
   - `GSCORE_BASE_IMAGE`
   - `GSCORE_HTTP_PROXY`
   - `GSCORE_HTTPS_PROXY`
   - `GSCORE_NO_PROXY`

   4. 安装鸣潮相关插件：在 GsCore 网页控制台的插件管理中安装，或进入 `gsuid_core/gsuid_core/plugins` 插件目录手动安装
    
    - 手动安装示例
      ```shell
      cd gsuid_core/gsuid_core/plugins
      # XutheringWavesUID 鸣潮Bot插件
      git clone -b main https://github.com/Loping151/XutheringWavesUID.git --depth=1 --single-branch
      # RoverSign 鸣潮签到插件
      git clone -b main https://github.com/Loping151/RoverSign.git --depth=1 --single-branch
      # TodayEcho 声骸强化模拟插件
      git clone -b main https://github.com/Loping151/TodayEcho.git --depth=1 --single-branch
      # ScoreEcho 小维OCR识别声骸并评分
      git clone -b main https://github.com/Loping151/ScoreEcho.git --depth=1 --single-branch

      # [已迁移] WutheringWavesUID 鸣潮Bot插件 (可以在 GsCore 网页控制台插件管理中下载)
      # git clone -b master https://github.com/tyql688/WutheringWavesUID.git --depth=1 --single-branch
      # [已迁移] RoverSign 鸣潮签到插件
      # git clone -b main https://github.com/tyql688/RoverSign.git --depth=1 --single-branch
      ```

   5. 鸣潮登录、库街区配置、排行榜 token 等内容以对应插件文档为准

4. AstrBot / Shipyard

   - 有需要自行取消 compose.yaml 中的注释
   - AstrBot 默认暴露端口：`6185`、`9600`
   - Shipyard 默认随 compose 启动，用于提供 AstrBot 沙盒环境
   - `compose.yaml` 中涉及 `ACCESS_TOKEN` 一类的值属于部署密钥，实际使用时建议改成自己的值，不要直接对外公开


## 常用命令

1. 查看服务状态

   ```shell
   docker compose ps
   ```

2. 查看 NapCat 日志

   ```shell
   docker logs -f napcat
   ```

3. 重建并启动全部服务

   ```shell
   docker compose up -d --build
   ```

4. 重启 GsCore

   ```shell
   docker restart gsuidcore
   ```

5. 查看 NoneBot 日志

   ```shell
   docker logs -f nonebot
   ```

6. 查看 GsCore 日志

   ```shell
   docker logs -f gsuidcore
   ```

7. 停止全部服务

   ```shell
   docker compose down
   ```



## 资源/资料

- [早柚核心 Docs](https://docs.sayu-bot.com/)
- [GsCore](https://github.com/Genshin-bots/gsuid_core)
- [NoneBot](https://nonebot.dev/)
- [NapCatQQ](https://napneko.github.io/)
- [AstrBot](https://github.com/Soulter/AstrBot)
- [XutheringWavesUID](https://github.com/Loping151/XutheringWavesUID)
- [RoverSign](https://github.com/Loping151/RoverSign)
- [TodayEcho](https://github.com/Loping151/TodayEcho)
- [ScoreEcho](https://github.com/Loping151/ScoreEcho)
