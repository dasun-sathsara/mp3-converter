from __future__ import annotations

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from db import get_session
from models import TokenResponse, User, UserCreate, ValidateResponse
from security import create_access_token, decode_token, hash_password, verify_password

app = FastAPI(title="Auth Service", version="0.1.0")

security = HTTPBasic()


@app.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, session: Session = Depends(get_session)) -> TokenResponse:
    existing = session.exec(select(User).where(User.email == user_in.email)).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        age=int(user_in.age),
    )

    session.add(user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    session.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token)


def _parse_basic_credentials(credentials: HTTPBasicCredentials) -> tuple[str, str]:
    return credentials.username, credentials.password


@app.post("/login", response_model=TokenResponse)
def login(
    credentials: HTTPBasicCredentials = Depends(security),
    session: Session = Depends(get_session),
) -> TokenResponse:
    email, password = _parse_basic_credentials(credentials)
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token)


@app.post("/validate", response_model=ValidateResponse)
def validate_token(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> ValidateResponse:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = session.get(User, int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token user"
            )
        return ValidateResponse(valid=True, user_id=int(user_id), email=email)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
