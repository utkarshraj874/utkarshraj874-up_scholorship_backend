import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Annotated, Any, TypedDict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user, get_db
from backend.app.models.chat import ChatConversation, ChatMessage
from backend.app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Scholarship Assistant"])
MAX_MESSAGE_LENGTH = 4000
HISTORY_LIMIT = 20


class CreateConversationRequest(BaseModel):
    title: str = Field(default="New conversation", min_length=1, max_length=120)


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=MAX_MESSAGE_LENGTH)


def _conversation_for_user(db: Session, conversation_id: int, user_id: int) -> ChatConversation:
    conversation = (
        db.query(ChatConversation)
        .filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == user_id,
        )
        .first()
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Chat conversation not found")
    return conversation


def _message_payload(message: ChatMessage) -> dict[str, Any]:
    return {
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
    }


@router.post("/conversations")
def create_conversation(
    req: CreateConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = ChatConversation(
        user_id=current_user.id,
        title=req.title.strip() or "New conversation",
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
    }


@router.get("/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == current_user.id)
        .order_by(ChatConversation.updated_at.desc())
        .all()
    )
    return [
        {
            "id": item.id,
            "title": item.title,
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
        }
        for item in conversations
    ]


@router.get("/conversations/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = _conversation_for_user(db, conversation_id, current_user.id)
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "messages": [_message_payload(message) for message in messages],
    }


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    conversation = _conversation_for_user(db, conversation_id, current_user.id)
    db.delete(conversation)
    db.commit()
    return {"detail": "Conversation deleted"}


@router.post("/conversations/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: int,
    req: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="The scholarship assistant is not configured yet.",
        )

    content = req.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Message cannot be empty")

    conversation = _conversation_for_user(db, conversation_id, current_user.id)
    prior_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    prior_messages.reverse()
    user_message = ChatMessage(
        conversation_id=conversation.id,
        role="user",
        content=content,
    )
    db.add(user_message)
    if not prior_messages:
        conversation.title = content[:80]
    conversation.updated_at = datetime.utcnow()
    db.commit()

    try:
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
        from langchain_groq import ChatGroq
        from langgraph.graph import END, START, StateGraph
        from langgraph.graph.message import add_messages
    except ImportError as exc:
        logger.exception("Chatbot dependencies are not installed")
        raise HTTPException(
            status_code=503,
            detail="The scholarship assistant is temporarily unavailable.",
        ) from exc

    class GraphState(TypedDict):
        messages: Annotated[list[Any], add_messages]

    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    model = ChatGroq(model=model_name, api_key=api_key, temperature=0.2)
    prompt_messages: list[Any] = [
        SystemMessage(
            content=(
                "You are a helpful assistant for students using the IIIT Ranchi UP "
                "Scholarship facilitation portal. Give clear, concise guidance about "
                "organizing application information and documents. Do not claim to "
                "submit official applications, verify government records, or provide "
                "legal/financial guarantees. Encourage users to verify deadlines and "
                "official requirements on scholarship.up.gov.in. Do not ask users to "
                "share passwords, OTPs, full Aadhaar numbers, or other sensitive IDs."
            )
        )
    ]
    for message in prior_messages:
        if message.role == "user":
            prompt_messages.append(HumanMessage(content=message.content))
        elif message.role == "assistant":
            prompt_messages.append(AIMessage(content=message.content))
    prompt_messages.append(HumanMessage(content=content))

    token_queue: asyncio.Queue[tuple[str, str] | None] = asyncio.Queue()

    async def assistant_node(state: GraphState) -> dict[str, list[Any]]:
        response_parts: list[str] = []
        async for chunk in model.astream(state["messages"]):
            chunk_content = chunk.content
            if isinstance(chunk_content, str):
                text = chunk_content
            elif isinstance(chunk_content, list):
                text = "".join(
                    block.get("text", "")
                    for block in chunk_content
                    if isinstance(block, dict) and isinstance(block.get("text"), str)
                )
            else:
                text = ""
            if text:
                response_parts.append(text)
                await token_queue.put(("token", text))
        return {"messages": [AIMessage(content="".join(response_parts))]}

    graph_builder = StateGraph(GraphState)
    graph_builder.add_node("assistant", assistant_node)
    graph_builder.add_edge(START, "assistant")
    graph_builder.add_edge("assistant", END)
    graph = graph_builder.compile()

    async def produce_response() -> None:
        try:
            await graph.ainvoke({"messages": prompt_messages})
        except Exception:
            logger.exception("Scholarship assistant request failed")
            await token_queue.put(
                ("error", "The assistant could not complete this response. Please try again.")
            )
        finally:
            await token_queue.put(None)

    async def event_stream():
        response_parts: list[str] = []
        producer = asyncio.create_task(produce_response())
        try:
            while True:
                item = await token_queue.get()
                if item is None:
                    break
                kind, value = item
                if kind == "error":
                    yield f"event: error\ndata: {json.dumps({'error': value})}\n\n"
                    continue
                response_parts.append(value)
                yield f"data: {json.dumps({'token': value}, ensure_ascii=False)}\n\n"

            response_text = "".join(response_parts)
            if response_text:
                db.add(
                    ChatMessage(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=response_text,
                    )
                )
                conversation.updated_at = datetime.utcnow()
                db.commit()
            yield f"event: done\ndata: {json.dumps({'conversation_id': conversation.id})}\n\n"
        finally:
            if not producer.done():
                producer.cancel()
            await asyncio.gather(producer, return_exceptions=True)
            db.close()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
