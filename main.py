from fastapi import FastAPI
from database import get_db_connection
from pydantic import BaseModel
from typing import List
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Employee API")


class Employee(BaseModel):
    Id: int
    Name: str
    Department: str
    Email: str


@app.get("/", tags=["Root"])  
def read_root():
    return {"message": "Welcome to the Employee API"}


@app.get("/employees", response_model=List[Employee])
def get_employees():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Id, Name, Department, Email FROM Employees")
    rows = cursor.fetchall()
    employees = []
    for row in rows:
        employees.append(Employee(Id=row[0], Name=row[1], Department=row[2], Email=row[3]))
    conn.close()
    return employees
 
@app.post("/run_query")
async def run_query(request: Request):
    data = await request.json()
    sql_query = data.get("query")
    if not sql_query:
        raise HTTPException(status_code=400, detail="No query provided")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        try:
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
        except:
            results = {"message": "Query executed (no results to fetch)"}
        conn.commit()
        conn.close()
        return JSONResponse(content={"results": results})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
 