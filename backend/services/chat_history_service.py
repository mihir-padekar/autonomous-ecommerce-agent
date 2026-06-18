from backend.database.db import SessionLocal

from backend.database.models import ChatHistory


def save_message(
    session_id,
    role,
    message
):

    db = SessionLocal()

    try:

        chat = ChatHistory(

            session_id=session_id,

            role=role,

            message=message
        )

        db.add(chat)

        db.commit()

    finally:

        db.close()


def get_conversation_history(
    session_id,
    limit=10
):

    db = SessionLocal()

    try:

        messages = (

            db.query(ChatHistory)

            .filter(
                ChatHistory.session_id == session_id
            )

            .order_by(
                ChatHistory.created_at.desc()
            )

            .limit(limit)

            .all()
        )

        messages.reverse()

        return [

            {
                "role": m.role,
                "message": m.message
            }

            for m in messages
        ]

    finally:

        db.close()