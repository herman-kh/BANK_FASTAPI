from fastapi import APIRouter, Depends, HTTPException, status, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from data.database import get_async_session
from schemas.base import UserCreate, Registration, UserDataForAutorization, SuccsessfulRegistraionVerify
from config.security import hash_password, verify_password
from services.crud import get_user_by_email, create_user
from services.selector import find_by_username
from services.utils import create_access_token, create_refresh_token, decode_refresh_token
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from config.variables import SecureDict
from config.config import settings
from datetime import datetime, timezone, timedelta
import random

from services.kafka_producer import producer

router = APIRouter(tags=["Auth"])

verification_store = SecureDict(settings.VERIFICATION_CODES_KEY)

@router.post("/register", response_model=Registration, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_async_session)):
    email = payload.email.lower().strip()
    existing_user = await get_user_by_email(db, payload.email)
    existing_username = await find_by_username(payload.username, db)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    if not (14 <= payload.age <= 120):
        raise HTTPException(status_code=400, detail="Age must be between 14 and 120")
    code = random.randint(100000, 999999)

    verification_data = {
        "code": str(code),
        "username": payload.username,
        "password": payload.password,
        "age": payload.age,
        "attempts": 3,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
    }
    

    verification_store[payload.email] = verification_data
    await producer.send_registration_verify_message(email=email, code=code)
    return {"message": "You need to verify your email. We sent code to your email, you should enter it",}
    
@router.post("/register/verify", response_class=JSONResponse)
async def verify_registration(code: int = Query(...), email: EmailStr = Query(...), db: AsyncSession = Depends(get_async_session)):
    verification_data = verification_store.get(email)
    if not verification_data:
        return JSONResponse({"detail": "Code is expired or not exisist"}, status_code=400)
    
    if verification_data["attempts"] <= 0:
        verification_store.pop(email)
        return JSONResponse({"detail": "You have too much attempts. You need another code"}, status_code=400)
    
    if str(code) != verification_data["code"]:
        verification_data["attempts"] -= 1
        verification_store[email] = verification_data
        return JSONResponse({
            "detail": f"Code is wrong! Remaining attempts {verification_data["attempts"]}"
        }, status_code=400)
    


    result = await create_user(db,
        username=verification_data["username"],
        password=verification_data["password"],
        email=email,
        age=verification_data["age"],
    )
    
    verification_store.pop(email)
    await producer.send_user_created(user_id=result.id, email=result.email)
    if not result:
        return JSONResponse({"detail": "Error during user creation"}, status_code=500)
    
    return JSONResponse({"detail": "User susseccfully registrated",})


@router.post("/auth", response_class = JSONResponse)
async def login(form_data: UserDataForAutorization, db: AsyncSession = Depends(get_async_session)):
    user = await find_by_username(form_data.username, db) 
    id_password_verify = await verify_password(form_data.password, user.hashed_password)
    if user.email != form_data.email or not id_password_verify:
        raise HTTPException(status_code=400, detail='Data is incorrect!')
    access_token = create_access_token({"sub": user.email, 'id':user.id, "status": user.status})
    refresh_token = create_refresh_token({'sub': user.email, 'id':user.id, "status": user.status})
    return {'access_token':access_token,
            'refresh_token':refresh_token,
             "token_type": "bearer"
            }

@router.post("/refresh", response_class=JSONResponse)
async def refresh(refresh_token: str = Form(...), db: AsyncSession = Depends(get_async_session)):
    payload = decode_refresh_token(refresh_token)
    if not payload:
        return JSONResponse({"detail": "Invalid refresh_token"}, status_code=401)
        
    username = payload.get("sub")
    if not username:
        return JSONResponse({"detail": "Invalid refresh_token"}, status_code=401)
    
    user_id = payload.get("id")
    if not user_id:
        return JSONResponse({"detail": "Invalid refresh_token"}, status_code=401)
    
    user_status = payload.get("status")
        
    user = await get_user_by_email(db, username)
    if not user:
        return JSONResponse({"detail": "User not found"}, status_code=404)
    
  
    token_data = {"sub": username, 'id': user_id, 'status': user_status}
        
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
