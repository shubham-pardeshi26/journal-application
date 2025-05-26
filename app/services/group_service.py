# app/services/group_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid # For generating group codes if needed, though you have group_code as a model field
from typing import List, Optional

from app.db.models.group import Group, GroupMember
from app.db.models.user import User
from app.schemas.group import GroupCreate, GroupUpdate # Ensure these are imported correctly
from app.schemas.user import UserResponseMinimal # To return minimal user data for members if needed

# Helper functions for permission checks
async def is_group_owner(db: Session, group_id: str, user_id: str) -> bool:
    """Checks if a user is the owner of a given group."""
    group = db.query(Group).filter(Group.id == group_id, Group.created_by_user_id == user_id).first()
    return group is not None

async def is_group_admin(db: Session, group_id: str, user_id: str) -> bool:
    """Checks if a user is an admin of a given group."""
    # An owner is implicitly an admin
    if await is_group_owner(db, group_id, user_id):
        return True
    
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id,
        GroupMember.is_admin == True
    ).first()
    return member is not None

async def is_group_member(db: Session, group_id: str, user_id: str) -> bool:
    """Checks if a user is a member of a given group (admin or regular member)."""
    member = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id
    ).first()
    return member is not None

# Core Group CRUD Operations

async def create_group(db: Session, group_in: GroupCreate, owner_id: str) -> Group:
    """Creates a new group and sets the creator as its owner and initial member/admin."""
    # Check for unique group name (optional, but good practice)
    existing_group_by_name = db.query(Group).filter(Group.name == group_in.name).first()
    if existing_group_by_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group with this name already exists.")

    # You have 'group_code' in your model. Ensure it's unique if user provides or generate one.
    # For simplicity, let's assume `group_code` is auto-generated and unique
    # OR that group_in.group_code is provided and we ensure uniqueness here.
    # For now, let's assume `group_in.group_code` must be unique if provided, otherwise generate a simple one.
    if group_in.group_code:
        existing_group_by_code = db.query(Group).filter(Group.group_code == group_in.group_code).first()
        if existing_group_by_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group code already in use.")
    else:
        # Generate a simple unique code (e.g., first 8 chars of a UUID)
        group_in.group_code = str(uuid.uuid4())[:8].upper()
        # Basic check to ensure it's truly unique in the DB (though collisions are low)
        while db.query(Group).filter(Group.group_code == group_in.group_code).first():
            group_in.group_code = str(uuid.uuid4())[:8].upper()


    db_group = Group(
        name=group_in.name,
        description=group_in.description,
        group_code=group_in.group_code, # Use the provided or generated code
        max_members=group_in.max_members,
        created_by_user_id=owner_id
    )
    db.add(db_group)
    db.flush() # Flush to get db_group.id before committing

    # Add the creator as the first member and admin of the group
    db_group_member = GroupMember(
        group_id=db_group.id,
        user_id=owner_id,
        is_admin=True # Creator is an admin
    )
    db.add(db_group_member)

    db.commit()
    db.refresh(db_group)
    return db_group

async def get_group_by_id(db: Session, group_id: str) -> Optional[Group]:
    """Retrieves a group by its ID."""
    return db.query(Group).filter(Group.id == group_id).first()

async def get_user_groups(db: Session, user_id: str) -> List[Group]:
    """Retrieves all groups that a user owns or is a member of."""
    # Get groups where the user is the creator
    owned_groups = db.query(Group).filter(Group.created_by_user_id == user_id).all()
    
    # Get groups where the user is a member
    member_of_groups_ids = [
        gm.group_id for gm in db.query(GroupMember).filter(GroupMember.user_id == user_id).all()
    ]
    member_of_groups = db.query(Group).filter(Group.id.in_(member_of_groups_ids)).all()

    # Combine and ensure uniqueness (using set for IDs is efficient)
    all_groups_map = {group.id: group for group in owned_groups + member_of_groups}
    return list(all_groups_map.values())


