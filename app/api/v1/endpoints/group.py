# app/api/endpoints/group.py

from fastapi import APIRouter, Depends, HTTPException, status, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.db.models.group import Group, GroupMember
from app.db.models.user import User # To type-hint current_user
from app.dependencies import get_current_active_user
from app.schemas.group import (
    GroupCreate, GroupMemberAdd, GroupUpdate, GroupResponse,
    GroupMemberResponse, GroupJoin
)
from app.schemas.user import UserResponseMinimal # For listing members
from app.services import group_service # Import your group service

router = APIRouter()

# --- Group CRUD Operations ---

@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_new_group(
    group_in: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new group. The current authenticated user becomes the owner.
    """
    try:
        group = await group_service.create_group(db, group_in, current_user.id)
        return group
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create group: {e}")

@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve details of a specific group.
    Requires the user to be a member of the group.
    """
    group = await group_service.get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")

    if not await group_service.is_group_member(db, group_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this group.")

    return group

@router.get("/", response_model=List[GroupResponse])
async def get_all_user_groups(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve all groups the current user owns or is a member of.
    """
    groups = await group_service.get_user_groups(db, current_user.id)
    return groups

@router.put("/{group_id}", response_model=GroupResponse)
async def update_existing_group(
    group_update: GroupUpdate,
    group_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update details of a group. Only the group owner can perform this action.
    """
    try:
        group = await group_service.update_group(db, group_id, group_update, current_user.id)
        return group
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update group: {e}")

@router.delete("/{group_id}", status_code=status.HTTP_200_OK)
async def delete_group(
    group_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a group. Only the group owner can perform this action.
    This will also delete all associated group members and journals (due to cascade).
    """
    try:
        result = await group_service.delete_group(db, group_id, current_user.id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete group: {e}")

# --- Group Membership Operations ---

@router.get("/{group_id}/members", response_model=List[UserResponseMinimal])
async def get_members_of_group(
    group_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a list of all members in a specific group.
    Requires the current user to be a member of the group.
    """
    try:
        members = await group_service.get_group_members(db, group_id, current_user.id)
        return members
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch group members: {e}")


@router.post("/{group_id}/members", response_model=GroupMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member_to_group(
    member_data: GroupMemberAdd, # Accepts user_id to add
    group_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a user as a member to a group.
    Only group admins or the group owner can add members.
    """
    try:
        group_member = await group_service.add_group_member(db, group_id, member_data.user_id, current_user.id)
        # Manually attach user data for response, as it's not eager loaded in service by default
        user_in_db = db.query(User).filter(User.id == group_member.user_id).first()
        if user_in_db:
            response_data = GroupMemberResponse.model_validate(group_member) # Create dict from model_dump
            response_data.user = UserResponseMinimal.model_validate(user_in_db)
            return response_data
        return GroupMemberResponse.model_validate(group_member) # Fallback if user not found (shouldn't happen)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add group member: {e}")

@router.delete("/{group_id}/members/{user_id_to_remove}", status_code=status.HTTP_200_OK)
async def remove_member_from_group(
    group_id: str = Path(..., min_length=36, max_length=36),
    user_id_to_remove: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove a user from a group.
    Group admins/owners can remove other members. A user can also remove themselves (leave group).
    Group owner cannot remove themselves (must delete group).
    """
    try:
        result = await group_service.remove_group_member(db, group_id, user_id_to_remove, current_user.id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to remove group member: {e}")

@router.put("/{group_id}/members/{user_id_to_modify}/role", response_model=GroupMemberResponse)
async def update_member_role_in_group(
    group_id: str = Path(..., min_length=36, max_length=36),
    user_id_to_modify: str = Path(..., min_length=36, max_length=36),
    is_admin: bool = Body(..., embed=True), # Expects JSON body like {"is_admin": true}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a member's role (e.g., set as admin or demote).
    Only the group owner can modify roles. The owner cannot change their own admin status.
    """
    try:
        group_member = await group_service.update_member_role(db, group_id, user_id_to_modify, is_admin, current_user.id)
        # Manually attach user data for response if desired
        user_in_db = db.query(User).filter(User.id == group_member.user_id).first()
        if user_in_db:
            response_data = GroupMemberResponse.model_validate(group_member)
            response_data.user = UserResponseMinimal.model_validate(user_in_db)
            return response_data
        return GroupMemberResponse.model_validate(group_member)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update member role: {e}")

@router.post("/join", response_model=GroupMemberResponse, status_code=status.HTTP_201_CREATED)
async def join_group_by_code(
    group_join: GroupJoin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Allow a user to join a group using its unique group code.
    """
    group = db.query(Group).filter(Group.group_code == group_join.group_code).first()
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found with the provided code.")

    try:
        current_member_count = db.query(GroupMember).filter(GroupMember.group_id == group.id).count()
        if current_member_count >= group.max_members:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Group has reached its maximum member limit of {group.max_members}.")
        
        if await group_service.is_group_member(db, group.id, current_user.id):
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are already a member of this group.")
        
        
        db_group_member = GroupMember(
            group_id=group.id,
            user_id=current_user.id,
            is_admin=False
        )
        db.add(db_group_member)
        db.commit()
        db.refresh(db_group_member)

        user_in_db = db.query(User).filter(User.id == db_group_member.user_id).first()
        if user_in_db:
            response_data = GroupMemberResponse.model_validate(db_group_member)
            response_data.user = UserResponseMinimal.model_validate(user_in_db)
            return response_data
        return GroupMemberResponse.model_validate(db_group_member)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to join group: {e}")