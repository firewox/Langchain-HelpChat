# @Time  :2024/12/5 19:27
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import os.path
from fastapi import FastAPI,Query,File, UploadFile,Form
from pydantic import BaseModel
from backend.servers.login.login_services import login_services
from backend.servers.history.history_services import history_services # services的处理工具
from backend.servers.knowledge.knowledge_services import knowledge_services # services的处理工具
from backend.configs.backend_config import VECTOR_SEARCH_TOP_K,EMBEDDING_DEVICE,PROMPT_TEMPLATE,BACKEND_SERVER,UPLOAD_ROOT_PATH
from dotenv import load_dotenv
import uvicorn
from fastapi.responses import JSONResponse
from utils.logger import logger
import uuid

# 加载环境变量
dotenv_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(dotenv_path,".env_backend"),override=True)

app = FastAPI()

class historyBaseModel(BaseModel):
    user_id: str="100"
    user_name:str="cell2024"
    history_name: str = "default"

class historyNameList(BaseModel):
    user_id: str="100"

class historySet(BaseModel):
    user_id: str="100"
    user_name:str="cell2024"
    history_name: str = "default"
    messages:list=[]

class loginBaseModel(BaseModel):
    user_name:str=""
    password:str=""

class knowledgeChat(BaseModel):
    user_id:str=""
    knowledge_vector_name:str=""
    prompt:str=""

# 后端请求入口
@app.post("/login")
def login(params:loginBaseModel):
    user_name=params.user_name
    password=params.password
    logger.info(f"\nparams={params}")
    messages = login_services.login(user_name=user_name,password=password)
    logger.info(f"\nmessages={messages}")
    return {"msg":messages}

# GET 处理前端发送来的查询聊天历史记录
@app.post("/get_history_chat")
def get_history_chat(params:historyBaseModel):
    user_id = params.user_id
    user_name = params.user_name
    history_name = params.history_name
    messages = history_services.chatGetHistoryByUsernameAndHistoryName(user_id=user_id,user_name=user_name,history_name=history_name)
    return {"msg":messages}


# GET 处理前端发送来的查询历史聊天记录名称列表的请求
@app.post("/get_history_name_list")
def get_history_name_list(params:historyNameList):
    user_id=params.user_id
    history_name_list = history_services.chatGetHistoryNameList(user_id=user_id)
    return {"msg":history_name_list}

# GET 处理前端发送来的查询历史聊天记录名称列表的请求
@app.post("/set_history_chat")
def set_history_chat(params:historySet):
    user_id=params.user_id
    user_name=params.user_name
    history_name=params.history_name
    messages=params.messages
    history_name_list = history_services.chatSetHistoryByUseridAndHistoryName(user_id=user_id,history_name=history_name,messages=messages)
    return {"msg":history_name_list}

@app.get("/create_new_dialogue")
def create_new_dialogue(user_id:str=Query(...,description="user id"),
                        messages:list=Query(...,description="system prompt系统内置的记录")):
    history_name = history_services.chatCreateNewDialogueByUserId(user_id=user_id,messages=messages)
    return {'msg':history_name}

@app.post("/upload_file")
async def upload_file(
        file: UploadFile = File(...),
        dir_name: str = Form("default"),
        user_id: str = Form(...)
):
    try:
        # 构建保存目录，可以包含用户ID
        upload_dir = os.path.join(UPLOAD_ROOT_PATH, user_id, dir_name)
        os.makedirs(upload_dir, exist_ok=True)
        # 构建文件的完整路径
        file_path = os.path.join(upload_dir, file.filename)
        logger.info(f"\n上传文件file_path={file_path}")
        # 以二进制写模式打开文件，并写入内容
        with open(file_path, "wb") as buffer:
            contents = await file.read()  # 读取上传文件的内容
            buffer.write(contents)  # 写入到新文件
        # 保存文件
        knowledge_services.knowledgeInsertFile(user_id=user_id,dir_name=dir_name,file_name=file.filename)
        return JSONResponse(status_code=200,content={
            "msg": 1,
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={"msg": None})

@app.post("/create_knowledge")
def create_knowledge(dir_name: str = Form("default"),
                     user_id: str = Form(...)):
    fl = knowledge_services.create_knowledge(dir_name=dir_name,user_id=user_id)
    if fl==1:
        return JSONResponse(status_code=200, content={"msg": 1})
    else:
        return JSONResponse(status_code=200, content={"msg": None})

# POST 处理前端发送来的查询所有已经向量化后的知识库列表
@app.get("/get_knowledge_name_list")
def get_knowledge_name_list(user_id:str=Query(..., description="user id")):
    knowledge_name_list = knowledge_services.knowledgeGetKnowledgeNameList(user_id=user_id)
    return {"msg":knowledge_name_list}

# POST 处理前端发送来的知识向量库问答聊天
@app.post("/get_knowledge_chat")
def get_knowledge_chat(params:knowledgeChat):
    # {"user_id":user_id,"knowledge_vector_name":knowledge_vector_name,"prompt":prompt_query}
    user_id = params.user_id
    knowledge_vector_name = params.knowledge_vector_name
    prompt = params.prompt
    prompt_new,_ = knowledge_services.knowledgeChat(user_id=user_id,
                                              knowledge_vector_name=knowledge_vector_name,
                                              prompt=prompt)
    return {"msg":prompt_new}


# 主函数，用于启动 Uvicorn 服务器
if __name__ == "__main__":
    uvicorn.run(app, host=BACKEND_SERVER.get("host","127.0.0.1"), port=int(BACKEND_SERVER.get("port",8601)))
