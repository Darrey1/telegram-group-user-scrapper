from fastapi import APIRouter, Depends, HTTPException,Response,Query
from sqlmodel import select
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.table import Books
from typing import List,Optional,Union
from http import HTTPStatus

api_router = APIRouter(
    prefix="/books",
    tags=["books"]
)


@api_router.get("/", response_model=List[Books])
async def get_books(session: AsyncSession = Depends(get_session))->Books:
    query = select(Books)
    result = await session.exec(query)
    return result.fetchall()



@api_router.post("/", response_model=Books)
async def create_book(book: Books, session: AsyncSession = Depends(get_session)):
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book



@api_router.put("/{book_id}", response_model=Books)
async def update_book(book_id: str, book_update: Books, session: AsyncSession = Depends(get_session)):
    db_book = await session.get(Books, book_id)
    if not db_book:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND.value, detail="Book not found")
    book_data = book_update.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(db_book, key, value)
    session.add(db_book)
    await session.commit()
    await session.refresh(db_book)
    return db_book




@api_router.get("/search",response_model=List[Books])
async def search(title:Optional[str]=Query(default=None),
                 author_name:Optional[str]=Query(default=None,alias="author"),
                 session: AsyncSession = Depends(get_session)
                 ):
    
    if title and author_name:
        query=select(Books).where(Books.title == title,Books.author == author_name)
        
    elif title:
        query=select(Books).where(Books.title == title)
        
    elif author_name:
        query=select(Books).where(Books.author == author_name)
        
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND.value, detail="You must provide either a title or an author name.")
    
    result = await session.exec(query)
    books = result.fetchall()
    
    if not books:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND.value, detail="No books found matching the criteria.")
    return books

        




@api_router.delete("/{book_id}", response_model=Books)
async def delete_book(book_id: str, session: AsyncSession = Depends(get_session)):
    db_book = await session.get(Books, book_id)
    if not db_book:
        raise HTTPException(status_code=HTTPStatus.NO_CONTENT.value, detail="Book not found")
    await session.delete(db_book)
    await session.commit()
    return db_book
