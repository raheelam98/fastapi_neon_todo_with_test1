from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi_neon2.model import Todo, create_db_and_tables , engine, get_session
from sqlmodel import  Session, select
from typing import Annotated
from contextlib import asynccontextmanager

#@asynccontextmanager
async def life_span(app: FastAPI):
    print("Crate table.... ")
    create_db_and_tables()
    yield

app = FastAPI(lifespan=life_span, title="Fast API")

@app.get('/')
def get_root_route():
    return {"Fast API": "Todo"}

# get todo from database
def get_db_todo():
    with Session(engine) as session:
        get_todos = select(Todo)
        todo_list = session.exec(get_todos).all()
        if not todo_list:
            return "Todo Not Found"
        else:
            return todo_list
        
@app.get('/get_todos', response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
    todo_list = get_db_todo()
    if not todo_list:
        raise HTTPException(status_code=404, detail="Todo Not Found ...")
    else:
        return todo_list

# insert data into Todo
def create_db_todo(todo : str):
    with Session(engine) as session:
        select_todo = Todo(todo_name=todo)
        session.add(select_todo)
        session.commit()
        session.refresh(select_todo)
        return select_todo
    
@app.post('/add_todo', response_model=Todo) 
def add_todo_route(user_todo : Annotated[str, Body()], session: Annotated[Session,Depends(get_session) ]):
    if not user_todo:
        raise HTTPException(status_code=404, detail="Todo Not Found...")
    else:
        added_todo = create_db_todo(user_todo)
        return added_todo
    
def update_db_todo(user_id:int, user_todo:str, session):
    selected_todo = select(Todo).where(Todo.id == user_id)
    update_todo = session.exec(selected_todo).first()
    update_todo.todo_name = user_todo
    if not update_todo:
        raise HTTPException(status_code=404, detail="Todo Not Found")
    else:
        session.add(update_todo)
        session.commit()
        session.refresh(update_todo)
        return update_todo 
    
@app.put('/update', response_model=Todo)   
def update_todo_route(todo_id: int, todo_name: Annotated[str, Body()], session: Annotated[Session, Depends(get_session)] ):
    updated_todo = update_db_todo(todo_id, todo_name, session)
    if not updated_todo:
        raise f"Todo user_id: {todo_id} not found...."
    return updated_todo    
            
def delete_from_table(user_id : int):  
   with Session(engine) as session:
     statment = select(Todo).where(Todo.id == user_id) 
     result = session.exec(statment).first()
     session.delete(result)
     session.commit()
     return result

@app.delete('/delete_todo/{todo_id}/')
def delete_route(todo_id : int, session : Annotated[Session, Depends(get_session)] ):
    delete_todo  = delete_from_table(todo_id) 
    if not delete_todo:
        raise HTTPException(status_code=404, detail='Todo not found ....' )
    else:
        return {"message" : 'Data Delete Sucessfully ' }
    
#### ==================== testing code ==================== #####  



@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo
