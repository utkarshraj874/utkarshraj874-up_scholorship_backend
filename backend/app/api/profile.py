from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.profile import Profile
from backend.app.schema.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from backend.app.models.user import User
from backend.app.core.dependencies import get_db, get_current_user

router = APIRouter()

# ✅ Create or update profile (upsert)
@router.post("/profiles", response_model=ProfileResponse)
def create_profile(
    profile: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        existing_profile = db.query(Profile).filter(
            Profile.user_id == current_user.id
        ).first()

        profile_data = profile.model_dump() if hasattr(profile, "model_dump") else profile.dict()

        if existing_profile:
            for key, value in profile_data.items():
                setattr(existing_profile, key, value)
            db.commit()
            db.refresh(existing_profile)
            return existing_profile

        db_profile = Profile(**profile_data, user_id=current_user.id)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except Exception as e:
        db.rollback()
        print("❌ Error in create_profile:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ✅ Get current user's profile directly
@router.get("/profiles/me", response_model=ProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_profile = db.query(Profile).filter(
        Profile.user_id == current_user.id
    ).first()

    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile


# ✅ Update current user's profile directly
@router.put("/profiles/me", response_model=ProfileResponse)
def update_my_profile(
    profile: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_profile = db.query(Profile).filter(
            Profile.user_id == current_user.id
        ).first()

        if not db_profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile_data = profile.model_dump(exclude_unset=True) if hasattr(profile, "model_dump") else profile.dict(exclude_unset=True)
        for key, value in profile_data.items():
            setattr(db_profile, key, value)

        db.commit()
        db.refresh(db_profile)
        return db_profile
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("❌ Error in update_my_profile:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ✅ Get profile by ID (ownership check)
@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_profile = db.query(Profile).filter(
        Profile.id == profile_id,
        Profile.user_id == current_user.id
    ).first()

    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found or not authorized")
    return db_profile


# ✅ Update profile (ownership check)
@router.put("/profiles/{profile_id}", response_model=ProfileResponse)
def update_profile(
    profile_id: int,
    profile: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_profile = db.query(Profile).filter(
            Profile.id == profile_id,
            Profile.user_id == current_user.id
        ).first()

        if not db_profile:
            raise HTTPException(status_code=404, detail="Profile not found or not authorized")

        for key, value in profile.dict(exclude_unset=True).items():
            setattr(db_profile, key, value)

        db.commit()
        db.refresh(db_profile)
        return db_profile
    except Exception as e:
        print("❌ Error in update_profile:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ✅ Delete profile (ownership check)
@router.delete("/profiles/{profile_id}")
def delete_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_profile = db.query(Profile).filter(
            Profile.id == profile_id,
            Profile.user_id == current_user.id
        ).first()

        if not db_profile:
            raise HTTPException(status_code=404, detail="Profile not found or not authorized")

        db.delete(db_profile)
        db.commit()
        return {"message": "Profile deleted successfully"}
    except Exception as e:
        print("❌ Error in delete_profile:", str(e))
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
