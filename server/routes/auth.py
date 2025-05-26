from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse
from services.security import get_password_hash, verify_password, create_access_token
from settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from models.strategy import Strategy

auth_router = APIRouter()


def get_token_from_cookie(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return token


def get_current_user(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Authorization error")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@auth_router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists")

    hashed = get_password_hash(user.password)
    new_user = User(username=user.username, email=user.email, password=hashed)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    ml_strategies = [
        Strategy(
            user_id=new_user.id,
            title="Random Forest Strategy",
            strategy_type="ml_rf",
            buy_signals=[],
            sell_signals=[],
            signal_logic="AND",
            confirmation_candles=1,
            order_type="market",
            use_notional=False,
            trade_amount=100,
            use_balance_percent=False,
            stop_loss=None,
            take_profit=None,
            sl_tp_is_percent=True,
            default_timeframe="1H",
            market_check_frequency="1 Hour",
            automation_mode="NotifyOnly",
            is_enabled=False
        ),
        Strategy(
            user_id=new_user.id,
            title="TensorFlow Strategy",
            strategy_type="ml_tf",
            buy_signals=[],
            sell_signals=[],
            signal_logic="AND",
            confirmation_candles=1,
            order_type="market",
            use_notional=False,
            trade_amount=100,
            use_balance_percent=False,
            stop_loss=None,
            take_profit=None,
            sl_tp_is_percent=True,
            default_timeframe="1H",
            market_check_frequency="1 Hour",
            automation_mode="NotifyOnly",
            is_enabled=False
        )
    ]

    db.add_all(ml_strategies)
    db.commit()

    return {"message": "✅ Registration successful", "user_id": new_user.id}


@auth_router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Ищем либо по email, либо по username
    user = (
        db.query(User)
        .filter((User.email == form_data.username) | (User.username == form_data.username))
        .first()
    )

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # В проде ставим True
        samesite="Lax",
        max_age=60 * 60 * 24
    )
    return response


@auth_router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@auth_router.get("/refresh")
def refresh_token(
    request: Request,
    response: Response,
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if not email:
            raise HTTPException(status_code=401, detail="Unauthorized")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_token = create_access_token(data={"sub": user.email})

        response.set_cookie(
            key="access_token",
            value=new_token,
            httponly=True,
            secure=False,  # True в проде!
            samesite="Lax",
            max_age=60 * 60 * 24
        )
        return {"message": "Token refreshed"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@auth_router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token")
    return response