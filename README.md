# aicharacter
基于 xiaoapi 的ai角色对话


## 安装
```
pip install -r requirements.txt
pip install -r requirements_webui.txt
```

## 配置
在 application/settings 中 修改以下配置：
```python
SEARCH_SERVER_URL = "http://127.0.0.1:7862"

LLM_MODELS_CONFIG = {
    "openai-api": {
        "model_name": "gpt-4",  # 由接口传入，不会使用这个
        "api_base_url": "https://api.openai.com/v1",
        "api_key": "EMPTY",
    },
}
```


## 初始化数据库
```
python manage.py sqlalchemy create-tables
```


## 启动
### 启动fastapi服务
```
python manage.py run-server
```

### 启动webui
```
streamlit run webui.py
```