from typing import Optional, List
from fastapi import APIRouter, Depends, status, Response
from psycopg2 import IntegrityError
from db import fetch_all, fetch_one, execute_returning, execute_with_row_count
from helpers import (
    get_db,
    raise_if_not_found,
    handle_error,
    get_current_user,
)
from schemas import (
    AgentCreate,
    AgentUpdate,
    AgentCreateOut,
    AgentUpdateOut,
    AgentDetailOut,
    AgentsOut,
    AgentNameOut,
    User,
)


router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)

#########################################
#               GET                     #
#########################################


@router.get("/", response_model=AgentsOut)
def list_agents(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT a.id,
               u.first_name,
               u.last_name,
               u.email,
               u.phone,
               a.title,
               a.license_number,
               ag.name AS agency
        FROM agents a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN agent_agencies aa ON a.id = aa.agent_id
        LEFT JOIN agencies ag ON aa.agency_id = ag.id
        ORDER BY a.id
    """

    parameters: List = []

    if limit is not None:
        query += " LIMIT %s"
        parameters.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        parameters.append(offset)

    rows = fetch_all(connection, query, parameters)
    return {"count": len(rows), "items": rows}


@router.get("/{agent_id}", response_model=AgentDetailOut)
def agent_detail(agent_id: int, connection=Depends(get_db)):
    query = """
        SELECT a.id,
               u.first_name,
               u.last_name,
               u.email,
               u.phone,
               a.title,
               a.license_number,
               a.bio,
               ag.name AS agency
        FROM agents a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN agent_agencies aa ON a.id = aa.agent_id
        LEFT JOIN agencies ag ON aa.agency_id = ag.id
        WHERE a.id = %s
    """
    row = fetch_one(connection, query, (agent_id,))
    return raise_if_not_found(row, "Agent")


#########################################
#                POST                   #
#########################################


@router.post(
    "/{agency_id}", status_code=status.HTTP_201_CREATED, response_model=AgentCreateOut
)
def create_agent(
    payload: AgentCreate,
    connection=Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = """
        INSERT INTO agents (user_id, title, license_number, bio, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING id, user_id, title, license_number, bio, created_at
    """
    try:
        row = execute_returning(
            connection,
            query,
            (payload.user_id, payload.title, payload.license_number, payload.bio),
        )

        if row is not None and payload.agency_id is not None:
            execute_with_row_count(
                connection,
                """agent_id: int,
                    INSERT INTO agent_agencies (agency_id, agent_id)
                    VALUES (%s, %s)
                """,
                (
                    payload.agency_id,
                    row["id"],
                ),
            )

        return row
    except IntegrityError as exc:
        handle_error(exc, "Could not create agent")


#########################################
#               PUT                     #
#########################################


@router.put("/{agent_id}", response_model=AgentUpdateOut)
def update_agent(
    agent_id: int,
    payload: AgentUpdate,
    connection=Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = """
        UPDATE agents
        SET user_id = COALESCE(%s, user_id),
            title = COALESCE(%s, title),
            license_number = COALESCE(%s, license_number),
            bio = COALESCE(%s, bio),
            updated_at = NOW()
        WHERE id = %s
        RETURNING id, user_id, title, license_number, bio, created_at, updated_at
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.user_id,
                payload.title,
                payload.license_number,
                payload.bio,
                agent_id,
            ),
        )

        if row is not None and payload.agency_id is not None:
            execute_with_row_count(
                connection,
                """
                    UPDATE agent_agencies 
                    SET agency_id = %s 
                    WHERE agent_id = %s 
                """,
                (
                    payload.agency_id,
                    agent_id,
                ),
            )

        return raise_if_not_found(row, "Saved search")
    except IntegrityError as exc:
        handle_error(exc, "Could not update agent")


#########################################
#               DELETE                  #
#########################################


@router.delete(
    "/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["agents"],
)
def delete_agent(
    agent_id: int,
    connection=Depends(get_db),
    _: User = Depends(get_current_user),
):
    execute_returning(
        connection, "DELETE FROM agent_agencies WHERE agent_id = %s", (agent_id,)
    )

    deleted = execute_returning(
        connection,
        "DELETE FROM agents WHERE id = %s RETURNING id",
        (agent_id,),
    )
    raise_if_not_found(deleted, "Agent")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


#########################################
#               PATCH                   #
#########################################


@router.patch("/{agents_id}/change/name", response_model=AgentNameOut)
def update_agent_name(
    agent_id: int,
    first_name: str,
    last_name: str,
    _: User = Depends(get_current_user),
    connection=Depends(get_db),
):
    agent_query = """
        UPDATE users
        SET first_name = %s,
            last_name = %s,
            updated_at = NOW()
        WHERE id = (
            SELECT user_id 
            FROM agents 
            WHERE id = %s
        )
        RETURNING title
    """
    patched = execute_returning(
        connection,
        agent_query,
        (
            first_name,
            last_name,
            agent_id,
        ),
    )

    return raise_if_not_found(patched, "Agent name")