async def update_group(db: Session, group_id: str, group_update: GroupUpdate, current_user_id: str) -> Group:
    """Updates a group's details (owner-only)."""
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")
    
    if not await is_group_owner(db, group_id, current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this group.")
    
    update_data = group_update.model_dump(exclude_unset=True)

    # Handle unique fields if updated
    if 'name' in update_data and update_data['name'] != group.name:
        existing_group = db.query(Group).filter(Group.name == update_data['name']).first()
        if existing_group and existing_group.id != group_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group name already taken.")
            
    if 'group_code' in update_data and update_data['group_code'] != group.group_code:
        existing_group = db.query(Group).filter(Group.group_code == update_data['group_code']).first()
        if existing_group and existing_group.id != group_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group code already in use.")

    for key, value in update_data.items():
        setattr(group, key, value)
    
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

async def delete_group(db: Session, group_id: str, current_user_id: str):
    """Deletes a group (owner-only). Cascades to group members and associated journals/comments/media."""
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")
    
    if not await is_group_owner(db, group_id, current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the owner of this group.")
    
    # Due to cascade="all, delete-orphan" in Group model relationships,
    # deleting the group should automatically delete its members and journals.
    db.delete(group)
    db.commit()
    return {"message": "Group deleted successfully."}

# Group Membership Operations

async def get_group_members(db: Session, group_id: str, current_user_id: str) -> List[UserResponseMinimal]:
    """
    Retrieves all members of a group.
    Requires the current user to be a member of the group.
    """
    if not await is_group_member(db, group_id, current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not a member of this group.")

    group_members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    member_user_ids = [gm.user_id for gm in group_members]
    
    # Fetch user details for each member
    members_data = db.query(User).filter(User.id.in_(member_user_ids)).all()
    
    # Map to UserResponseMinimal for cleaner output
    return [UserResponseMinimal.model_validate(user) for user in members_data]


async def add_group_member(db: Session, group_id: str, user_id_to_add: str, current_user_id: str) -> GroupMember:
    """
    Adds a user as a member to a group.
    Only group admins or owners can add members.
    """
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")

    if not await is_group_admin(db, group_id, current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to add members to this group.")
    
    user_to_add = db.query(User).filter(User.id == user_id_to_add).first()
    if not user_to_add:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to add not found.")
    
    if await is_group_member(db, group_id, user_id_to_add):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member of this group.")
    
    # Check max members limit
    current_member_count = db.query(GroupMember).filter(GroupMember.group_id == group_id).count()
    if current_member_count >= group.max_members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Group has reached its maximum member limit of {group.max_members}.")


    db_group_member = GroupMember(
        group_id=group_id,
        user_id=user_id_to_add,
        is_admin=False # Added as regular member by default
    )
    db.add(db_group_member)
    db.commit()
    db.refresh(db_group_member)
    return db_group_member

async def remove_group_member(db: Session, group_id: str, user_id_to_remove: str, current_user_id: str):
    """
    Removes a user from a group.
    Only group admins/owners can remove members. A user can also remove themselves (leave group).
    Group owner cannot remove themselves (must delete group if they are the only member).
    """
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")
    
    member_to_remove = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id_to_remove
    ).first()

    if not member_to_remove:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not a member of this group.")

    # Check permissions
    if user_id_to_remove == current_user_id:
        # User is trying to remove themselves (leave the group)
        if await is_group_owner(db, group_id, current_user_id):
            # Owner can't leave unless they delete the group (or transfer ownership)
            # For simplicity, prevent owner from leaving directly without deleting.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Group owner cannot leave the group directly. Please delete the group if it's no longer needed.")
        # Regular member can leave
        db.delete(member_to_remove)
        db.commit()
        return {"message": "You have left the group successfully."}
    else:
        # Current user is trying to remove another user
        if not await is_group_admin(db, group_id, current_user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to remove members from this group.")
        
        # Prevent admin from removing the owner
        if user_id_to_remove == group.created_by_user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot remove the group owner.")

        # Admin can remove another member
        db.delete(member_to_remove)
        db.commit()
        return {"message": "Member removed successfully."}

async def update_member_role(db: Session, group_id: str, user_id_to_modify: str, is_admin: bool, current_user_id: str) -> GroupMember:
    """
    Updates a member's role (e.g., set as admin or demote).
    Only group owner can modify roles. Owner cannot change their own admin status.
    """
    group = await get_group_by_id(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found.")

    if not await is_group_owner(db, group_id, current_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the group owner can modify member roles.")
    
    member_to_modify = db.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user_id_to_modify
    ).first()

    if not member_to_modify:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not a member of this group.")

    if user_id_to_modify == current_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot change your own admin status.")
    
    member_to_modify.is_admin = is_admin
    db.add(member_to_modify)
    db.commit()
    db.refresh(member_to_modify)
    return member_to_modify