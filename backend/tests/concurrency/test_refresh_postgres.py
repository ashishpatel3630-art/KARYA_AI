import threading
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.auth.refresh import get_session_from_refresh_token
from app.auth.token_hash import hash_refresh_token
from app.auth.tokens import create_refresh_token
from app.core.database import Base
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


def test_refresh_row_lock_serializes_concurrent_requests():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    setup_db = SessionLocal()

    try:
        user = User(
            email="concurrency@example.com",
            password_hash="test-password-hash",
        )

        setup_db.add(user)
        setup_db.flush()

        refresh_token, jti, token_family, expires_at = (
            create_refresh_token(user.id)
        )

        session = SessionModel(
            user_id=user.id,
            refresh_token_hash=hash_refresh_token(
                refresh_token
            ),
            jti=jti,
            token_family=token_family,
            expires_at=expires_at,
            revoked=False,
        )

        setup_db.add(session)
        setup_db.commit()

        session_id = session.id
        user_id = user.id

    finally:
        setup_db.close()

    first_lock_acquired = threading.Event()
    release_first_transaction = threading.Event()

    results = []

    def worker_1():
        db = SessionLocal()

        try:
            locked_session = get_session_from_refresh_token(
                db=db,
                refresh_token=refresh_token,
            )

            assert locked_session.id == session_id

            first_lock_acquired.set()

            # Keep the transaction open.
            release_first_transaction.wait(timeout=5)

            locked_session.revoked = True
            locked_session.revoked_at = datetime.now(
                timezone.utc
            )

            db.commit()

            results.append(
                ("first", "success")
            )

        except Exception as exc:
            db.rollback()

            results.append(
                (
                    "first",
                    "error",
                    type(exc).__name__,
                    str(exc),
                )
            )

        finally:
            db.close()

    def worker_2():
        db = SessionLocal()

        try:
            # Do not start until worker 1 definitely owns the lock.
            first_lock_acquired.wait(timeout=5)

            try:
                locked_session = (
                    get_session_from_refresh_token(
                        db=db,
                        refresh_token=refresh_token,
                    )
                )

                results.append(
                    (
                        "second",
                        "success",
                        locked_session.id,
                    )
                )

            except HTTPException as exc:
                results.append(
                    (
                        "second",
                        "http_error",
                        exc.status_code,
                        exc.detail,
                    )
                )

        except Exception as exc:
            results.append(
                (
                    "second",
                    "error",
                    type(exc).__name__,
                    str(exc),
                )
            )

        finally:
            db.rollback()
            db.close()

    thread_1 = threading.Thread(target=worker_1)
    thread_2 = threading.Thread(target=worker_2)

    thread_1.start()
    thread_2.start()

    # Make sure worker 1 acquired FOR UPDATE before worker 2 runs.
    assert first_lock_acquired.wait(timeout=5)

    # Give worker 2 time to reach the blocking SELECT ... FOR UPDATE.
    threading.Event().wait(0.2)

    # Worker 1 now revokes the session and releases the lock.
    release_first_transaction.set()

    thread_1.join(timeout=5)
    thread_2.join(timeout=5)

    assert not thread_1.is_alive()
    assert not thread_2.is_alive()

    first_results = [
        result
        for result in results
        if result[0] == "first"
    ]

    second_results = [
        result
        for result in results
        if result[0] == "second"
    ]

    assert first_results == [
        ("first", "success")
    ]

    assert len(second_results) == 1

    second_result = second_results[0]

    assert second_result[0] == "second"
    assert second_result[1] == "http_error"
    assert second_result[2] == 401
    assert second_result[3] == "Refresh token reuse detected"

    verify_db = SessionLocal()

    try:
        final_session = verify_db.get(
            SessionModel,
            session_id,
        )

        assert final_session is not None
        assert final_session.user_id == user_id
        assert final_session.revoked is True

    finally:
        verify_db.close()
        Base.metadata.drop_all(bind=engine)