from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from starlette.status import HTTP_400_BAD_REQUEST
from sqlalchemy.orm import Session
# custom defined
from app.models.user import UserCreate, User, TokenResponse, UserList
from app.crud.user import get_user_by_name, create_user, get_users, get_user, get_user_count, update_user
from app.dependencies.db import get_db
from app.dependencies.jwt import get_current_user_authorizer
from app.utils.jwt import create_access_token
from app.utils.security import verify_password
from app.core.config import secret_key

router = APIRouter()


@router.post("/users/login", response_model=TokenResponse, tags=["user"], name='用户登录')
async def login(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    dbuser = get_user_by_name(db, name=user.username)
    if not dbuser:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="用户名错误"
        )
    if not verify_password(dbuser.salt + user.password, dbuser.hashed_password):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="密码错误"
        )
    token = create_access_token(data={"id": dbuser.id})
    # swaggerui 要求返回此格式
    return TokenResponse(access_token=token)


@router.post("/users/", response_model=User, tags=["user"], name='添加用户')
def add_user(data: UserCreate = Body(...), db: Session = Depends(get_db),
             user: User = Depends(get_current_user_authorizer())):
    if user.is_admin is False:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='权限不足')
    db_user = get_user_by_name(db, name=data.name)
    if db_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Name already registered")
    return create_user(db=db, user_item=data)


@router.get("/users/", response_model=UserList, tags=["user"], name='用户列表')
def read_users(page: int = 1, size: int = 20, db: Session = Depends(get_db),
               user: User = Depends(get_current_user_authorizer())):
    if user.is_admin is False:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='权限不足')
    users = get_users(db, skip=(page - 1) * size, limit=size)
    count = get_user_count(db)
    return {'data': users, 'total': count}


@router.get("/users/me", response_model=User, tags=["user"], name='用户信息')
def read_user_me(db: Session = Depends(get_db), user: User = Depends(get_current_user_authorizer())):
    db_user = get_user(db, user_id=user.id)
    if db_user is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")
    return db_user


@router.patch("/users/reset/password", response_model=User, tags=["user"], name='密码修改')
def reset_password(new_pass: str = Body(..., embed=True), db: Session = Depends(get_db),
                   user: User = Depends(get_current_user_authorizer())):
    db_user = get_user(db, user_id=user.id)
    if db_user is None:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="User not found")
    update_user(db=db, user_id=user.id, password=new_pass)
    return db_user


@router.post("/users/init", response_model=User, tags=["user"], name='初始化管理员')
def add_admin(data: UserCreate = Body(...), api_key: str = Body(...), db: Session = Depends(get_db)):
    if api_key != secret_key:
        raise HTTPException(HTTP_400_BAD_REQUEST, 'apikey错误')
    db_user = get_user_by_name(db, name=data.name)
    if db_user:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Name already registered")
    data.is_admin = True
    return create_user(db=db, user_item=data)
