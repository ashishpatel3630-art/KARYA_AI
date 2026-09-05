import threading

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.auth.token_hash import hash_refresh_token
from app.core import database as db_module
from app.core.database import Base
from app.main import app
from app.models.session import Session as SessionModel
from app.models.user import User


DATABASE_URL = (
    "postgresql+psycopg://aashishmewada@localhost/karya_test"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def test_concurrent_refresh_endpoint():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # IMPORTANT:
    # tests/conftest.py normally overrides get_db with SQLite.
    # Override it again here so this test uses PostgreSQL.
    app.dependency_overrides[db_module.get_db] = override_get_db

    setup_client = TestClient(app)

    clients = [
        TestClient(app),
        TestClient(app),
    ]

    try:
        # ---------------------------------------------------------
        # 1. Register
        # ---------------------------------------------------------

        register = setup_client.post(
            "/auth/register",
            json={
                "email": "endpoint-concurrency@example.com",
                "password": "StrongPass123!",
            },
        )

        assert register.status_code == 201

        # ---------------------------------------------------------
        # 2. Login
        # ---------------------------------------------------------

        login = setup_client.post(
            "/auth/login",
            json={
                "email": "endpoint-concurrency@example.com",
                "password": "StrongPass123!",
            },
        )

        assert login.status_code == 200

        refresh_token = login.json()["refresh_token"]

        # ---------------------------------------------------------
        # 3. Locate original refresh session
        # ---------------------------------------------------------

        db = SessionLocal()

        try:
            user = db.execute(
                select(User).where(
                    User.email
                    == "endpoint-concurrency@example.com"
                )
            ).scalar_one()

            original_session = db.execute(
                select(SessionModel).where(
                    SessionModel.user_id == user.id,
                    SessionModel.refresh_token_hash
                    == hash_refresh_token(refresh_token),
                )
            ).scalar_one()

            user_id = user.id
            original_session_id = original_session.id
            token_family = original_session.token_family

        finally:
            db.close()

        # ---------------------------------------------------------
        # 4. Send two concurrent refresh requests
        # ---------------------------------------------------------

        barrier = threading.Barrier(2)

        results = []

        def worker(client_index):
            try:
                barrier.wait()

                response = clients[client_index].post(
                    "/auth/refresh",
                    json={
                        "refresh_token": refresh_token,
                    },
                )

                results.append(
                    (
                        client_index,
                        response.status_code,
                        response.json(),
                    )
                )

            except Exception as exc:
                results.append(
                    (
                        client_index,
                        "error",
                        str(exc),
                    )
                )

        thread_1 = threading.Thread(
            target=worker,
            args=(0,),
        )

        thread_2 = threading.Thread(
            target=worker,
            args=(1,),
        )

        thread_1.start()
        thread_2.start()

        thread_1.join(timeout=10)
        thread_2.join(timeout=10)

        # ---------------------------------------------------------
        # 5. Both requests must finish
        # ---------------------------------------------------------

        assert not thread_1.is_alive()
        assert not thread_2.is_alive()

        assert len(results) == 2

        # ---------------------------------------------------------
        # 6. Exactly one request succeeds
        #    and exactly one detects token reuse
        # ---------------------------------------------------------

        status_codes = sorted(
            result[1]
            for result in results
        )

        assert status_codes == [200, 401]

        successful = next(
            result
            for result in results
            if result[1] == 200
        )

        rejected = next(
            result
            for result in results
            if result[1] == 401
        )

        # ---------------------------------------------------------
        # 7. Successful request receives a NEW refresh token
        # ---------------------------------------------------------

        new_refresh_token = (
            successful[2]["refresh_token"]
        )

        assert new_refresh_token != refresh_token

        # ---------------------------------------------------------
        # 8. Losing request detects reuse
        # ---------------------------------------------------------

        assert (
            rejected[2]["detail"]
            == "Refresh token reuse detected"
        )

        # ---------------------------------------------------------
        # 9. Token family must now be revoked
        # ---------------------------------------------------------

        verify_db = SessionLocal()

        try:
            sessions = verify_db.execute(
                select(SessionModel).where(
                    SessionModel.user_id == user_id,
                    SessionModel.token_family
                    == token_family,
                )
            ).scalars().all()

            # Original session + rotated session
            assert len(sessions) >= 2

            # Original session must exist
            assert any(
                session.id == original_session_id
                for session in sessions
            )

            # Replay detection revokes entire family
            assert all(
                session.revoked
                for session in sessions
            )

        finally:
            verify_db.close()

    finally:
        for client in clients:
            client.close()

        setup_client.close()

        # Remove PostgreSQL override
        app.dependency_overrides.clear()

        # Clean test database
        Base.metadata.drop_all(bind=engine)