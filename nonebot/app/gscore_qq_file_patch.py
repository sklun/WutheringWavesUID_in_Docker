import base64
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Union

import aiohttp

try:
    from nonebot.log import logger
except Exception:  # pragma: no cover - local unit tests do not need NoneBot.
    import logging

    logger = logging.getLogger(__name__)


LINK_PREFIX = "link://"
LOCAL_PREFIX = "local://"
BASE64_PREFIX = "base64://"
QQ_FILE_PREFIX = "qqfile://"
LOCAL_FILE_ROOT = Path(os.getenv("GSCORE_SHARED_DATA_PATH", "/gsuid_core/data"))
LOCAL_IMAGE_CACHE_ROOT = Path(
    os.getenv("GSCORE_SHARED_IMAGE_CACHE_PATH", "/gsuid_core/data/onebot_shared/images")
)
_ORIGINAL_ONEBOT_SEND = None


def parse_file_payload(file_data: str) -> Tuple[str, str]:
    if file_data.startswith(QQ_FILE_PREFIX):
        file_data = file_data[len(QQ_FILE_PREFIX) :]
    file_name, file_content = file_data.split("|", 1)
    return Path(file_name).name, file_content


def _strip_base64_prefix(file_content: str) -> str:
    if file_content.startswith(BASE64_PREFIX):
        return file_content[len(BASE64_PREFIX) :]
    return file_content


async def download_file_to_path(url: str, path: Path) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            path.write_bytes(await response.read())


def write_base64_file_to_path(file_content: str, path: Path) -> None:
    path.write_bytes(base64.b64decode(_strip_base64_prefix(file_content)))


def build_link_fallback_text(file_name: str, file_content: str) -> Optional[str]:
    if file_content.startswith(LINK_PREFIX):
        url = file_content[len(LINK_PREFIX) :]
        return f"QQ文件上传失败，请使用下载链接：\n{file_name}\n{url}"
    return None


def build_qq_upload_notice_text(file_name: str) -> str:
    return f"正在通过QQ发送文件：{file_name}\n大文件可能需要一点时间，请稍候。"


def build_onebot_image_file(image_data: Union[str, bytes]) -> str:
    if isinstance(image_data, bytes):
        return f"{BASE64_PREFIX}{base64.b64encode(image_data).decode('ascii')}"

    if image_data.startswith(LINK_PREFIX):
        return image_data[len(LINK_PREFIX) :]
    if image_data.startswith((BASE64_PREFIX, "http://", "https://")):
        return image_data
    return f"{BASE64_PREFIX}{image_data}"


def is_napcat_sent_timeout(exc: Exception) -> bool:
    message = " ".join(
        str(part)
        for part in (
            getattr(exc, "message", ""),
            getattr(exc, "wording", ""),
            str(exc),
        )
        if part
    )
    return (
        "Timeout: NTEvent serviceAndMethod:NodeIKernelMsgService/sendMsg" in message
        and '"result": 0' in message
        and '"errMsg": ""' in message
    )


def is_explicit_qq_file_delivery(content: Optional[List]) -> bool:
    if not content:
        return False
    return any(
        getattr(segment, "type", None) == "file"
        and isinstance(getattr(segment, "data", None), str)
        and segment.data.startswith(QQ_FILE_PREFIX)
        for segment in content
    )


def build_message_return_timeout_error(exc: Exception) -> TimeoutError:
    return TimeoutError(
        "OneBot消息发送返回超时：NapCat sendMsg 已返回 result=0，"
        "但 NoneBot 未收到正常回执，请检查 QQ 客户端是否实际展示消息。"
    )


def resolve_local_file_uri(file_content: str) -> Path:
    path = Path(file_content[len(LOCAL_PREFIX) :]).resolve()
    root = LOCAL_FILE_ROOT.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"local file path is outside shared root: {path}") from exc
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


async def _materialize_file(file_name: str, file_content: str, temp_dir: Path) -> Path:
    path = temp_dir / file_name
    if file_content.startswith(LINK_PREFIX):
        await download_file_to_path(file_content[len(LINK_PREFIX) :], path)
    else:
        write_base64_file_to_path(file_content, path)
    return path


async def upload_onebot_file(
    bot,
    target_id: str,
    target_type: Optional[str],
    file_data: str,
) -> None:
    file_name, file_content = parse_file_payload(file_data)
    target = int(target_id)
    if file_content.startswith(LOCAL_PREFIX):
        path = resolve_local_file_uri(file_content)
        await _upload_onebot_path(bot, target, target_type, path, file_name)
        return

    with tempfile.TemporaryDirectory(prefix="gscore_onebot_file_") as temp:
        path = await _materialize_file(file_name, file_content, Path(temp))
        await _upload_onebot_path(bot, target, target_type, path, file_name)


async def _upload_onebot_path(
    bot,
    target: int,
    target_type: Optional[str],
    path: Path,
    file_name: str,
) -> None:
    if target_type == "group":
        await bot.call_api(
            "upload_group_file",
            file=str(path.absolute()),
            name=file_name,
            group_id=target,
        )
    else:
        await bot.call_api(
            "upload_private_file",
            file=str(path.absolute()),
            name=file_name,
            user_id=target,
        )


