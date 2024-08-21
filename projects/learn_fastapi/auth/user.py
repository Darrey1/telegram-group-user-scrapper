from datetime import timedelta , datetime
from typing import Annotated,Optional,Any
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, HTTPException,status, APIRouter
from pydantic import BaseModel
from starlette import status
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.table import Registration,Books
from sqlmodel import select
import bcrypt


SECRET_KEY = "535000$x6IN/FYr1vXZZJEK$bdfKb/nIQIPIYULWvdBtGrCGIiXIq8OmUArGb6clh97"
ALOGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  
# db_dependency = Annotated[AsyncSession, Depends(get_session)]

# db = {
#     "paul":{
#       "username":"pythondev",
#       "full_name":"Dare Timileyin",
#       "email": "daretimileyin1@gmail.com",
#       "hashed_password":"$2b$12$u3NxMkSA0EUfWkEGUvN/v.mvj/oJtY0ZtxhAQckqTd.m6JyXtIX7W",
#       "disabled":False
#     }
# }

class Data(BaseModel):
    name:str
    
class Token(BaseModel):
    access_token:str
    token_type:str
    

class TokenData(BaseModel):
    username:str|None = None 

class User(BaseModel):
    username:str
    email:str | None = None
    full_name:str | None = None
    disabled: bool | None = None
    hashed_password:str
    
class UserIndb(User):
    hashed_password:str
    
class CreateUserRequest(BaseModel):
    username:str
    password:Optional[str | Any] = Any
    email:str
    full_name:str
    disabled:bool | None = False
    
class Profile(BaseModel):
    username: str
    email:str
    full_name:str
    account_disable:bool


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl= "auth/token")

async def verify_password(plain_password, hashed_password):
    # return pwd_context.verify(plain_password, hashed_password
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password_bytes)

def get_password_hash(password):
    # return pwd_context.hash(password)
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password


async def get_user(username:str,session:AsyncSession=Depends(get_session)):
    print("username",username)
    user = select(Registration).where(Registration.username == username)
    print(user)
    result = await session.exec(user)
    user_data = result.one_or_none()
    
    if user_data is not None:
        print(user_data.__dict__)
        return UserIndb(**user_data.__dict__)



async def authenticate_user(username:str, password:str,session:AsyncSession=Depends(get_session)):
    user = await get_user(username,session) 
    if not user:
        return False
    print(user.hashed_password)
    if not  await verify_password(password, user.hashed_password):
        return False
    
    return user


async def create_access_token(data:dict, expire_delta:timedelta | None = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.now() + expire_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
        
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALOGORITHM)
    return encoded_jwt


async def get_current_user(token:str = Depends(oauth_2_scheme),session:AsyncSession = Depends(get_session)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try:
        print("token",token)
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALOGORITHM])
        username:str = payload.get("sub")
        if not username:
            raise credential_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception 
    
    user = await get_user(token_data.username,session)
    print(user)
    if user is None: 
        print("hello")
        raise credential_exception
    
    return user


async def get_current_active_user(current_user:UserIndb = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


@router.post("/", status_code=status.HTTP_201_CREATED,response_model=Registration)
async def create_user(create_user_request:CreateUserRequest,session:AsyncSession = Depends(get_session)):
    create_user_model = Registration(
       username = create_user_request.username,
       email= create_user_request.email,
       full_name= create_user_request.full_name,
       disabled = create_user_request.disabled,
       hashed_password = get_password_hash(create_user_request.password)
    )
    print(create_user_model)
    session.add(create_user_model)
    await session.commit()
    await session.refresh(create_user_model)
    return create_user_model


@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:OAuth2PasswordRequestForm= Depends(),session:AsyncSession=Depends(get_session)):
    users = await authenticate_user(form_data.username,form_data.password,session)
    if not users:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate":"Bearer"})
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub":users.username}, expire_delta=access_token_expires)
    return {"access_token":access_token, "token_type":"bearer"} 


@router.get("/users/me")
async def read_users_me(current_user:User = Depends(get_current_active_user),session: AsyncSession = Depends(get_session)):
    
    return current_user

@router.get("/user/me/items")
async def read_own_items(current_user:User=Depends(get_current_active_user),session: AsyncSession = Depends(get_session)):
    query = select(Books)
    result = await session.exec(query)
    books = result.fetchall()
    if books:
        return books
    
    
@router.get("/users/profile")
async def read_users_me(current_user:User = Depends(get_current_active_user),session: AsyncSession = Depends(get_session)):
    user_profile = Profile(
        username = current_user.username,
        email = current_user.email,
        full_name= current_user.full_name,
        account_disable = current_user.disabled
    )
    return user_profile

# import asyncio
# password = input("enter your password:")
# hash_p = get_password_hash("darrey327739")
# print(hash_p)
    