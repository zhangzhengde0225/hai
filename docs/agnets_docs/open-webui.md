# Open-WebUI

Link: https://github.com/open-webui/open-webui

## 一些问题

- 1.open-webui重复打印：需要注释open-webui源码```utils/middleware.py```中的```post_response_handler```函数中的```tag_content_handler```函数中的：

```python
# if before_tag:
#     content_blocks[-1]["content"] = before_tag
```
- 2.前端的chat_id通过"chat_id"传递给了后端。