def get_bytes_from_base64_str(data_str: str) -> bytes:
    return base64.b64decode(_strip_base64_prefix(data_str))


def to_json(msg: list, name: str, uin: str):
    return {
        "type": "node",
        "data": {"name": name, "uin": uin, "content": msg},
    }


async def onebot_send(
    bot,
    content: Optional[List],
    target_id: Optional[str],
    target_type: Optional[str],
):
    if is_explicit_qq_file_delivery(content):
        return await qq_file_onebot_send(bot, content, target_id, target_type)
    if _ORIGINAL_ONEBOT_SEND is None:
        logger.warning("[gscore] 原生OneBot发送函数未保存，回退到兼容发送逻辑")
        return await qq_file_onebot_send(bot, content, target_id, target_type)
    return await _ORIGINAL_ONEBOT_SEND(bot, content, target_id, target_type)


async def qq_file_onebot_send(
    bot,
    content: Optional[List],
    target_id: Optional[str],
    target_type: Optional[str],
):
    if target_id is None or content is None:
        return
    target = int(target_id)

    from nonebot.adapters.onebot.v11 import MessageSegment

    async def _send_node(messages):
        if target_type == "group":
            await bot.call_api(
                "send_group_forward_msg",
                group_id=target,
                messages=messages,
            )
        else:
            await bot.call_api(
                "send_private_forward_msg",
                user_id=target,
                messages=messages,
            )

    async def _send_text_now(text: str) -> None:
        if target_type == "group":
            await bot.call_api(
                "send_group_msg",
                group_id=target,
                message=[MessageSegment.text(text)],
            )
        else:
            await bot.call_api(
                "send_private_msg",
                user_id=target,
                message=[MessageSegment.text(text)],
            )

    async def to_msg(gsmsgs: List):
        message = []
        for segment in gsmsgs:
            if not segment.data:
                continue
            if segment.type == "text":
                message.append(MessageSegment.text(segment.data))
            elif segment.type == "image":
                message.append(MessageSegment.image(build_onebot_image_file(segment.data)))
            elif segment.type == "node":
                temp_data = [_make_gs_message(item) for item in segment.data]
                send_forward = [
                    to_json(
                        await to_msg([node_msg]),
                        "小助手",
                        str(2854196310),
                    )
                    for node_msg in temp_data
                ]
                await _send_node(send_forward)
            elif segment.type == "file":
                file_name, file_content = parse_file_payload(segment.data)
                try:
                    await _send_text_now(build_qq_upload_notice_text(file_name))
                except Exception as exc:
                    if is_napcat_sent_timeout(exc):
                        logger.warning(
                            "[gscore] QQ文件发送提示返回超时：NapCat sendMsg "
                            "返回result=0，按已提交发送处理。"
                        )
                    else:
                        logger.warning(f"[gscore] QQ文件发送提示发送失败: {exc}")
                try:
                    await upload_onebot_file(
                        bot,
                        target_id,
                        target_type,
                        segment.data,
                    )
                except Exception as exc:
                    if is_napcat_sent_timeout(exc):
                        logger.warning(
                            "[gscore] QQ文件上传返回超时：NapCat sendMsg "
                            "返回result=0，按已提交上传处理。"
                        )
                        continue
                    logger.exception("[gscore] OneBot文件上传失败")
                    fallback_text = build_link_fallback_text(file_name, file_content)
                    if fallback_text:
                        message.append(MessageSegment.text(fallback_text))
            elif segment.type == "at":
                message.append(MessageSegment.at(segment.data))
            elif segment.type == "record":
                message.append(
                    MessageSegment.record(get_bytes_from_base64_str(segment.data))
                )
        return message

    result_msg = await to_msg(content)
    if result_msg:
        try:
            if target_type == "group":
                await bot.call_api(
                    "send_group_msg",
                    group_id=target,
                    message=result_msg,
                )
            else:
                await bot.call_api(
                    "send_private_msg",
                    user_id=target,
                    message=result_msg,
                )
        except Exception as exc:
            if is_napcat_sent_timeout(exc):
                raise build_message_return_timeout_error(exc) from exc
            raise


def _make_gs_message(data):
    try:
        from GenshinUID.models import Message as GsMessage

        return GsMessage(**data)
    except Exception:
        class _Message:
            def __init__(self, type=None, data=None):
                self.type = type
                self.data = data

        return _Message(**data)


def install_patch() -> bool:
    global _ORIGINAL_ONEBOT_SEND

    try:
        from nonebot import get_driver

        get_driver()
    except Exception:
        return False

    try:
        import GenshinUID.client as client
    except Exception as exc:
        logger.warning(f"[gscore] GenshinUID文件上传补丁加载失败: {exc}")
        return False

    _ORIGINAL_ONEBOT_SEND = getattr(
        client,
        "_gscore_original_onebot_send",
        client.onebot_send,
    )
    client._gscore_original_onebot_send = _ORIGINAL_ONEBOT_SEND
    client.onebot_send = onebot_send
    logger.info("[gscore] 已启用OneBot QQ文件上传显式通道补丁")
    return True


install_patch()
